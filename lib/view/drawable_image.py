from PyQt5 import QtWidgets, QtCore, QtGui


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
            width = moved_x - self.clicked_x1
            height = moved_y - self.clicked_y1

            painter.fillRect(self.clicked_x1, self.clicked_y1, width, height, QtGui.QColor(0, 0, 0))
            self.update()

    def mouseReleaseEvent(self, loc):
        if self.blacklisting:
            self.clicked_x2 = loc.x()
            self.clicked_y2 = loc.y()
            self.blacklisting = False
            self.done_blacklisting.emit()

    def generate_blacklist_rectangle(self):
        scaled_y1 = self.clicked_y1 / self.pixmap().height()
        scaled_x1 = self.clicked_x1 / self.pixmap().width()
        scaled_y2 = self.clicked_y2 / self.pixmap().height()
        scaled_x2 = self.clicked_x2 / self.pixmap().width()

        term_x1 = min(scaled_x1, scaled_x2)
        term_x2 = max(scaled_x1, scaled_x2)
        term_y1 = min(scaled_y1, scaled_y2)
        term_y2 = max(scaled_y1, scaled_y2)

        return (term_y1, term_x1), (term_y2, term_x2)

    def generate_click_point(self):
        scaled_y1 = self.clicked_y1 / self.pixmap().height()
        scaled_x1 = self.clicked_x1 / self.pixmap().width()

        return scaled_y1, scaled_x1

    def draw_blacklisted(self, blacklist):
        painter = QtGui.QPainter()
        painter.begin(self.pixmap())
        painter.setBrush(QtGui.QBrush())
        painter.setOpacity(1)
        width = self.pixmap().width()
        height = self.pixmap().height()
        for zone in blacklist:
            zone_x = int(zone[0][1] * width)
            zone_y = int(zone[0][0] * height)
            zone_w = abs(int(zone[1][1] * width) - zone_x)
            zone_h = abs(int(zone[1][0] * height) - zone_y)
            painter.fillRect(zone_x, zone_y, zone_w, zone_h, QtGui.QColor(0, 0, 0))
        self.update()

    def reset(self):
        self.blacklisting = False
        self.starting = False

        self.clicked_x1 = 0
        self.clicked_y1 = 0
        self.clicked_x2 = 0
        self.clicked_y2 = 0
