__author__ = 'raquel'
__version__ = '0.1'


from os.path import join, abspath, pardir
from os import walk, system, chdir, getcwd, popen
import subprocess
import re
from mimetypes import MimeTypes
# import magic
import subliminal
import urllib
import json
from rottentomatoes import RT
rt = RT("qzqe4rz874rhxrkrjgrj95g3")


uni, byt, xinput = str, bytes, input


def utf8_encode(x):
    return x.encode("utf8") if isinstance(x, uni) else x


def utf8_decode(x):
    return x.decode("utf8") if isinstance(x, byt) else x


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

    def is_av(self):
        if self.file_type() == "video":
            return True
        elif self.file_type() == "audio":
            return True
        else:
            return False

    def play(self):
        if self.is_file():
            subprocess.call(["mpv",  self.name])
        else:
            # Should raise exception
            raise ValueError("Can't play back %s because it is not a file" % self)


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
        if file.is_dir():
            raise ValueError("Item instance of type file required")
        self.file = file
        self.video = subliminal.Video.fromname(file.name)

    def trailer_url(self):
        if type(self.video) == subliminal.video.Movie:
            url = "https://gdata.youtube.com/feeds/api/videos/?q={0}+{1}+trailer&alt=jsonc&v=2"
            url = url.format(urllib.quote_plus(self.video.title), self.video.year)
            wdata = utf8_decode(urllib.urlopen(url).read())
            wdata = json.loads(wdata)
            return wdata['data']['items'][0]['player']['default']
        else:
            raise ValueError('The file or directory must be a Movie')

    def play_trailer(self):
        try:
            subprocess.call(["mpv", self.trailer_url()])
        except Exception as e:
            print "Error in input: %s" % e
            print "Please select a Movie file for trailer"


    def rt_info(self):
        rt_string = self.video.title + str(" ") + str(self.video.year)
        film_info = rt.search(rt_string)[0]
        film_info["genres"] = rt.info(film_info.get("id")).get("genres")
        film_info["directors"] = rt.info(film_info.get("id")).get("abridged_directors")
        return film_info

    def format_info(self):
        info = self.rt_info()
        order = ["title", "year", "genres", "directors", "runtime", "critics_consensus",
                 "ratings", "synopsis"]
        results = [(k, info[k]) for k in order if info[k] != ""]
        for x in results:
            print x
