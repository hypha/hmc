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
from utils import Struct
from media_info import MediaInfo


class Item(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.uri = self.file_uri()

    def __str__(self):
        if self.is_dir():
            return "[ %s ]" % self.name
        else:
            return self.name

    def is_file(self):
        return self.type == "file"

    def is_dir(self):
        return self.type == "dir"

    def is_uri(self):
        # return self.type == "uri"   #ToDO: change it to stream
        return False

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
        self.items = []

    def list_dirs(self):
        return self.dirs[::]

    def list_files(self):
        return self.items[::]

    def prevdir(self):
        return os.path.abspath(os.path.join(self.path, os.path.pardir))

    def refresh(self, path):
        self.path = path
        self.dirs = []
        self.items = []
        for (p, d, f) in walk(path):
            self.path = p
            for dir in d:
                self.dirs.append(Item(dir, "dir"))
            for file in f:
                self.items.append(Item(file, "file"))
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

    def __init__(self, item):
        # if file.is_dir():
        #     raise ValueError("Item instance of type file required")
        self.item = item
        self.media = MediaInfo(self.item.uri).factory(self.item.uri)

    def file_cache(self):
        cache_dir = self.get_cache_dir()
        cache_file = os.path.join(cache_dir, self.item.name + ".cache")
        return cache_file

    def cache_on_disk(self):
        print "retrieving remote information, please wait...\n"
        info = self.media_info()
        self.__info_in_memory[self.item.uri] = {"retrieved_on": datetime.datetime.now(), "data": info}
        return info

    def load_info(self):
        while self.item.uri in self.__info_in_memory.keys():      # if in memory
            if self.__info_in_memory[self.item.uri]["retrieved_on"] + self.expiry < datetime.datetime.now():
                return self.cache_on_disk()
            else:
                return self.__info_in_memory[self.item.uri]["data"]      # load from memory
        else:
            return self.cache_on_disk()

    def play(self):
        if self.item.is_file():
            subprocess.call(["mpv",  self.item.name])  #ToDo see whether I can play all uri so that it would be a standard.
        elif self.item.is_uri():
            subprocess.call(["mpv", self.item.name])
        else:
            raise ValueError("Can't play back %s because it is not a file" % self)

    def play_trailer(self):
        trailer = self.media.get_trailer_url()
        title = trailer.title
        uri = trailer.trailer_url
        print "\nPlaying", title, '\n'
        subprocess.call(["mpv", uri])

    def subtitle(self):
        if hasattr(self.media, "film_title"):
            subs = self.media.get_subtitle(self.item.file_path(), self.media.film_title)
        else:
            subs = self.media.get_subtitle(self.item.file_path(), self.media.series_title)

        if not subs or not sum([len(s) for s in subs.values()]):
            print "\nNo subtitle downloaded"
        else:
            subtitles_count = sum([len(s) for s in subs.values()])
            if subtitles_count == 1:
                print '%d subtitle downloaded' % subtitles_count
            # if subtitles_count > 1:
            #     print "\nYIFY subtitle downloaded"

    def media_info(self):
        if self.media.type == "film":
            film = self.media.imdb_film()
            rt_info = self.media.rt_info(film)
            imdb_info = self.media.imdb_info(film)
            film_info = dict(imdb=imdb_info, rt=rt_info)
            self.__info_in_memory[self.item.uri] = {"retrieved_on": datetime.datetime.now(),
                                               "data": film_info}
        # Return what we've got
            return film_info

        if self.media.type == "series":
            show_match = self.media.tvdb_match()
            if len(show_match) == 0:
                return
            else:
                show = self.media.tvdb_info(show_match)
                episode = show[self.media.season][self.media.series_episode]

                show_obj = Struct(dict(show.data.items()))

                episode_obj = Struct(dict(episode.data.items()))

                show_info = dict(tvdb=show_obj, episode=episode_obj)
                self.__info_in_memory[self.item.uri] = {"retrieved_on": datetime.datetime.now(),
                                                   "data": show_info}
                return show_info


class uriItem(Item):

    def __init__(self, name, uri):
        super(uriItem, self).__init__(name=name, type="uri")
        self.uri = uri

    def is_uri(self):
        return True
    



