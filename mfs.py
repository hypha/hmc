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

    def __init__(self, path):
        for (p, d, f) in walk(path):
            self.path = p
            self.dirs = d
            self.files = f

    def list_files(self):
        # Change so it uses walk()'s data structure
        files = self.files
        files.sort()
        return files
        # return {i: files[i-1] for i in range(1, len(files)+1)}

    def list_dirs(self):
        dirs = self.dirs
        # May want to add a separate function for different sorting alternatives.
        dirs.sort()
        return {i: dirs[i-1] for i in range(1, len(dirs)+1)}



    def prevdir(self):
        return abspath(join(self.path, pardir))

    def __shell_quote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"

    # def list_pre_dir(self):

    def play_item(self, idx):
        sound = self.__shell_quote(self.files[idx])
        system('mpv %s' % sound)
        #subprocess.Popen(["mpv", sound], stdin=subprocess.PIPE,
        #                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
