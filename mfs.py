__author__ = 'raquel'
# import subprocess
# files = subprocess.popen('ls', stdout=subprocess.pipe)
# ls_files = files.stdout.read()
# print type(ls_files)
# print ls_files


#!/usr/bin/ python
from os import listdir
from os.path import isfile, join, abspath, pardir
from os import walk, system, chdir, getcwd
import subprocess

class Item:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        if self.is_dir():
            return "[ %s ]" % self.name
        else:
            return self.name

    def is_file(self):
        return self.type == "file"

    def is_dir(self):
        return self.type == "dir"

    def play(self):
        if self.is_file():
            sound = self.__shell_quote(self.name)
            system('mpv %s' % sound)
        else:
            # Should raise excep
            raise ValueError("Can't play back %s because it is not a file" % self)
        #subprocess.Popen(["mpv", sound], stdin=subprocess.PIPE,
        #                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def __shell_quote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"



class Directory(object):

    def __init__(self, path):
        self.path = path
        self.dirs = []
        self.files = []
        for (p, d, f) in walk(self.path):
            self.path = p
            for dir in d:
                self.dirs.append(Item(dir, "dir"))
            for file in f:
                self.files.append(Item(file, "file"))
            break

    def list_dirs(self):
        return self.dirs[::]

    def list_files(self):
        return self.files[::]
        # return {i: files[i-1] for i in range(1, len(files)+1)}

    def prevdir(self):
        return abspath(join(self.path, pardir))

    # def list_pre_dir(self):

class Browser(Directory):

    def __init__(self, path = getcwd()):
        super(Browser, self).__init__(path)

    def chdir(self, item):
        chdir(item.name)
        self.__init__(getcwd())

    def cdup(self):
        chdir("..")
        self.__init__(getcwd())
