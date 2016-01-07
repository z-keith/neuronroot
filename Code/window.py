from PyQt5.QtWidgets import (QWidget, QToolTip,
    QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import QCoreApplication, QSize, Qt, QRect

from PIL import Image

import config

class MainWindow(QWidget):

    # Stores the reference to the program logic
    controller = None

    # Stores references to UI elements
    initial_image_frame = None
    skeleton_image_frame = None
    output_log_label = None
    add_blacklist_btn = None
    clear_blacklist_btn = None
    select_infile_btn = None
    select_output_btn = None
    find_nodules_checkbox = None
    dpi_settext = None
    discard_redo_btn = None
    discard_next_btn = None
    accept_next_btn = None
    ready_run_btn = None

    def __init__(self, controller):
        self.controller = controller

        super().__init__()

        self.initUI()


    def initUI(self):

        QToolTip.setFont(QFont('SansSerif', 10))

        hbox = QHBoxLayout(self)

        self.initial_image_frame = QLabel(self)
        self.initial_image_frame.setFixedWidth(350)
        self.initial_image_frame.setFrameShape(1)
        self.initial_image_frame.setLineWidth(1)
        self.initial_image_frame.setAlignment(Qt.AlignCenter)
        self.initial_image_frame.setText("The initial image will appear here.")

        self.skeleton_image_frame = QLabel(self)
        self.skeleton_image_frame.setFixedWidth(350)
        self.skeleton_image_frame.setFrameShape(1)
        self.skeleton_image_frame.setLineWidth(1)
        self.skeleton_image_frame.setAlignment(Qt.AlignCenter)
        self.skeleton_image_frame.setText("The skeleton image will appear here.")

        btn = QPushButton('Run', self)
        btn.clicked.connect(self.onclick_run)
        btn.setToolTip('Analyze the current image')

        button_column = QVBoxLayout(self)
        button_column.addWidget(QLabel("hello"))
        button_column.addWidget(btn)

        hbox.addWidget(self.initial_image_frame)
        hbox.addWidget(self.skeleton_image_frame)
        hbox.addWidget(self.nodule_image_frame)
        hbox.addLayout(button_column)
        self.setLayout(hbox)

        self.setGeometry(50, 50, 1000, 600)
        self.setFixedSize(1000, 600)
        self.setWindowTitle('Neuronroot 1.0')
        self.show()

    def SetLabelImage(self, label, imageFileName):

        pixmap = QPixmap(imageFileName);
        if (pixmap.isNull()):
            return False

        w = min(pixmap.width(),  label.maximumWidth())
        h = min(pixmap.height(), label.maximumHeight())
        pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        return True

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