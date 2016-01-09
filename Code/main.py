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

main()
