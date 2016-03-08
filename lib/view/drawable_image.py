from PyQt5 import QtWidgets, QtCore, QtGui

import config

class DrawableImage(QtWidgets.QLabel):

	blacklisting = False
	starting = False

	clicked_x1 = 0
	clicked_x2 = 0
	clicked_y1 = 0
	clicked_y2 = 0

	done_blacklisting = QtCore.pyqtSignal()
	done_starting = QtCore.pyqtSignal()
	
	def mousePressEvent(self, loc):
		if self.blacklisting:
			self.clicked_x1 = loc.x()
			self.clicked_y1 = loc.y()
		elif self.starting:
			self.clicked_x1 = loc.x()
			self.clicked_y1 = loc.y()
			self.starting = False
			self.done_starting.emit()

	def mouseMoveEvent(self, loc):
		if self.blacklisting:
			painter = QtGui.QPainter()
			painter.begin(self.pixmap())
			painter.setBrush(QtGui.QBrush())
			painter.setOpacity(1)

			moved_x = loc.x()
			moved_y = loc.y()
			width = moved_x-self.clicked_x1
			height = moved_y-self.clicked_y1

			painter.fillRect(self.clicked_x1, self.clicked_y1, width, height, QtGui.QColor(0,0,0))
			self.update()


	def mouseReleaseEvent(self, loc):
		if self.blacklisting:
			self.clicked_x2 = loc.x()
			self.clicked_y2 = loc.y()
			self.blacklisting = False
			self.done_blacklisting.emit()

	def drawBlacklisted(self):
		painter = QtGui.QPainter()
		painter.begin(self.pixmap())
		painter.setBrush(QtGui.QBrush())
		painter.setOpacity(1)
		width = self.pixmap().width()
		height = self.pixmap().height()
		for zone in config.area_blacklist:
			zonex = int(zone[0][1]*width)
			zoney = int(zone[0][0]*height)
			zonew = abs(int(zone[1][1]*width)-zonex)
			zoneh = abs(int(zone[1][0]*height)-zoney)
			painter.fillRect(zonex, zoney, zonew, zoneh, QtGui.QColor(0,0,0))
		self.update()