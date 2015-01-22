#!/usr/bin/ python

__author__ = 'raquel'

from mfs import Directory
from pprint import pprint


def main(mypath):
    d = Directory(mypath)
    print "Parent Directory: ", '\n', d.prevdir()
    d.print_list_files()
    d.play_item()


main(".")

