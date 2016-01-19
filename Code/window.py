import os

import time
from PyQt4 import QtGui, QtCore

from PIL import Image

from threading import Thread

import config
import controller

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

    # Signals
    buttons_init = QtCore.pyqtSignal()
    buttons_run = QtCore.pyqtSignal()
    buttons_end = QtCore.pyqtSignal()
    img_update = QtCore.pyqtSignal()
    write = QtCore.pyqtSignal()

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        controller.qt_window = self
        controller.ui_update.connect(self.update_UI)
        controller.image_update.connect(self.set_image_updated)
        controller.write_finished.connect(self.set_write_finished)
        self.write.connect(self.controller.write_output)

        self.initUI()

    def initUI(self):

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.setFixedSize(1100, 600)
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
        self.skeleton_image_frame.setText("The skeleton image will appear here, updating as it is refined.")
        self.img_update.connect(self.show_image_progress)
        hbox.addWidget(self.skeleton_image_frame)

        vbox = QtGui.QVBoxLayout(self)

        self.output_log_label = QtGui.QPlainTextEdit(self)
        self.output_log_label.setFixedWidth(350)
        self.output_log_label.setFrameShape(1)
        self.output_log_label.setLineWidth(1)
        self.output_log_label.setReadOnly(True)
        vbox.addWidget(self.output_log_label)

        row1 = QtGui.QHBoxLayout(self)
        row2 = QtGui.QHBoxLayout(self)
        row3 = QtGui.QHBoxLayout(self)
        row4 = QtGui.QHBoxLayout(self)

        self.add_blacklist_btn = QtGui.QPushButton('Blacklist area', self)
        self.add_blacklist_btn.setToolTip('Select an area to ignore')
        self.add_blacklist_btn.clicked.connect(self.onclick_set_blacklist)
        self.buttonsetup_group1(self.add_blacklist_btn)

        self.clear_blacklist_btn = QtGui.QPushButton('Clear blacklist', self)
        self.clear_blacklist_btn.setToolTip('Clear the blacklist')
        self.clear_blacklist_btn.clicked.connect(self.onclick_clear_blacklist)
        self.buttonsetup_group1(self.clear_blacklist_btn)

        row1.addWidget(self.add_blacklist_btn)
        row1.addWidget(self.clear_blacklist_btn)

        self.select_infile_btn = QtGui.QPushButton('Input location...', self)
        self.select_infile_btn.setToolTip('Select files to process')
        self.select_infile_btn.clicked.connect(self.onclick_input)
        self.buttonsetup_group1(self.select_infile_btn)

        self.select_output_btn = QtGui.QPushButton('Output location...', self)
        self.select_output_btn.setToolTip('Choose where to save output images and data')
        self.select_output_btn.clicked.connect(self.onclick_output)
        self.buttonsetup_group1(self.select_output_btn)

        row2.addWidget(self.select_infile_btn)
        row2.addWidget(self.select_output_btn)

        self.discard_redo_btn = QtGui.QPushButton('Discard + redo', self)
        self.discard_redo_btn.setToolTip('Retry analysis of the current image')
        self.discard_redo_btn.clicked.connect(self.onclick_reject_redo)
        self.buttonsetup_group3(self.discard_redo_btn)

        self.discard_next_btn = QtGui.QPushButton('Discard + continue', self)
        self.discard_next_btn.setToolTip('Continue without saving data')
        self.discard_next_btn.clicked.connect(self.onclick_reject_skip)
        self.buttonsetup_group3(self.discard_next_btn)

        self.accept_next_btn = QtGui.QPushButton('Accept + continue', self)
        self.accept_next_btn.setToolTip('Save data and continue')
        self.accept_next_btn.clicked.connect(self.onclick_accept)
        self.buttonsetup_group3(self.accept_next_btn)

        row3.addWidget(self.discard_redo_btn)
        row3.addWidget(self.discard_next_btn)
        row3.addWidget(self.accept_next_btn)

        self.ready_run_btn = QtGui.QPushButton('Ready', self)
        self.ready_run_btn.setToolTip('Select a start point and analyze the current image')
        self.ready_run_btn.clicked.connect(self.onclick_run)
        self.buttonsetup_group1(self.ready_run_btn)

        self.skip_btn = QtGui.QPushButton('Skip', self)
        self.skip_btn.setToolTip('Load the next image, ignoring the current one')
        self.skip_btn.clicked.connect(self.onclick_skip)
        self.buttonsetup_group1(self.skip_btn)

        self.cancel_btn = QtGui.QPushButton('Cancel', self)
        self.cancel_btn.setToolTip('Stop analysis and discard any progress on the current image')
        self.cancel_btn.clicked.connect(self.onclick_cancel)
        self.buttonsetup_group2(self.cancel_btn)

        row4.addWidget(self.ready_run_btn)
        row4.addWidget(self.skip_btn)
        row4.addWidget(self.cancel_btn)

        vbox.addLayout(row1)
        vbox.addLayout(row2)
        vbox.addLayout(row3)
        vbox.addLayout(row4)

        hbox.addLayout(vbox)

        self.set_buttons_initial()

        self.show()

    def set_image_updated(self):
        self.img_update.emit()

    def show_image_progress(self):
        self.set_label_to_image(self.skeleton_image_frame, self.updated_image)

    def update_image_paths(self):
        self.initial_image = config.outfile_path + "/" + config.file_name +"-initial" + config.proper_file_extension
        self.updated_image = config.outfile_path + "/" + config.file_name + "-analysis" + config.proper_file_extension
        self.set_label_to_image(self.initial_image_frame, self.initial_image)
        self.log_string = ""
        self.output_log_label.setPlainText(self.log_string)
        self.buttons_init.emit()

    def update_UI(self):
        self.log_string = self.controller.log_string
        self.output_log_label.setPlainText(self.log_string)
        self.output_log_label.verticalScrollBar().setSliderPosition(self.output_log_label.verticalScrollBar().maximum())
        if self.image_updated:
            self.img_update.emit()
            self.image_updated = False

    def set_filepath(self):
        path = self.file_set[self.file_idx]
        config.file_name = os.path.basename(path).split('.')[0]
        config.file_extension = '.' + os.path.basename(path).split('.')[1]
        config.infile_path = os.path.dirname(path)

    def reset_controller(self):
        self.controller = controller.Controller()
        self.controller.ui_update.connect(self.update_UI)
        self.controller.image_update.connect(self.set_image_updated)

    def reset_UI(self):
        self.initial_image_frame.setText("The initial image will appear here once it is loaded.")
        self.skeleton_image_frame.setText("The skeleton image will appear here, updating as it is refined.")
        self.log_string = ""
        self.set_buttons_initial()
        self.update_UI()

    def set_buttons_initial(self):
        self.buttons_init.emit()

    def set_buttons_running(self):
        self.buttons_run.emit()

    def set_buttons_finished(self):
        self.buttons_end.emit()

    def buttonsetup_group1(self, button):
        self.buttons_init.connect(button.show)
        self.buttons_run.connect(button.hide)
        self.buttons_end.connect(button.hide)

    def buttonsetup_group2(self, button):
        self.buttons_init.connect(button.hide)
        self.buttons_run.connect(button.show)
        self.buttons_end.connect(button.hide)

    def buttonsetup_group3(self, button):
        self.buttons_init.connect(button.hide)
        self.buttons_run.connect(button.hide)
        self.buttons_end.connect(button.show)

    def set_label_to_image(self, label, imagepath):
        pixmap = QtGui.QPixmap(imagepath)
        if (pixmap.isNull()):
            return False

        w = min(pixmap.width(),  label.maximumWidth())
        h = min(pixmap.height(), label.maximumHeight())
        pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        return True

    def load_next_file(self):
        self.reset_controller()
        self.reset_UI()
        if self.file_idx < len(self.file_set):
            self.set_filepath()
            self.image_setup()
        else:
            self.log_string = "All files complete!"
            self.output_log_label.setPlainText(self.log_string)

    def set_controller(self, controller):
        self.controller = controller

    def image_setup(self):
        self.buttons_run.emit()
        thread = Thread(target=self.controller.spawn_proper_infile)
        thread.start()
        self.log_string = "Loading file..."
        self.output_log_label.setPlainText(self.log_string)
        self.controller.image_spawned.connect(self.update_image_paths)

    def onclick_input(self):
        # get list of files, store them in config, load first one as preview
        self.file_set = QtGui.QFileDialog.getOpenFileNames(self.select_infile_btn, "Select image files", "", "Images (*.png *.tif *.jpg *.bmp)")
        self.file_idx = 0
        self.load_next_file()

    def onclick_output(self):
        # get output location, store it in config
        config.outfile_path = QtGui.QFileDialog.getExistingDirectory(self.select_output_btn, "Select output directory")

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

    def onclick_skip(self):
        # go to next file, load as preview
        self.file_idx += 1
        self.load_next_file()

    def onclick_cancel(self):
        self.cancel_clicked = True

    def onclick_accept(self):
        # go to next file, load as preview
        self.write.emit()
        while not self.finished_writing:
            time.sleep(1)
        self.finished_writing = False
        self.file_idx += 1
        self.load_next_file()

    def set_write_finished(self):
        self.finished_writing = True

    def onclick_reject_skip(self):
        # go to next file, load as preview
        self.file_idx += 1
        self.load_next_file()

    def onclick_reject_redo(self):
        # clear temp data, set up for new run
        self.load_next_file()

    def analyze(self):
        # load the image file into an ArrayBuilder
        thread = Thread(target=self.controller.load_image_to_array)
        thread.start()
        thread.join()

        #self.initial_image = config.outfile_path + config.file_name +"-initial" + config.proper_file_extension

        # construct a graph and associated node_dict in a AreaBuilder
        thread = Thread(target=self.controller.build_areas)
        thread.start()
        thread.join()

        # print the initial representation of the output with a new Printer

        thread = Thread(target=self.controller.print_background)
        thread.start()
        thread.join()

        #self.updated_image = config.outfile_path + config.file_name + "-analysis" + config.proper_file_extension

        if config.test_radii:
            # reuse the Printer to print radius test images
            thread = Thread(target=self.controller.print_test_radii)
            thread.start()
            thread.join()

        # prune the initial representation down to a skeleton with a TreeBuilder
        thread = Thread(target=self.controller.build_trees)
        thread.start()
        thread.join()

        # reuse the Printer to print the skeleton representation of the output
        thread = Thread(target=self.controller.print_skeleton)
        thread.start()
        thread.join()

        # build root structures with a RootBuilder
        thread = Thread(target=self.controller.build_roots)
        thread.start()
        thread.join()

        # reuse the Printer to print a representation of the roots
        thread = Thread(target=self.controller.print_roots)
        thread.start()
        thread.join()

        # if the user selected it, search for nodules
        if config.search_for_nodules:
            thread = Thread(target=self.controller.find_nodules)
            thread.start()
            thread.join()

            # and print them
            thread = Thread(target=self.controller.print_nodules)
            thread.start()
            thread.join()

        # complete!
        thread = Thread(target=self.controller.print_final_data)
        thread.start()
        thread.join()

        self.set_buttons_finished()