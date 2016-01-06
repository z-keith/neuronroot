# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       main.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Calls and manipulates the controller to perform an iteration of the analysis algorithm
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# noinspection PyUnresolvedReferences
import controller
# noinspection PyUnresolvedReferences
import config
# noinspection PyUnresolvedReferences
import window, sys
from PyQt5.QtWidgets import QApplication

def main():
    """
    Function called on program initialization
    """

    # initialize the Controller object
    current_controller = controller.Controller()

    # initialize a Window
    app = QApplication(sys.argv)
    win = window.MainWindow(current_controller)
    sys.exit(app.exec_())

all_files_1 = [293, 308, 311, 315, 317, 320, 324, 326, 328, 329]
all_files_2 = [335, 426, 427, 428, 429, 446, 449, 455, 459]

trouble_set = [293]

for val in trouble_set:
    config.current_file = val
    main()
