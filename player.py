#!/usr/bin/python

__author__ = 'raquel'

from mfs import Directory
from pprint import pprint
import readline
from console_ui import Console_ui


def main(mypath):
    d = Directory(mypath)
    # print "Parent Directory: ", '\n', d.prevdir()
    ui = Console_ui(d)
    ui.event_loop()

main(".")
