#!/usr/bin/python

__author__ = 'raquel'

from mfs import Directory
from pprint import pprint
import readline


class Console_ui:
    def __init__(self, d):
        self.d = d
        self.update_pwd()

    def update_pwd(self):
        self.pwdlist = self.d.list_files()
        self.pwdlist.sort()
        tmp = self.d.list_dirs()
        tmp.sort()
        self.pwdlist.extend(tmp)


    def print_list_pwd(self):
        print "Listing of %s: " % self.d.path, '\n'
        for x in range(len(self.pwdlist)):
            print x+1, ':', self.pwdlist[x]

    def event_loop(self):

        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')

        while True:
            self.print_list_pwd()
            choice = raw_input("Choose a media file to play: ")
            if choice == "q":
                print "exiting..."
                break
            elif choice == "..":
                self.d.cdup()
                self.update_pwd()
            else:
                item = self.pwdlist[int(choice)-1]
                print item
                if item.is_file():
                    item.play()
                elif item.is_dir():
                    self.d.chdir(item)
                    self.update_pwd()
            # try:
            #     l = self.d.list_files()
            #     item = l[int(choice)-1]
            #     print item
            #     if item.is_file():
            #         item.play()
            # except IndexError:
            #     print "You may only choose a file with a listed number."
            # except ValueError:
            #     print "You may only enter a number."


