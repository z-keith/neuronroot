import os
from threading import Thread

from PyQt5.QtCore import pyqtSignal, QObject
from PIL import Image


class Controller(QObject):
    # Configuration info
    config = None

    # Stores the list of files currently in use
    file_set = None
    file_idx = None

    window = None
    model = None

    csv_out_string = ""

    # Debug/testing objects
    log_string = ""

    # Updated signal
    image_update = pyqtSignal()
    log_update = pyqtSignal()
    image_spawned = pyqtSignal()

    def __init__(self, config_obj):
        QObject.__init__(self)
        self.config = config_obj

    def signal_log_update(self):
        self.log_string = self.model.log_string
        self.log_update.emit()

    def signal_image_update(self):
        self.image_update.emit()

    def signal_initial_draw(self):
        self.image_spawned.emit()

    def onclick_input(self):
        # get list of files, load first one as preview
        self.file_set = self.window.get_files()
        if self.file_set:
            self.file_idx = 0
            self.load_next_file()

    def onclick_output(self):
        # get output location, store it in config
        self.config.outfile_path = self.window.get_outfile_path()

    def onclick_set_blacklist(self):
        self.window.update_log("Click and drag to draw a blacklisted area")
        self.window.initial_image_frame.blacklisting = True
        self.window.set_buttons_running()

    def onclick_clear_blacklist(self):
        self.config.area_blacklist = list()
        self.window.update_log("Clearing blacklist")
        self.signal_initial_draw()
        self.window.update_log(" ")

    def onclick_run(self):
        if self.window.nodule_checkbox.isChecked():
            self.config.search_for_nodules = True
        else:
            self.config.search_for_nodules = False
        self.window.initial_image_frame.starting = True
        self.window.set_buttons_running()
        self.window.update_log("Select the start point")

    def onclick_skip(self):
        # go to next file, load as preview
        self.file_idx += 1
        self.load_next_file()

    def onclick_accept(self):
        # go to next file, load as preview
        outfile = open(self.config.outfile_path + "/output.csv", "a")
        outfile.writelines(self.model.csv_out_string)
        outfile.close()

        os.remove(self.config.initial_image_path)

        self.file_idx += 1
        self.load_next_file()

    def onclick_reject_skip(self):
        # go to next file, load as preview
        os.remove(self.config.initial_image_path)

        self.file_idx += 1
        self.load_next_file()

    def onclick_reject_redo(self):
        # clear temp data, set up for new run
        self.load_next_file()

    def blacklist_finished(self):
        self.window.update_log(" ")

        new_blacklist_zone = self.window.initial_image_frame.generate_blacklist_rectangle()
        self.config.area_blacklist.append(new_blacklist_zone)

        self.window.initial_image_frame.reset()
        self.window.initial_image_frame.draw_blacklisted(self.config.area_blacklist)

        self.window.set_buttons_ready()

    def load_next_file(self):
        self.window.reset_ui()
        if self.file_idx < len(self.file_set):
            path = self.file_set[self.file_idx]
            self.config.file_name = os.path.basename(path).split('.')[0]
            self.config.file_extension = '.' + os.path.basename(path).split('.')[1]
            self.config.infile_path = os.path.dirname(path)

            self.config.initial_image_path = \
                self.config.outfile_path + self.config.file_name + "-initial" + self.config.proper_file_extension
            self.config.updated_image_path = \
                self.config.outfile_path + self.config.file_name + "-analysis" + self.config.proper_file_extension

            self.window.set_buttons_running()

            if os.path.isfile(self.config.initial_image_path):
                self.signal_initial_draw()
            else:
                thread = Thread(target=self.spawn_proper_infile)
                thread.start()
                self.window.update_log("Loading file...")

        else:
            self.window.update_log("All files complete!")
            self.window.set_buttons_initial()

    def start_run_thread(self):
        self.window.update_log(" ")

        self.config.seedYX = self.window.initial_image_frame.generate_click_point()

        self.window.initial_image_frame.reset()

        thread = Thread(target=self.analyze)
        thread.start()

    def analyze(self):
        # load the image file into an ArrayBuilder
        self.model.load_image_to_array(self.config.initial_image_path)

        # construct a graph and associated node_dict in a AreaBuilder
        self.model.build_areas()

        # print the initial representation of the output with a new Printer
        self.model.print_background()

        if self.config.test_radii:
            self.model.print_test_radii()

        # prune the initial representation down to a skeleton with a TreeBuilder
        self.model.build_trees()

        # reuse the Printer to print the skeleton representation of the output
        self.model.print_skeleton()

        # build root structures with a RootBuilder
        self.model.build_roots()

        # reuse the Printer to print a representation of the roots
        self.model.print_roots()

        # if the user selected it, search for nodules
        if self.config.search_for_nodules:
            self.model.find_nodules()

            # and print them
            self.model.print_nodules()

        # complete!
        self.model.display_final_data()

        self.model.clean_up()

        self.window.set_buttons_finished()

    def spawn_proper_infile(self):
        initial_image = Image.open(
            self.config.infile_path + "/" + self.config.file_name + self.config.file_extension).convert('RGB')
        initial_image.save(self.config.initial_image_path)
        if 'dpi' in initial_image.info:
            self.config.dpi = initial_image.info['dpi'][0]
        self.signal_initial_draw()

    def scale_config(self, scale_factor):
        self.config.cm_per_pixel = 1/(470 * scale_factor)
        self.config.seedYX = (scale_factor*self.config.seedYX[0]), (scale_factor*self.config.seedYX[1])
