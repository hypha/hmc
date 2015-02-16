#!/usr/bin/env python

__author__ = 'raquel'
__version__ = '0.1'

from mfs import Browser
from console_ui import Console_ui


def main(mypath):
    ui = Console_ui(Browser())
    ui.event_loop()

main(".")
