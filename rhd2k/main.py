#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from mainwindow import MainWindow


def isMac():
    return True


def main():
    """Start the app"""
    app = QApplication(sys.argv)

    if isMac():
        app.setStyle(QStyleFactory.create("Fusion"))

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
