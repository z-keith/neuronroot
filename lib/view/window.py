from PyQt5 import QtGui, QtCore, QtWidgets

from lib.view import drawable_image


class MainWindow(QtWidgets.QWidget):
    # Stores the reference to the program logic
    controller = None

    # Stores references to UI elements
    # Display elements:
    initial_image_frame = None
    skeleton_image_frame = None
    output_log_label = None
    # Preferences elements:
    threshold_textedit = None
    dpi_textedit = None
    nodule_checkbox = None

    # Stores the current display image paths
    initial_image_path = None
    updated_image_path = None

    # Generate the signals that will be used
    buttons_init = QtCore.pyqtSignal()
    buttons_ready = QtCore.pyqtSignal()
    buttons_run = QtCore.pyqtSignal()
    buttons_end = QtCore.pyqtSignal()

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        controller.qt_window = self

        self.controller.log_update.connect(self.update_log)
        self.controller.image_spawned.connect(self.display_preview_image)
        self.controller.image_update.connect(self.display_updating_image)

        self.init_ui()

    def init_ui(self):

        QtWidgets.QToolTip.setFont(QtGui.QFont('SansSerif', 8))
        self.setWindowTitle('Neuronroot 1.0')

        hbox = QtWidgets.QHBoxLayout(self)

        self.initial_image_frame = drawable_image.DrawableImage(self)
        self.initial_image_frame.setFixedWidth(350)
        self.initial_image_frame.setFrameShape(1)
        self.initial_image_frame.setLineWidth(1)
        self.initial_image_frame.setAlignment(QtCore.Qt.AlignCenter)
        self.initial_image_frame.setFont(QtGui.QFont('SansSerif', 8))
        self.initial_image_frame.done_starting.connect(self.controller.start_run_thread)
        self.initial_image_frame.done_blacklisting.connect(self.controller.blacklist_finished)
        hbox.addWidget(self.initial_image_frame)

        self.skeleton_image_frame = QtWidgets.QLabel(self)
        self.skeleton_image_frame.setFixedWidth(350)
        self.skeleton_image_frame.setFrameShape(1)
        self.skeleton_image_frame.setLineWidth(1)
        self.skeleton_image_frame.setAlignment(QtCore.Qt.AlignCenter)
        self.skeleton_image_frame.setFont(QtGui.QFont('SansSerif', 8))
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

        options_widget = QtWidgets.QFrame(self)
        options_row = QtWidgets.QHBoxLayout(options_widget)
        options_widget.setContentsMargins(0, 0, 0, 0)
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
        # TODO: Load checked status from config

        options_row.addWidget(dpi_label)
        options_row.addWidget(self.dpi_textedit)
        options_row.addWidget(threshold_label)
        options_row.addWidget(self.threshold_textedit)
        options_row.addWidget(nodule_label)
        options_row.addWidget(self.nodule_checkbox)
        options_row.addStretch(1000)
        self.buttonsetup_image_operations(options_widget)

        blacklist_widget = QtWidgets.QFrame(self)
        blacklist_row = QtWidgets.QHBoxLayout(blacklist_widget)
        blacklist_widget.setContentsMargins(0, 0, 0, 0)
        blacklist_row.setContentsMargins(0, 0, 0, 0)

        add_blacklist_btn = QtWidgets.QPushButton('Blacklist area', self)
        add_blacklist_btn.setToolTip('Select an area to ignore')
        add_blacklist_btn.clicked.connect(self.controller.onclick_set_blacklist)

        clear_blacklist_btn = QtWidgets.QPushButton('Clear blacklist', self)
        clear_blacklist_btn.setToolTip('Clear the blacklist')
        clear_blacklist_btn.clicked.connect(self.controller.onclick_clear_blacklist)

        blacklist_row.addWidget(clear_blacklist_btn)
        blacklist_row.addWidget(add_blacklist_btn)
        self.buttonsetup_image_operations(blacklist_widget)

        io_widget = QtWidgets.QFrame(self)
        io_row = QtWidgets.QHBoxLayout(io_widget)
        io_widget.setContentsMargins(0, 0, 0, 0)
        io_row.setContentsMargins(0, 0, 0, 0)

        self.select_infile_btn = QtWidgets.QPushButton('Input images...', self)
        self.select_infile_btn.setToolTip('Select files to process')
        self.select_infile_btn.clicked.connect(self.controller.onclick_input)

        self.select_output_btn = QtWidgets.QPushButton('Output location...', self)
        self.select_output_btn.setToolTip('Choose where to save output images and data')
        self.select_output_btn.clicked.connect(self.controller.onclick_output)

        io_row.addWidget(self.select_output_btn)
        io_row.addWidget(self.select_infile_btn)
        self.buttonsetup_io(io_widget)

        judge_widget = QtWidgets.QFrame(self)
        judge_row = QtWidgets.QHBoxLayout(judge_widget)
        judge_widget.setContentsMargins(0, 0, 0, 0)
        judge_row.setContentsMargins(0, 0, 0, 0)

        discard_redo_btn = QtWidgets.QPushButton('Discard + redo', self)
        discard_redo_btn.setToolTip('Retry analysis of the current image')
        discard_redo_btn.clicked.connect(self.controller.onclick_reject_redo)

        discard_next_btn = QtWidgets.QPushButton('Discard + continue', self)
        discard_next_btn.setToolTip('Continue without saving data')
        discard_next_btn.clicked.connect(self.controller.onclick_reject_skip)

        accept_next_btn = QtWidgets.QPushButton('Accept + continue', self)
        accept_next_btn.setToolTip('Save data and continue')
        accept_next_btn.clicked.connect(self.controller.onclick_accept)

        judge_row.addWidget(discard_redo_btn)
        judge_row.addWidget(discard_next_btn)
        judge_row.addWidget(accept_next_btn)
        self.buttonsetup_judge_output(judge_widget)

        ready_widget = QtWidgets.QFrame(self)
        ready_row = QtWidgets.QHBoxLayout(ready_widget)
        ready_widget.setContentsMargins(0, 0, 0, 0)
        ready_row.setContentsMargins(0, 0, 0, 0)

        ready_run_btn = QtWidgets.QPushButton('Ready', self)
        ready_run_btn.setToolTip('Select a start point and analyze the current image')
        ready_run_btn.clicked.connect(self.controller.onclick_run)

        skip_btn = QtWidgets.QPushButton('Skip', self)
        skip_btn.setToolTip('Load the next image, ignoring the current one')
        skip_btn.clicked.connect(self.controller.onclick_skip)

        ready_row.addWidget(skip_btn)
        ready_row.addWidget(ready_run_btn)
        self.buttonsetup_image_operations(ready_widget)

        vbox.addWidget(options_widget)
        vbox.addWidget(blacklist_widget)
        vbox.addWidget(io_widget)
        vbox.addWidget(judge_widget)
        vbox.addWidget(ready_widget)

        hbox.addWidget(vbox_widget)

        self.reset_ui()

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

    def set_buttons_initial(self):
        self.buttons_init.emit()

    def set_buttons_ready(self):
        self.buttons_ready.emit()

    def set_buttons_running(self):
        self.buttons_run.emit()

    def set_buttons_finished(self):
        self.buttons_end.emit()

    def display_preview_image(self):
        pixmap = QtGui.QPixmap(self.controller.config.initial_image_path)
        if pixmap.isNull():
            self.update_log("Image load failed.")
            return
        w = min(pixmap.width(), self.initial_image_frame.maximumWidth())
        h = min(pixmap.height(), self.initial_image_frame.maximumHeight())
        pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.initial_image_frame.setPixmap(pixmap)
        self.initial_image_frame.draw_blacklisted(self.controller.config.area_blacklist)
        self.set_values(self.controller.config.dpi, self.controller.config.threshold_multiplier,
                        self.controller.config.search_for_nodules)
        self.update_log(" ")
        self.set_buttons_ready()

    def set_values(self, dpi, threshold, nodule):
        self.dpi_textedit.setText(str(int(dpi)))
        self.threshold_textedit.setText(str(int(threshold)))
        self.nodule_checkbox.setChecked(nodule)

    def display_updating_image(self):
        pixmap = QtGui.QPixmap(self.controller.config.updated_image_path)
        if pixmap.isNull():
            return
        w = min(pixmap.width(), self.skeleton_image_frame.maximumWidth())
        h = min(pixmap.height(), self.skeleton_image_frame.maximumHeight())
        pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.skeleton_image_frame.setPixmap(pixmap)

    def update_log(self, text=None):
        if text:
            self.output_log_label.setPlainText(text)
        else:
            self.output_log_label.setPlainText(self.controller.log_string)
        self.output_log_label.verticalScrollBar().setSliderPosition(self.output_log_label.verticalScrollBar().maximum())

    def reset_ui(self):
        self.initial_image_frame.setText("The initial image will appear here once it is loaded.")
        self.skeleton_image_frame.setText("The skeleton image will appear here, updating as it is refined.")
        self.update_log(" ")
        self.set_buttons_initial()

    def get_files(self):
        return QtWidgets.QFileDialog.getOpenFileNames(self.select_infile_btn, "Select image files", "../TestImages/",
                                                      "Images (*.png *.tif *.jpg *.bmp)")[0]

    def get_outfile_path(self):
        return QtWidgets.QFileDialog.getExistingDirectory(self.select_output_btn, "Select output directory")

    def dpi_update(self):
        self.dpi_textedit.clearFocus()
        x = self.dpi_textedit.text()
        try:
            y = int(x)
            self.controller.config.dpi = y
        except ValueError:
            self.dpi_textedit.setText(str(self.controller.config.dpi))

    def threshold_update(self):
        self.threshold_textedit.clearFocus()
        x = self.threshold_textedit.text()
        try:
            y = float(x)
            self.controller.config.threshold_multiplier = y
        except ValueError:
            self.threshold_textedit.setText(str(self.controller.config.threshold_multiplier))
