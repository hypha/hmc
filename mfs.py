__author__ = 'raquel'
__version__ = '1.0'


from os.path import join, abspath, pardir
from os import walk, chdir, getcwd
import subprocess
import re
from collections import namedtuple
from mimetypes import MimeTypes
# import magic

from media_info import MediaInfo


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

    def file_uri(self):
        return "file:/"+self.file_path()

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
        self.refresh(self.path)
        self.dirs = []
        self.files = []

    def list_dirs(self):
        return self.dirs[::]

    def list_files(self):
        return self.files[::]

    def prevdir(self):
        return abspath(join(self.path, pardir))

    def refresh(self, path):
        self.path = path
        self.dirs = []
        self.files = []
        for (p, d, f) in walk(path):
            self.path = p
            for dir in d:
                self.dirs.append(Item(dir, "dir"))
            for file in f:
                self.files.append(Item(file, "file"))
            break


class Browser(Directory):

    def __init__(self, path=getcwd()):
        super(Browser, self).__init__(path)

    def chdir(self, item):
        chdir(item.name)
        self.refresh(getcwd())

    def cdup(self):
        chdir("..")
        self.refresh(getcwd())


class Media():
    def __init__(self, file):
        # if file.is_dir():
        #     raise ValueError("Item instance of type file required")
        self.file = file
        self.uri = file.file_uri()

    def play(self):
        if self.file.is_file():
            subprocess.call(["mpv",  self.file.name])
        else:
            raise ValueError("Can't play back %s because it is not a file" % self)

    def play_trailer(self):
        media = MediaInfo(self.uri).factory(self.uri)
        trailer = media.get_trailer_url()
        title = trailer.title
        url = trailer.trailer_url
        print "\nPlaying", title, '\n'
        subprocess.call(["mpv", url])

    def subtitle(self):
        media = MediaInfo(self.uri).factory(self.uri)
        subs = media.get_subtitle(self.file.file_path(), media.film_title)
        if not subs or not sum([len(s) for s in subs.values()]):
            print "\nNo subtitle downloaded"
        else:
            subtitles_count = sum([len(s) for s in subs.values()])
            if subtitles_count == 1:
                print '%d subtitle downloaded' % subtitles_count
            if subtitles_count > 1:
                print "\nYIFY subtitle downloaded"

    def info(self):
        media = MediaInfo(self.uri).factory(self.uri)
        if media.type == "film":
            film = media.imdb_film()
            rt_info = media.rt_info(film)
            imdb_info = media.imdb_info(film)
            film_info = namedtuple("film", ["imdb", "rt"])
            return film_info(imdb_info, rt_info)

        if media.type == "series":
            show = media.tvdb_match()
            if len(show) == 0:
                return
            else:
                show = media.tvdb_info(show)
                show_info = namedtuple("series", ["tvdb", "season", "series_episode"])
                return show_info(show, media.season, media.series_episode)




