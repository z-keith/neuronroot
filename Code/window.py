from PyQt5.QtWidgets import (QWidget, QToolTip,
    QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QPlainTextEdit)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import QCoreApplication, QSize, Qt, QRect, QTimer

from PIL import Image

from time import sleep

from threading import Thread

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
    cancel_btn = None
    ready_run_btn = None
    skip_btn = None

    # Stores the log output as a string
    log_string = ""

    def __init__(self, controller):
        self.controller = controller

        super().__init__()

        self.initUI()


    def initUI(self):

        QToolTip.setFont(QFont('SansSerif', 10))

        hbox = QHBoxLayout(self)

        self.initial_image_frame = QLabel(self)
        self.initial_image_frame.setFixedWidth(500)
        self.initial_image_frame.setFrameShape(1)
        self.initial_image_frame.setLineWidth(1)
        self.initial_image_frame.setAlignment(Qt.AlignCenter)
        self.initial_image_frame.setText("The initial image will appear here once it is loaded.")

        self.skeleton_image_frame = QLabel(self)
        self.skeleton_image_frame.setFixedWidth(500)
        self.skeleton_image_frame.setFrameShape(1)
        self.skeleton_image_frame.setLineWidth(1)
        self.skeleton_image_frame.setAlignment(Qt.AlignCenter)
        self.skeleton_image_frame.setText("The skeleton image will appear here and update as it is refined.")

        self.output_log_label = QPlainTextEdit(self)
        self.output_log_label.setFixedWidth(450)
        self.output_log_label.setFrameShape(1)
        self.output_log_label.setLineWidth(1)
        self.output_log_label.setReadOnly(True)

        self.add_blacklist_btn = QPushButton('Blacklist area', self)
        self.add_blacklist_btn.clicked.connect(self.onclick_run)
        self.add_blacklist_btn.setToolTip('Select an area to exclude from the search')

        self.clear_blacklist_btn = QPushButton('Clear blacklist', self)
        self.clear_blacklist_btn.clicked.connect(self.onclick_run)
        self.clear_blacklist_btn.setToolTip('Clear the blacklist')

        self.select_infile_btn = QPushButton('Input location...', self)
        self.select_infile_btn.clicked.connect(self.onclick_run)
        self.select_infile_btn.setToolTip('Select files to process')

        self.select_output_btn = QPushButton('Output location...', self)
        self.select_output_btn.clicked.connect(self.onclick_run)
        self.select_output_btn.setToolTip('Choose where to save output images and data')

        self.discard_redo_btn = QPushButton('Discard + redo', self)
        self.discard_redo_btn.clicked.connect(self.onclick_run)
        self.discard_redo_btn.setToolTip('Choose where to save output images and data')

        self.discard_next_btn = QPushButton('Discard + continue', self)
        self.discard_next_btn.clicked.connect(self.onclick_run)
        self.discard_next_btn.setToolTip('Choose where to save output images and data')

        self.accept_next_btn = QPushButton('Accept + continue', self)
        self.accept_next_btn.clicked.connect(self.onclick_run)
        self.accept_next_btn.setToolTip('Choose where to save output images and data')

        self.cancel_btn = QPushButton('Cancel', self)
        self.cancel_btn.clicked.connect(self.onclick_run)
        self.cancel_btn.setToolTip('Select a start point and analyze the current image')

        self.ready_run_btn = QPushButton('Ready', self)
        self.ready_run_btn.clicked.connect(self.onclick_run)
        self.ready_run_btn.setToolTip('Select a start point and analyze the current image')

        self.skip_btn = QPushButton('Skip', self)
        self.skip_btn.clicked.connect(self.onclick_run)
        self.skip_btn.setToolTip('Select a start point and analyze the current image')

        button_column = QVBoxLayout(self)
        button_column.addWidget(self.output_log_label)

        row1 = QHBoxLayout(self)
        row1.addWidget(self.add_blacklist_btn)
        row1.addWidget(self.clear_blacklist_btn)
        button_column.addLayout(row1)

        row2 = QHBoxLayout(self)
        row2.addWidget(self.select_infile_btn)
        row2.addWidget(self.select_output_btn)
        button_column.addLayout(row2)

        row3 = QHBoxLayout(self)
        row3.addWidget(self.discard_redo_btn)
        row3.addWidget(self.discard_next_btn)
        row3.addWidget(self.accept_next_btn)
        button_column.addLayout(row3)

        row4 = QHBoxLayout(self)
        row4.addWidget(self.cancel_btn)
        button_column.addLayout(row4)

        row5 = QHBoxLayout(self)
        row5.addWidget(self.skip_btn)
        row5.addWidget(self.ready_run_btn)
        button_column.addLayout(row5)

        hbox.addWidget(self.initial_image_frame)
        hbox.addWidget(self.skeleton_image_frame)
        hbox.addLayout(button_column)
        self.setLayout(hbox)

        self.set_buttons_initial()

        self.setFixedSize(1500, 800)
        self.setWindowTitle('Neuronroot 1.0')
        self.show()

    def update_UI_custom(self):
        self.output_log_label.setPlainText(self.log_string)
        self.output_log_label.repaint()

    def set_buttons_initial(self):
        self.discard_redo_btn.hide()
        self.discard_next_btn.hide()
        self.accept_next_btn.hide()

        self.cancel_btn.hide()

        self.skip_btn.show()
        self.ready_run_btn.show()

    def set_buttons_running(self):
        self.discard_redo_btn.hide()
        self.discard_next_btn.hide()
        self.accept_next_btn.hide()

        self.cancel_btn.show()

        self.skip_btn.hide()
        self.ready_run_btn.hide()

    def set_buttons_finished(self):
        self.discard_redo_btn.show()
        self.discard_next_btn.show()
        self.accept_next_btn.show()

        self.cancel_btn.hide()

        self.skip_btn.hide()
        self.ready_run_btn.hide()

    def SetLabelImage(self, label, imageFileName):

        pixmap = QPixmap(imageFileName)
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
        self.log_string = ""
        thread = Thread(target=self.analyze)
        thread.start()
        while thread.is_alive():
            self.update_UI_custom()
            sleep(1)
        self.update_UI_custom()

    def analyze(self):
        # load the image file into an ArrayBuilder
        thread = Thread(target=self.controller.load_image_to_array)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string

        # construct a graph and associated node_dict in a AreaBuilder
        thread = Thread(target=self.controller.build_areas)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string

        # print the initial representation of the output with a new Printer

        thread = Thread(target=self.controller.print_background)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string

        if config.test_radii:
            # reuse the Printer to print radius test images
            thread = Thread(target=self.controller.print_test_radii)
            thread.start()
            thread.join()

            self.log_string = self.controller.log_string

        # prune the initial representation down to a skeleton with a TreeBuilder
        thread = Thread(target=self.controller.build_trees)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string

        # reuse the Printer to print the skeleton representation of the output
        thread = Thread(target=self.controller.print_skeleton)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string

        # build root structures with a RootBuilder
        thread = Thread(target=self.controller.build_roots)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string

        # reuse the Printer to print a representation of the roots
        thread = Thread(target=self.controller.print_roots)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string

        # if the user selected it, search for nodules
        if config.search_for_nodules:
            thread = Thread(target=self.controller.find_nodules)
            thread.start()
            thread.join()

            self.log_string = self.controller.log_string

            # and print them
            thread = Thread(target=self.controller.print_nodules)
            thread.start()
            thread.join()

            self.log_string = self.controller.log_string

        # complete!
        thread = Thread(target=self.controller.print_final_data)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string