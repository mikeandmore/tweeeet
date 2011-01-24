#!/usr/bin/env python

import sys
import gtk
from ui.main import MainWindow

def main():
    gtk.threads_init()
    gtk.threads_enter()
    MainWindow().show()
    gtk.main()
    gtk.threads_leave()
