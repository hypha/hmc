#!/usr/bin/python

__author__ = 'raquel'

from mfs import Directory, Browser
from pprint import pprint
import readline
from console_ui import Console_ui


def main(mypath):
    # print "Parent Directory: ", '\n', d.prevdir()
    ui = Console_ui(Browser())
    ui.event_loop()

main(".")
