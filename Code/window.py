
from PyQt4 import QtGui, QtCore

from PIL import Image

from time import sleep

from threading import Thread

import config

class MainWindow(QtGui.QWidget):

    # Stores the reference to the program logic
    controller = None

    # Stores the list of files currently in use
    file_set = None
    file_idx = None

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

    # Stores the display image paths
    initial_image = None
    updated_image = None
    image_updated = False

    # Toggle to allow the cancel button to work
    cancel_clicked = True


    def __init__(self, controller):
        self.controller = controller

        super().__init__()

        self.initUI()

    def initUI(self):

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.setFixedSize(1100, 500)
        self.setWindowTitle('Neuronroot 1.0')

        hbox = QtGui.QHBoxLayout(self)

        self.initial_image_frame = QtGui.QLabel(self)
        self.initial_image_frame.setFixedWidth(350)
        self.initial_image_frame.setFrameShape(1)
        self.initial_image_frame.setLineWidth(1)
        self.initial_image_frame.setAlignment(QtCore.Qt.AlignCenter)
        self.initial_image_frame.setText("The initial image will appear here once it is loaded.")
        hbox.addWidget(self.initial_image_frame)

        self.skeleton_image_frame = QtGui.QLabel(self)
        self.skeleton_image_frame.setFixedWidth(350)
        self.skeleton_image_frame.setFrameShape(1)
        self.skeleton_image_frame.setLineWidth(1)
        self.skeleton_image_frame.setAlignment(QtCore.Qt.AlignCenter)
        self.skeleton_image_frame.setText("The skeleton image will appear here and update as it is refined.")
        hbox.addWidget(self.skeleton_image_frame)

        vbox = QtGui.QVBoxLayout(self)

        self.output_log_label = QtGui.QPlainTextEdit(self)
        self.output_log_label.setFixedWidth(300)
        self.output_log_label.setFrameShape(1)
        self.output_log_label.setLineWidth(1)
        self.output_log_label.setReadOnly(True)
        vbox.addWidget(self.output_log_label)

        row1 = QtGui.QHBoxLayout(self)
        row2 = QtGui.QHBoxLayout(self)
        row3 = QtGui.QHBoxLayout(self)
        row4 = QtGui.QHBoxLayout(self)

        self.add_blacklist_btn = QtGui.QPushButton('Blacklist area', self)
        self.add_blacklist_btn.clicked.connect(self.onclick_set_blacklist)
        self.add_blacklist_btn.setToolTip('Select an area to exclude from the search')
        row1.addWidget(self.add_blacklist_btn)

        self.clear_blacklist_btn = QtGui.QPushButton('Clear blacklist', self)
        self.clear_blacklist_btn.clicked.connect(self.onclick_clear_blacklist)
        self.clear_blacklist_btn.setToolTip('Clear the blacklist')
        row1.addWidget(self.clear_blacklist_btn)

        self.select_infile_btn = QtGui.QPushButton('Input location...', self)
        self.select_infile_btn.clicked.connect(self.onclick_input)
        self.select_infile_btn.setToolTip('Select files to process')
        row2.addWidget(self.select_infile_btn)

        self.select_output_btn = QtGui.QPushButton('Output location...', self)
        self.select_output_btn.clicked.connect(self.onclick_output)
        self.select_output_btn.setToolTip('Choose where to save output images and data')
        row2.addWidget(self.select_output_btn)

        self.discard_redo_btn = QtGui.QPushButton('Discard + redo', self)
        self.discard_redo_btn.clicked.connect(self.onclick_reject_redo)
        self.discard_redo_btn.setToolTip('Choose where to save output images and data')
        row3.addWidget(self.discard_redo_btn)

        self.discard_next_btn = QtGui.QPushButton('Discard + continue', self)
        self.discard_next_btn.clicked.connect(self.onclick_reject_skip)
        self.discard_next_btn.setToolTip('Choose where to save output images and data')
        row3.addWidget(self.discard_next_btn)

        self.accept_next_btn = QtGui.QPushButton('Accept + continue', self)
        self.accept_next_btn.clicked.connect(self.onclick_accept)
        self.accept_next_btn.setToolTip('Choose where to save output images and data')
        row3.addWidget(self.accept_next_btn)

        self.ready_run_btn = QtGui.QPushButton('Ready', self)
        self.ready_run_btn.clicked.connect(self.onclick_run)
        self.ready_run_btn.setToolTip('Select a start point and analyze the current image')
        row4.addWidget(self.ready_run_btn)

        self.skip_btn = QtGui.QPushButton('Skip', self)
        self.skip_btn.clicked.connect(self.onclick_skip)
        self.skip_btn.setToolTip('Select a start point and analyze the current image')
        row4.addWidget(self.skip_btn)

        self.cancel_btn = QtGui.QPushButton('Cancel', self)
        self.cancel_btn.clicked.connect(self.onclick_cancel)
        self.cancel_btn.setToolTip('Select a start point and analyze the current image')
        row4.addWidget(self.cancel_btn)

        vbox.addLayout(row1)
        vbox.addLayout(row2)
        vbox.addLayout(row3)
        vbox.addLayout(row4)

        hbox.addLayout(vbox)

        self.set_buttons_initial()

        self.show()

    def update_UI_custom(self):
        self.output_log_label.setPlainText(self.log_string)
        self.output_log_label.repaint()
        if self.image_updated:
            self.set_label_to_image(self.initial_image_frame, self.initial_image)
            self.set_label_to_image(self.skeleton_image_frame, self.updated_image)
            self.image_updated = False

    def set_buttons_initial(self):
        self.add_blacklist_btn.setDisabled(False)
        self.clear_blacklist_btn.setDisabled(False)
        self.select_infile_btn.setDisabled(False)
        self.select_output_btn.setDisabled(False)

        self.discard_redo_btn.setDisabled(True)
        self.discard_next_btn.setDisabled(True)
        self.accept_next_btn.setDisabled(True)

        self.cancel_btn.setDisabled(True)

        self.skip_btn.setDisabled(False)
        self.ready_run_btn.setDisabled(False)

        self.discard_redo_btn.repaint()
        self.discard_next_btn.repaint()
        self.accept_next_btn.repaint()
        self.cancel_btn.repaint()
        self.skip_btn.repaint()
        self.ready_run_btn.repaint()

    def set_buttons_running(self):
        self.add_blacklist_btn.setDisabled(True)
        self.clear_blacklist_btn.setDisabled(True)
        self.select_infile_btn.setDisabled(True)
        self.select_output_btn.setDisabled(True)

        self.discard_redo_btn.setDisabled(True)
        self.discard_next_btn.setDisabled(True)
        self.accept_next_btn.setDisabled(True)

        self.cancel_btn.setDisabled(False)

        self.skip_btn.setDisabled(True)
        self.ready_run_btn.setDisabled(True)

        self.discard_redo_btn.repaint()
        self.discard_next_btn.repaint()
        self.accept_next_btn.repaint()
        self.cancel_btn.repaint()
        self.skip_btn.repaint()
        self.ready_run_btn.repaint()

    def set_buttons_finished(self):
        self.add_blacklist_btn.setDisabled(True)
        self.clear_blacklist_btn.setDisabled(True)
        self.select_infile_btn.setDisabled(True)
        self.select_output_btn.setDisabled(True)

        self.discard_redo_btn.setDisabled(False)
        self.discard_next_btn.setDisabled(False)
        self.accept_next_btn.setDisabled(False)

        self.cancel_btn.setDisabled(True)

        self.skip_btn.setDisabled(True)
        self.ready_run_btn.setDisabled(True)

        self.discard_redo_btn.repaint()
        self.discard_next_btn.repaint()
        self.accept_next_btn.repaint()
        self.cancel_btn.repaint()
        self.skip_btn.repaint()
        self.ready_run_btn.repaint()

    def set_label_to_image(self, label, imagepath):

        pixmap = QtGui.QPixmap(imagepath)
        if (pixmap.isNull()):
            return False

        w = min(pixmap.width(),  label.maximumWidth())
        h = min(pixmap.height(), label.maximumHeight())
        pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        return True

    def set_controller(self, controller):
        self.controller = controller

    def onclick_input(self):
        # get list of files, store them in config, load first one as preview
        self.file_set = QtGui.QFileDialog.getOpenFileNames(self.select_infile_btn, "Select image files", "", "Images (*.png *.tif *.jpg *.bmp)")
        print(self.file_set)

    def onclick_output(self):
        # get output location, store it in config
        outfile_path = QtGui.QFileDialog.getExistingDirectory(self.select_output_btn, "Select output directory")
        # TODO: Link to config

    def onclick_set_blacklist(self):
        #TODO: how to do this?
        pass

    def onclick_clear_blacklist(self):
        config.area_blacklist = []

    def onclick_run(self):
        self.log_string = ""
        thread = Thread(target=self.analyze)
        thread.start()
        self.set_buttons_running()
        while thread.is_alive():
            if self.cancel_clicked:
                # TODO: implement cancellation (kill thread, reset to start position)
                pass
            self.update_UI_custom()
            sleep(1)
        self.set_buttons_finished()
        self.update_UI_custom()

    def onclick_skip(self):
        # go to next file, load as preview
        pass

    def onclick_cancel(self):
        self.cancel_clicked = True

    def onclick_accept(self):
        # go to next file, load as preview
        pass

    def onclick_reject_skip(self):
        # go to next file, load as preview
        pass

    def onclick_reject_redo(self):
        # clear temp data, set up for new run
        pass

    def analyze(self):
        # load the image file into an ArrayBuilder
        thread = Thread(target=self.controller.load_image_to_array)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string
        self.initial_image = config.outfile_path + config.file_name +"-initial" + config.proper_file_extension
        self.image_updated = True
        while self.image_updated:
            sleep(1)

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
        self.updated_image = config.outfile_path + config.file_name + "-analysis" + config.proper_file_extension
        self.image_updated = True
        while self.image_updated:
            sleep(1)

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
        self.image_updated = True
        while self.image_updated:
            sleep(1)

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
        self.image_updated = True

        while self.image_updated:
            sleep(1)

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
            self.image_updated = True
            while self.image_updated:
                sleep(1)

        # complete!
        thread = Thread(target=self.controller.print_final_data)
        thread.start()
        thread.join()

        self.log_string = self.controller.log_string