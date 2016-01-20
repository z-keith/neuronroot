import os

from PyQt4 import QtGui, QtCore

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

    discard_redo_btn = None
    discard_next_btn = None
    accept_next_btn = None

    ready_run_btn = None
    skip_btn = None

    # Stores the log output as a string
    log_string = ""

    # Stores the display image paths
    initial_image = None
    updated_image = None

    # Signals
    buttons_init = QtCore.pyqtSignal()
    buttons_ready = QtCore.pyqtSignal()
    buttons_run = QtCore.pyqtSignal()
    buttons_end = QtCore.pyqtSignal()

    img_update = QtCore.pyqtSignal()

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        controller.qt_window = self
        controller.ui_update.connect(self.update_log)
        controller.image_update.connect(self.img_update.emit)

        self.initUI()

    def initUI(self):

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 8))
        self.setWindowTitle('Neuronroot 1.0')

        hbox = QtGui.QHBoxLayout(self)

        self.initial_image_frame = QtGui.QLabel(self)
        self.initial_image_frame.setFixedWidth(350)
        self.initial_image_frame.setFrameShape(1)
        self.initial_image_frame.setLineWidth(1)
        self.initial_image_frame.setAlignment(QtCore.Qt.AlignCenter)
        self.initial_image_frame.setFont(QtGui.QFont('SansSerif', 8))
        hbox.addWidget(self.initial_image_frame)

        self.skeleton_image_frame = QtGui.QLabel(self)
        self.skeleton_image_frame.setFixedWidth(350)
        self.skeleton_image_frame.setFrameShape(1)
        self.skeleton_image_frame.setLineWidth(1)
        self.skeleton_image_frame.setAlignment(QtCore.Qt.AlignCenter)
        self.skeleton_image_frame.setFont(QtGui.QFont('SansSerif', 8))
        self.img_update.connect(self.display_updating_image)
        hbox.addWidget(self.skeleton_image_frame)

        vbox_widget = QtGui.QFrame(self)
        vbox = QtGui.QVBoxLayout(vbox_widget)
        vbox_widget.setContentsMargins(0, 0, 0, 0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.output_log_label = QtGui.QPlainTextEdit(self)
        self.output_log_label.setFixedWidth(350)
        self.output_log_label.setFrameShape(1)
        self.output_log_label.setLineWidth(1)
        self.output_log_label.setReadOnly(True)
        self.output_log_label.setFont(QtGui.QFont('SansSerif', 8))
        vbox.addWidget(self.output_log_label)

        self.blacklist_widget = QtGui.QFrame(self)
        blacklist_row = QtGui.QHBoxLayout(self.blacklist_widget)
        self.blacklist_widget.setContentsMargins(0, 0, 0, 0)
        blacklist_row.setContentsMargins(0, 0, 0, 0)

        self.add_blacklist_btn = QtGui.QPushButton('Blacklist area', self)
        self.add_blacklist_btn.setToolTip('Select an area to ignore')
        self.add_blacklist_btn.clicked.connect(self.onclick_set_blacklist)

        self.clear_blacklist_btn = QtGui.QPushButton('Clear blacklist', self)
        self.clear_blacklist_btn.setToolTip('Clear the blacklist')
        self.clear_blacklist_btn.clicked.connect(self.onclick_clear_blacklist)

        blacklist_row.addWidget(self.clear_blacklist_btn)
        blacklist_row.addWidget(self.add_blacklist_btn)
        self.buttonsetup_image_operations(self.blacklist_widget)

        self.io_widget = QtGui.QFrame(self)
        io_row = QtGui.QHBoxLayout(self.io_widget)
        self.io_widget.setContentsMargins(0, 0, 0, 0)
        io_row.setContentsMargins(0, 0, 0, 0)

        self.select_infile_btn = QtGui.QPushButton('Input images...', self)
        self.select_infile_btn.setToolTip('Select files to process')
        self.select_infile_btn.clicked.connect(self.onclick_input)

        self.select_output_btn = QtGui.QPushButton('Output location...', self)
        self.select_output_btn.setToolTip('Choose where to save output images and data')
        self.select_output_btn.clicked.connect(self.onclick_output)

        io_row.addWidget(self.select_output_btn)
        io_row.addWidget(self.select_infile_btn)
        self.buttonsetup_io(self.io_widget)

        self.judge_widget = QtGui.QFrame(self)
        judge_row = QtGui.QHBoxLayout(self.judge_widget)
        self.judge_widget.setContentsMargins(0, 0, 0, 0)
        judge_row.setContentsMargins(0, 0, 0, 0)

        self.discard_redo_btn = QtGui.QPushButton('Discard + redo', self)
        self.discard_redo_btn.setToolTip('Retry analysis of the current image')
        self.discard_redo_btn.clicked.connect(self.onclick_reject_redo)

        self.discard_next_btn = QtGui.QPushButton('Discard + continue', self)
        self.discard_next_btn.setToolTip('Continue without saving data')
        self.discard_next_btn.clicked.connect(self.onclick_reject_skip)

        self.accept_next_btn = QtGui.QPushButton('Accept + continue', self)
        self.accept_next_btn.setToolTip('Save data and continue')
        self.accept_next_btn.clicked.connect(self.onclick_accept)

        judge_row.addWidget(self.discard_redo_btn)
        judge_row.addWidget(self.discard_next_btn)
        judge_row.addWidget(self.accept_next_btn)
        self.buttonsetup_judge_output(self.judge_widget)

        self.ready_widget = QtGui.QFrame(self)
        ready_row = QtGui.QHBoxLayout(self.ready_widget)
        self.ready_widget.setContentsMargins(0, 0, 0, 0)
        ready_row.setContentsMargins(0, 0, 0, 0)

        self.ready_run_btn = QtGui.QPushButton('Ready', self)
        self.ready_run_btn.setToolTip('Select a start point and analyze the current image')
        self.ready_run_btn.clicked.connect(self.onclick_run)

        self.skip_btn = QtGui.QPushButton('Skip', self)
        self.skip_btn.setToolTip('Load the next image, ignoring the current one')
        self.skip_btn.clicked.connect(self.onclick_skip)

        ready_row.addWidget(self.skip_btn)
        ready_row.addWidget(self.ready_run_btn)
        self.buttonsetup_image_operations(self.ready_widget)

        vbox.addWidget(self.blacklist_widget)
        vbox.addWidget(self.io_widget)
        vbox.addWidget(self.judge_widget)
        vbox.addWidget(self.ready_widget)

        hbox.addWidget(vbox_widget)

        self.reset_UI()

        self.show()

    def buttonsetup_io(self, row):
        self.buttons_init.connect(row.show)
        self.buttons_ready.connect(row.show)
        self.buttons_run.connect(row.hide)
        self.buttons_end.connect(row.hide)

    def buttonsetup_image_operations(self, row):
        self.buttons_init.connect(row.hide)
        self.buttons_ready.connect(row.show)
        self.buttons_run.connect(row.hide)
        self.buttons_end.connect(row.hide)

    def buttonsetup_judge_output(self, row):
        self.buttons_init.connect(row.hide)
        self.buttons_ready.connect(row.hide)
        self.buttons_run.connect(row.hide)
        self.buttons_end.connect(row.show)

    def onclick_input(self):
        # get list of files, store them in config, load first one as preview
        self.file_set = QtGui.QFileDialog.getOpenFileNames(self.select_infile_btn, "Select image files", "", "Images (*.png *.tif *.jpg *.bmp)")
        if self.file_set:
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

    def onclick_accept(self):
        # go to next file, load as preview
        self.controller.write_output()
        self.file_idx += 1
        self.load_next_file()

    def onclick_reject_skip(self):
        # go to next file, load as preview
        self.file_idx += 1
        self.load_next_file()

    def onclick_reject_redo(self):
        # clear temp data, set up for new run
        self.load_next_file()

    def set_buttons_initial(self):
        self.buttons_init.emit()

    def set_buttons_ready(self):
        self.buttons_ready.emit()

    def set_buttons_running(self):
        self.buttons_run.emit()

    def set_buttons_finished(self):
        self.buttons_end.emit()

    def display_preview_image(self):
        pixmap = QtGui.QPixmap(self.initial_image)
        if (pixmap.isNull()):
            return
        w = min(pixmap.width(),  self.initial_image_frame.maximumWidth())
        h = min(pixmap.height(), self.initial_image_frame.maximumHeight())
        pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.initial_image_frame.setPixmap(pixmap)

        self.log_string = ""
        self.output_log_label.setPlainText(self.log_string)
        self.set_buttons_ready()

    def display_updating_image(self):
        pixmap = QtGui.QPixmap(self.updated_image)
        if (pixmap.isNull()):
            return
        w = min(pixmap.width(),  self.skeleton_image_frame.maximumWidth())
        h = min(pixmap.height(), self.skeleton_image_frame.maximumHeight())
        pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.skeleton_image_frame.setPixmap(pixmap)

    def load_next_file(self):
        self.reset_controller()
        self.reset_UI()
        if self.file_idx < len(self.file_set):
            self.set_filepath()
            self.image_setup()
        else:
            self.log_string = "All files complete!"
            self.output_log_label.setPlainText(self.log_string)
            self.set_buttons_initial()

    def image_setup(self):
        self.buttons_run.emit()
        thread = Thread(target=self.controller.spawn_proper_infile)
        thread.start()
        self.log_string = "Loading file..."
        self.update_image_paths()
        self.output_log_label.setPlainText(self.log_string)
        self.controller.image_spawned.connect(self.display_preview_image)

    def update_image_paths(self):
        self.initial_image = config.outfile_path + "/" + config.file_name +"-initial" + config.proper_file_extension
        self.updated_image = config.outfile_path + "/" + config.file_name + "-analysis" + config.proper_file_extension

    def update_log(self):
        self.log_string = self.controller.log_string
        self.output_log_label.setPlainText(self.log_string)
        self.output_log_label.verticalScrollBar().setSliderPosition(self.output_log_label.verticalScrollBar().maximum())

    def set_filepath(self):
        path = self.file_set[self.file_idx]
        config.file_name = os.path.basename(path).split('.')[0]
        config.file_extension = '.' + os.path.basename(path).split('.')[1]
        config.infile_path = os.path.dirname(path)

    def reset_controller(self):
        self.controller = controller.Controller()
        self.controller.ui_update.connect(self.update_log)
        self.controller.image_update.connect(self.img_update.emit)

    def reset_UI(self):
        self.initial_image_frame.setText("The initial image will appear here once it is loaded.")
        self.skeleton_image_frame.setText("The skeleton image will appear here, updating as it is refined.")
        self.log_string = ""
        self.output_log_label.setPlainText(self.log_string)
        self.set_buttons_initial()

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