__author__ = 'raquel'
__version__ = '1.0'


from os import walk, chdir, getcwd
import os
import subprocess
import re
import shelve
from mimetypes import MimeTypes
import datetime
# import magic

from media_info import MediaInfo
from utils import Struct

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
        return os.path.abspath(self.name)

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
        return os.path.abspath(os.path.join(self.path, os.path.pardir))

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

    @staticmethod
    def get_cache_dir():
        home = os.path.expanduser("~/")
        cache = os.path.join(home, ".cache/")
        if not os.path.exists(cache):
            os.makedirs(cache)
        hmc = os.path.join(cache, "hmc_cache/")
        if not os.path.exists(hmc):
            os.makedirs(hmc)
        return hmc

    __info_in_memory = shelve.open(get_cache_dir.__func__()+".cache")
    expiry = datetime.timedelta(days=10)

    def __init__(self, file):
        # if file.is_dir():
        #     raise ValueError("Item instance of type file required")
        self.file = file
        self.uri = file.file_uri()

    def file_cache(self):
        cache_dir = self.get_cache_dir()
        cache_file = os.path.join(cache_dir, self.file.name + ".cache")
        return cache_file

    def cache_on_disk(self):
        print "retrieving remote information, please wait..."
        info = self.media_info()
        self.__info_in_memory[self.uri] = {"retrieved_on": datetime.datetime.now(),
                                           "data": info}
        return info

    def load_info(self):
        while self.uri in self.__info_in_memory.keys():      # if in memory
            if self.__info_in_memory[self.uri]["retrieved_on"] + self.expiry < datetime.datetime.now():
                return self.cache_on_disk()
            else:
                return self.__info_in_memory[self.uri]["data"]      # load from memory
        else:
            print "retrieving remote information, please wait..."
            return self.cache_on_disk()

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
        if hasattr(media, "film_title"):
            subs = media.get_subtitle(self.file.file_path(), media.film_title)
        else:
            subs = media.get_subtitle(self.file.file_path(), media.series_title)

        if not subs or not sum([len(s) for s in subs.values()]):
            print "\nNo subtitle downloaded"
        else:
            subtitles_count = sum([len(s) for s in subs.values()])
            if subtitles_count == 1:
                print '%d subtitle downloaded' % subtitles_count
            if subtitles_count > 1:
                print "\nYIFY subtitle downloaded"

    def media_info(self):
        media = MediaInfo(self.uri).factory(self.uri)
        if media.type == "film":
            film = media.imdb_film()
            rt_info = media.rt_info(film)
            imdb_info = media.imdb_info(film)
            film_info = dict(imdb=imdb_info, rt=rt_info)
            self.__info_in_memory[self.uri] = {"retrieved_on": datetime.datetime.now(),
                                               "data": film_info}
        # Return what we've got
            return film_info

        if media.type == "series":
            show_match = media.tvdb_match()
            if len(show_match) == 0:
                return
            else:
                show = media.tvdb_info(show_match)
                episode = show[media.season][media.series_episode]

                show_obj = Struct(dict(show.data.items()))

                episode_obj = Struct(dict(episode.data.items()))

                show_info = dict(tvdb=show_obj, episode=episode_obj)
                self.__info_in_memory[self.uri] = {"retrieved_on": datetime.datetime.now(),
                                                   "data": show_info}
                return show_info