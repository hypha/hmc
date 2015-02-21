__author__ = 'raquel'
__version__ = '1.0'


from os.path import join, abspath, pardir
from os import walk, chdir, getcwd
import subprocess
import re

from mimetypes import MimeTypes
# import magic


class Item:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        if self.is_dir():
            return "[ %s ]" % self.name
        else:
            return self.name

    def is_file(self):
        return self.type == "file"

    def is_dir(self):
        return self.type == "dir"

    @staticmethod
    def __shell_quote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"

    def mime_type(self):
        mime = MimeTypes()
        mimetype = mime.guess_type(self.name)
        # mimetype = subprocess.Popen(["file", self.name, '--mime-type', '-b'],
        #                             stdout=subprocess.PIPE).stdout.read().strip()
        # # mimetype = magic.from_file(self.name, mime=True)
        return mimetype[0]

    def file_type(self):
        if self.mime_type() is None:
            return 'unknown'
        else:
            return re.search(r'(\w)+', self.mime_type()).group()
        # return self.mime_type().split("/")[0]

    def file_path(self):
        return abspath(self.name)

    def is_av(self):
        if self.file_type() == "video":
            return True
        elif self.file_type() == "audio":
            return True
        else:
            return False




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

    def prevdir(self):
        return abspath(join(self.path, pardir))


class Browser(Directory):

    def __init__(self, path=getcwd()):
        super(Browser, self).__init__(path)

    def chdir(self, item):
        chdir(item.name)
        self.__init__(getcwd())

    def cdup(self):
        chdir("..")
        self.__init__(getcwd())


class Media():
    def __init__(self, file):
        # if file.is_dir():
        #     raise ValueError("Item instance of type file required")
        self.file = file

    def play(self):
        if self.file.is_file():
            subprocess.call(["mpv",  self.file.name])
        else:
            raise ValueError("Can't play back %s because it is not a file" % self)

    def play_trailer(self):
        try:
            subprocess.call(["mpv", self.trailer_url()])
        except Exception as e:
            print "Error in input: %s" % e
            print "Please select a film file for trailer"

    def info(self):
        if self.video["type"] == "movie":
            return self.format_film()
        if self.video["type"] == "episode":

            return self.format_tvdb()

