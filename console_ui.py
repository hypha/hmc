#!/usr/bin/python

__author__ = 'raquel'

from mfs import Directory
from pprint import pprint
import readline


class Console_ui:
    def __init__(self, d):
        self.d = d

    def print_list_files(self):
        l = self.d.list_files()
        print "Media Files: ", '\n'
        for x in range(len(l)):
            print x+1, ':', l[x]

    def event_loop(self):

        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')

        while True:
            self.print_list_files()
            choice = raw_input("Choose a media file to play: ")
            if choice == "q":
                print "exiting..."
                break
            try:
                l = self.d.list_files()
                print l[int(choice)-1]
                self.d.play_item(int(choice)-1)
            except IndexError:
                print "You may only choose a file with a listed number."
            except ValueError:
                print "You may only enter a number."


