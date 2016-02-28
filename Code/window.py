import os

from PyQt5 import QtGui, QtCore, QtWidgets

from threading import Thread

import config
import controller
import drawable_image

class MainWindow(QtWidgets.QWidget):

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

    threshold_textedit = None
    dpi_textedit = None
    nodule_checkbox = None

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

    initial_image_pixmap = None

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
        self.controller.ui_update.connect(self.update_log)
        self.controller.image_update.connect(self.img_update.emit)
        self.controller.image_spawned.connect(self.display_preview_image)

        self.initUI()

    def initUI(self):

        QtWidgets.QToolTip.setFont(QtGui.QFont('SansSerif', 8))
        self.setWindowTitle('Neuronroot 1.0')

        hbox = QtWidgets.QHBoxLayout(self)

        self.initial_image_frame = drawable_image.DrawableImage(self)
        self.initial_image_frame.setFixedWidth(350)
        self.initial_image_frame.setFrameShape(1)
        self.initial_image_frame.setLineWidth(1)
        self.initial_image_frame.setAlignment(QtCore.Qt.AlignCenter)
        self.initial_image_frame.setFont(QtGui.QFont('SansSerif', 8))
        self.initial_image_frame.done_starting.connect(self.start_run_thread)
        self.initial_image_frame.done_blacklisting.connect(self.blacklist_finished)
        hbox.addWidget(self.initial_image_frame)

        self.skeleton_image_frame = QtWidgets.QLabel(self)
        self.skeleton_image_frame.setFixedWidth(350)
        self.skeleton_image_frame.setFrameShape(1)
        self.skeleton_image_frame.setLineWidth(1)
        self.skeleton_image_frame.setAlignment(QtCore.Qt.AlignCenter)
        self.skeleton_image_frame.setFont(QtGui.QFont('SansSerif', 8))
        self.img_update.connect(self.display_updating_image)
        hbox.addWidget(self.skeleton_image_frame)

        vbox_widget = QtWidgets.QFrame(self)
        vbox = QtWidgets.QVBoxLayout(vbox_widget)
        vbox_widget.setContentsMargins(0, 0, 0, 0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.output_log_label = QtWidgets.QPlainTextEdit(self)
        self.output_log_label.setFixedWidth(350)
        self.output_log_label.setFrameShape(1)
        self.output_log_label.setLineWidth(1)
        self.output_log_label.setReadOnly(True)
        self.output_log_label.setFont(QtGui.QFont('SansSerif', 8))
        vbox.addWidget(self.output_log_label)

        self.options_widget = QtWidgets.QFrame(self)
        options_row = QtWidgets.QHBoxLayout(self.options_widget)
        self.options_widget.setContentsMargins(0, 0, 0, 0)
        options_row.setContentsMargins(0, 0, 0, 0)

        dpi_label = QtWidgets.QLabel(self)
        dpi_label.setFont(QtGui.QFont('SansSerif', 8))
        dpi_label.setText('DPI:')
        self.dpi_textedit = QtWidgets.QLineEdit(self)
        self.dpi_textedit.setToolTip('Input or correct the DPI value')
        self.dpi_textedit.setFixedWidth(60)
        self.dpi_textedit.returnPressed.connect(self.dpi_update)

        threshold_label = QtWidgets.QLabel(self)
        threshold_label.setFont(QtGui.QFont('SansSerif', 8))
        threshold_label.setText('Threshold multiplier:')
        self.threshold_textedit = QtWidgets.QLineEdit(self)
        self.threshold_textedit.setToolTip('Input the threshold value')
        self.threshold_textedit.setFixedWidth(30)
        self.threshold_textedit.returnPressed.connect(self.threshold_update)

        nodule_label = QtWidgets.QLabel(self)
        nodule_label.setFont(QtGui.QFont('SansSerif', 8))
        nodule_label.setText('Find nodules?')
        self.nodule_checkbox = QtWidgets.QCheckBox(self)
        self.nodule_checkbox.setToolTip('Toggle the nodule search feature')
        self.nodule_checkbox.setChecked(True)

        options_row.addWidget(dpi_label)
        options_row.addWidget(self.dpi_textedit)
        options_row.addWidget(threshold_label)
        options_row.addWidget(self.threshold_textedit)
        options_row.addWidget(nodule_label)
        options_row.addWidget(self.nodule_checkbox)
        options_row.addStretch(1000)
        self.buttonsetup_image_operations(self.options_widget)

        self.blacklist_widget = QtWidgets.QFrame(self)
        blacklist_row = QtWidgets.QHBoxLayout(self.blacklist_widget)
        self.blacklist_widget.setContentsMargins(0, 0, 0, 0)
        blacklist_row.setContentsMargins(0, 0, 0, 0)

        self.add_blacklist_btn = QtWidgets.QPushButton('Blacklist area', self)
        self.add_blacklist_btn.setToolTip('Select an area to ignore')
        self.add_blacklist_btn.clicked.connect(self.onclick_set_blacklist)

        self.clear_blacklist_btn = QtWidgets.QPushButton('Clear blacklist', self)
        self.clear_blacklist_btn.setToolTip('Clear the blacklist')
        self.clear_blacklist_btn.clicked.connect(self.onclick_clear_blacklist)

        blacklist_row.addWidget(self.clear_blacklist_btn)
        blacklist_row.addWidget(self.add_blacklist_btn)
        self.buttonsetup_image_operations(self.blacklist_widget)

        self.io_widget = QtWidgets.QFrame(self)
        io_row = QtWidgets.QHBoxLayout(self.io_widget)
        self.io_widget.setContentsMargins(0, 0, 0, 0)
        io_row.setContentsMargins(0, 0, 0, 0)

        self.select_infile_btn = QtWidgets.QPushButton('Input images...', self)
        self.select_infile_btn.setToolTip('Select files to process')
        self.select_infile_btn.clicked.connect(self.onclick_input)

        self.select_output_btn = QtWidgets.QPushButton('Output location...', self)
        self.select_output_btn.setToolTip('Choose where to save output images and data')
        self.select_output_btn.clicked.connect(self.onclick_output)

        io_row.addWidget(self.select_output_btn)
        io_row.addWidget(self.select_infile_btn)
        self.buttonsetup_io(self.io_widget)

        self.judge_widget = QtWidgets.QFrame(self)
        judge_row = QtWidgets.QHBoxLayout(self.judge_widget)
        self.judge_widget.setContentsMargins(0, 0, 0, 0)
        judge_row.setContentsMargins(0, 0, 0, 0)

        self.discard_redo_btn = QtWidgets.QPushButton('Discard + redo', self)
        self.discard_redo_btn.setToolTip('Retry analysis of the current image')
        self.discard_redo_btn.clicked.connect(self.onclick_reject_redo)

        self.discard_next_btn = QtWidgets.QPushButton('Discard + continue', self)
        self.discard_next_btn.setToolTip('Continue without saving data')
        self.discard_next_btn.clicked.connect(self.onclick_reject_skip)

        self.accept_next_btn = QtWidgets.QPushButton('Accept + continue', self)
        self.accept_next_btn.setToolTip('Save data and continue')
        self.accept_next_btn.clicked.connect(self.onclick_accept)

        judge_row.addWidget(self.discard_redo_btn)
        judge_row.addWidget(self.discard_next_btn)
        judge_row.addWidget(self.accept_next_btn)
        self.buttonsetup_judge_output(self.judge_widget)

        self.ready_widget = QtWidgets.QFrame(self)
        ready_row = QtWidgets.QHBoxLayout(self.ready_widget)
        self.ready_widget.setContentsMargins(0, 0, 0, 0)
        ready_row.setContentsMargins(0, 0, 0, 0)

        self.ready_run_btn = QtWidgets.QPushButton('Ready', self)
        self.ready_run_btn.setToolTip('Select a start point and analyze the current image')
        self.ready_run_btn.clicked.connect(self.onclick_run)

        self.skip_btn = QtWidgets.QPushButton('Skip', self)
        self.skip_btn.setToolTip('Load the next image, ignoring the current one')
        self.skip_btn.clicked.connect(self.onclick_skip)

        ready_row.addWidget(self.skip_btn)
        ready_row.addWidget(self.ready_run_btn)
        self.buttonsetup_image_operations(self.ready_widget)

        vbox.addWidget(self.options_widget)
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
        self.file_set = QtWidgets.QFileDialog.getOpenFileNames(self.select_infile_btn, "Select image files", "../TestImages/", "Images (*.png *.tif *.jpg *.bmp)")[0]
        if self.file_set:
            self.file_idx = 0
            self.load_next_file()

    def onclick_output(self):
        # get output location, store it in config
        config.outfile_path = QtWidgets.QFileDialog.getExistingDirectory(self.select_output_btn, "Select output directory")

    def onclick_set_blacklist(self):
        self.output_log_label.setPlainText("Click and drag to draw a blacklisted area")
        self.initial_image_frame.blacklisting = True
        self.set_buttons_running()

    def blacklist_finished(self):
        self.output_log_label.setPlainText("")
        scaled_y1 = self.initial_image_frame.clicked_y1/self.initial_image_frame.pixmap().height()
        scaled_x1 = self.initial_image_frame.clicked_x1/self.initial_image_frame.pixmap().width()
        scaled_y2 = self.initial_image_frame.clicked_y2/self.initial_image_frame.pixmap().height()
        scaled_x2 = self.initial_image_frame.clicked_x2/self.initial_image_frame.pixmap().width()
        termx1 = min(scaled_x1, scaled_x2)
        termx2 = max(scaled_x1, scaled_x2)
        termy1 = min(scaled_y1, scaled_y2)
        termy2 = max(scaled_y1, scaled_y2)
        new_tup = ((termy1, termx1),(termy2, termx2))    
        config.area_blacklist.append(new_tup)
        self.initial_image_frame.clicked_x1 = 0
        self.initial_image_frame.clicked_x2 = 0
        self.initial_image_frame.clicked_y1 = 0
        self.initial_image_frame.clicked_y2 = 0
        self.initial_image_frame.drawBlacklisted()
        self.set_buttons_ready()

    def onclick_clear_blacklist(self):
        config.area_blacklist = list()
        self.output_log_label.setPlainText("Clearing blacklist")
        self.display_preview_image()
        self.output_log_label.setPlainText("")

    def onclick_run(self):
        self.log_string = ""
        if self.nodule_checkbox.isChecked():
            config.search_for_nodules = True
        else:
            config.search_for_nodules = False
        self.initial_image_frame.starting = True
        self.set_buttons_running()
        self.output_log_label.setPlainText("Select the start point")

    def start_run_thread(self):
        self.output_log_label.setPlainText("")
        scaled_y = int(self.initial_image_frame.clicked_y1/self.scale)
        scaled_x = int(self.initial_image_frame.clicked_x1/self.scale)
        config.seedYX = (scaled_y, scaled_x)
        thread = Thread(target=self.analyze)
        thread.start()
        
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
        self.initial_image_pixmap = QtGui.QPixmap(self.initial_image)
        if (self.initial_image_pixmap.isNull()):
            return
        w = min(self.initial_image_pixmap.width(),  self.initial_image_frame.maximumWidth())
        h = min(self.initial_image_pixmap.height(), self.initial_image_frame.maximumHeight())
        self.scale = 350/self.initial_image_pixmap.width()
        self.initial_image_pixmap = self.initial_image_pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.initial_image_frame.setPixmap(self.initial_image_pixmap)
        self.initial_image_frame.drawBlacklisted()

        self.log_string = ""
        self.output_log_label.setPlainText(self.log_string)
        self.set_buttons_ready()

        self.dpi_textedit.setText(str(int(config.dpi)))
        self.threshold_textedit.setText(str(float(config.threshold_multiplier)))

    def display_updating_image(self):
        pixmap = QtGui.QPixmap(self.updated_image)
        if (pixmap.isNull()):
            return
        w = min(pixmap.width(),  self.skeleton_image_frame.maximumWidth())
        h = min(pixmap.height(), self.skeleton_image_frame.maximumHeight())
        pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.skeleton_image_frame.setPixmap(pixmap)

    def load_next_file(self):
        # self.reset_controller()
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

    def dpi_update(self):
        self.dpi_textedit.clearFocus()
        x = self.dpi_textedit.text()
        try:
            y = int(x)
            config.dpi = y
        except ValueError:
            self.dpi_textedit.setText(str(config.dpi))

    def threshold_update(self):
        self.threshold_textedit.clearFocus()
        x = self.threshold_textedit.text()
        try:
            y = float(x)
            config.threshold_multiplier = y
        except ValueError:
            self.threshold_textedit.setText(str(config.threshold_multiplier))

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
        self.controller.load_image_to_array()

        # construct a graph and associated node_dict in a AreaBuilder
        self.controller.build_areas()

        # print the initial representation of the output with a new Printer

        self.controller.print_background()

        if config.test_radii:
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

        self.set_buttons_finished()