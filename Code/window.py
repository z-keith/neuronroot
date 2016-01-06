from PyQt5.QtWidgets import (QWidget, QToolTip,
    QPushButton, QLabel, QHBoxLayout)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import QCoreApplication
from PIL import Image

import config

class MainWindow(QWidget):

    # Stores the reference to the program logic
    controller = None

    def __init__(self, controller):
        self.controller = controller

        super().__init__()

        self.initUI()


    def initUI(self):

        QToolTip.setFont(QFont('SansSerif', 10))

        temp = Image.open("../TestImages/2014-06-24-Tri-293.tif")
        temp.save("../TestImages/2014-06-24-Tri-293.jpg")

        hbox = QHBoxLayout(self)
        pixmap = QPixmap("../TestImages/2014-06-24-Tri-293.jpg").scaledToHeight(580)

        lbl = QLabel(self)
        lbl.setPixmap(pixmap)

        btn = QPushButton('Run', self)
        btn.clicked.connect(self.onclick_run)
        btn.setToolTip('Analyze the current image')

        hbox.addWidget(lbl)
        hbox.addWidget(btn)
        self.setLayout(hbox)

        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle('Neuronroot 1.0')
        self.show()

    def set_controller(self, controller):
        self.controller = controller

    def onclick_run(self):
        # load the image file into an ArrayBuilder
        self.controller.load_image_to_array()

        # construct a graph and associated node_dict in a AreaBuilder
        self.controller.build_areas()

        # print the initial representation of the output with a new Printer
        self.controller.print_background()

        if config.test_radii:
            # reuse the Printer to print radius test images
            self.controller.print_test_radii()

        # prune the initial representation down to a skeleton with a TreeBuilder
        self.controller.build_trees()

        # reuse the Printer to print the skeleton representation of the output
        self.controller.print_skeleton()

        # build root structures with a RootBuilder
        self.controller.build_roots()

        # reuse the Printer to print a representation of the roots
        self.controller.print_roots()

        # if the user selected it, search for nodules
        if config.search_for_nodules:
            self.controller.find_nodules()

            # and print them
            self.controller.print_nodules()

        # complete!
        self.controller.print_final_data()