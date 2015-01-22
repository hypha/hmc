__author__ = 'raquel'
# import subprocess
# files = subprocess.popen('ls', stdout=subprocess.pipe)
# ls_files = files.stdout.read()
# print type(ls_files)
# print ls_files


#!/usr/bin/ python
from os import listdir
from os.path import isfile, join, abspath, pardir
from os import walk
from os import system
import subprocess


class Directory:
    # self.path = ""
    # self.dirs = []
    # self.files = []

    def __init__(self, path):
        for (p, d, f) in walk(path):
            self.path = p
            self.dirs = d
            self.files = f

    def list_files(self):
        # Change so it uses walk()'s data structure
        files = self.files
        files.sort()
        return {i: files[i-1] for i in range(1, len(files)+1)}

    def list_dirs(self):
        dirs = self.dirs
        # May want to add a separate function for different sorting alternatives.
        dirs.sort()
        return {i: dirs[i-1] for i in range(1, len(dirs)+1)}

    def print_list_files(self):
        d = self.list_files()
        print "Media Files: ", '\n'
        for x in d.keys():
            print x, ':', d[x]

    def prevdir(self):
        return abspath(join(self.path, pardir))

    def __shell_quote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"

    def play_item(self):
        while True:
            try:
                choice = raw_input("Choose a media file to play: ")
                if choice == "q":
                    print "exiting..."
                    break
                sound = self.__shell_quote(self.files[int(choice)])
                print sound
                system('mpv %s 1>/dev/null 2>&1' % sound)

            except IndexError:
                print "You may only choose a file with a listed number."
            except ValueError:
                print "You may only enter a number."

        #subprocess.Popen(["mpv", sound], stdin=subprocess.PIPE,
        #                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
