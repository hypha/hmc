__author__ = 'raquel'
__version__ = '1.0'


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
from imdb import IMDb
from collections import OrderedDict
from pytvdbapi import api
from tabulate import tabulate
import guessit
uni, byt, xinput = str, bytes, input
from babelfish import Language

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

    def file_path(self):
        return abspath(self.name)

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
        self.video = guessit.guess_file_info(file.file_path())


    def video_title(self):
        return self.video["title"]

    def video_year(self):
        if "year" in self.video.keys():
            return self.video["year"]
        else:
            return ""

    def video_series(self):
        return self.video["series"]

    def video_episode(self):
        return self.video["episodeNumber"]

    def video_season(self):
        if "season" in self.video.keys():
            return self.video["season"]
        else:
            return 1

    def trailer_url(self):
        if self.video["type"] == "movie":
            url = "https://gdata.youtube.com/feeds/api/videos/?q={0}+{1}+trailer&alt=jsonc&v=2"
            url = url.format(urllib.quote_plus(self.video_title().encode("ascii", "ignore")), self.video_year())
            wdata = utf8_decode(urllib.urlopen(url).read())
            wdata = json.loads(wdata)
            return wdata['data']['items'][0]['player']['default']
        else:
            raise ValueError('The file or directory must be a film')

    def play_trailer(self):
        try:
            subprocess.call(["mpv", self.trailer_url()])
        except Exception as e:
            print "Error in input: %s" % e
            print "Please select a film file for trailer"

    def film_string(self, t, y):
        if y is not None:
            return t + str("+") + str(y)
        else:
            return t


    def shrink_title(self, t):
        c = 1
        titles = []
        title = re.findall(r'\w+', t)
        while c < len(title):
            title = title[0: len(title) - c]
            titles.append(" ".join(title))
            c + 1
        return titles

    def levenshtein(self, s1, s2):
        s1, s2 = s1.lower(), s2.lower()
        if len(s1) < len(s2):
            return self.levenshtein(s2, s1)

        # len(s1) >= len(s2)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def score_title(self, match_title, title):
        return float(self.levenshtein(match_title, title)) / len(title)

    def imdb_get_results(self, s):
        imdb = IMDb()
        return imdb.search_movie(s)

    def filter_year(self, r):
        year_l = [ind for ind, x in enumerate(r) if "year" in x.keys() and x["year"] == self.video_year()]
        return year_l

    def akas(self, f):
        IMDb().update(f)
        if "akas" in f.keys():
            akas = f["akas"]
            return akas

    def imdb_akas(self, f):
        akas = self.akas(f)
        if akas is not None:
            if self.score_title(f["title"], self.video_title()) <= 0.2:
                return f
            elif not [j for j in [re.match(r'([a-zA-Z]+)::', i, re.U).group(1) for i in akas
                      if not re.match(r'([a-zA-Z]+)::', i, re.U) is None]
                      if self.score_title(j, self.video_title()) <= 0.2] is []:
                return f
            else:
                print "Currently there is no information for this film"

    def shrinked_result(self, r):
        shrinked = [t for t in self.shrink_title(self.video_title())]
        films = []
        for idx, result in enumerate(r):
            if len(result) != 0:
                d = [[i, self.levenshtein(i["title"], shrinked[idx])]
                     for i in result if i["year"] == self.video_year()]
                film = min(d, key=lambda x: x[1])
                films.append(film)
        film = min(films, key=lambda x: x[1])[0]
        return film

    def imdb_match(self):
        results = self.imdb_get_results(self.film_string(self.video_title(), self.video_year()))
        if len(results) != 0:                               # 1. has results
            right_year = self.filter_year(results)       # 1.1 right year
            if len(right_year) != 0:                             # 1.11 has year
                films = [results[y] for y in right_year if          # a. get the film that match with the title
                         self.score_title(results[y]["title"], self.video_title()) <= 0.2]
                if len(films) != 0:
                    return films[0]
                else:                                               # b. if no match, compare akas
                    for y in right_year:
                        film = results[y]
                        film = self.imdb_akas(film)
                        if film is None:
                            pass
                        else:
                            return film
            else:                                                 # 1.12 no year
                scores = [[i, self.levenshtein(i["title"], self.video_title())] for i in results]
                film = min(scores, key=lambda x: x[1])[0]
                return film
        else:                                               # no results, shrink title
            results = [self.imdb_get_results(self.film_string(t, self.video_year()))
                       for t in self.shrink_title(self.video_title())]
            return self.shrinked_result(results)

    def rt_match(self, year, title, rt_results):
        film_l = [x for x in rt_results if year - 2 <= x["year"] <= year + 2
                  and self.score_title(x["title"], title) <= 1.5]
        if len(film_l) == 1:
            film = film_l[0]
            return film["ratings"]
        elif len(film_l) > 1:
            title_score = [self.score_title(x["title"], title) for x in film_l]
            film = film_l[title_score.index(min(title_score))]
            return film["ratings"]
        else:
            pass

    def rt_aka_match(self, f, rt):
        imdb_akas = self.akas(f)
        if imdb_akas is not None:
            akas = [j for j in [re.match(r'([a-zA-Z]+)::', i, re.U).group(1) for i in imdb_akas
                    if not re.match(r'([a-zA-Z]+)::', i, re.U) is None]]
            for aka in akas:
                search = self.film_string(aka, f["year"])
                rt_results = rt.search(search)
                ratings = self.rt_match(f["year"], aka, rt_results)
                return ratings

    def rt_rating(self, f):
        # set up rotten tomato api key
        rt = RT("qzqe4rz874rhxrkrjgrj95g3")
        if "title" in f.keys():
            t = f["title"]
        if "year" in f.keys():
            y = f["year"]
        search = self.film_string(t, y)
        if UnicodeEncodeError:
            search = search.encode("ascii", "ignore")

        rt_results = rt.search(search)
        if len(rt_results) != 0:
            ratings = self.rt_match(f["year"], f["title"], rt_results)
            if ratings is not None:
                return ratings
            else:
                return self.rt_aka_match(f, rt)
        elif len(rt_results) == 0:
            if self.rt_aka_match(f, rt) is not None:
                return self.rt_aka_match(f, rt)
            else:
                pass

    def format_info(self):
        film = self.imdb_match()
        if film == None:
            print "Currently there is no information for this film"
        else:
            rt_rating = self.rt_rating(film)
            IMDb().update(film)
            print film.summary().encode('utf8')
            if rt_rating is None:
                print "\nNo Rotten Tomato score available for the film"
            else:
                print "\nRotten Tomato scores: ",
                for key, value in rt_rating.iteritems():
                    print "%s: %s    " % (key, value),
                print

    def init_tvdb(self):
        return api.TVDB("B1F9E70454EBEB3C")

    def tvdb(self):
        db = self.init_tvdb()
        search = db.search(self.video_series(), "en")
        if len(search) == 0:
            return search
        else:
            if len(search) == 1:
                show = search[0]
            elif len(search) > 1:
                shows = [x for x in search if self.score_title(x.SeriesName, self.video_series()) < 1.5]

                if len(shows) == 1:
                    show = shows[0]
                else:
                    for idx, x in enumerate(search):
                        print idx+1, ": ", x
                    show = search[int(raw_input()) - 1]
            return show

    def format_tvdb(self):
        show = self.tvdb()
        if len(show) == 0:
            print "No information on the show or film"
        else:
            show.update()
            # show_imdb = self.imdb_get_results(show.IMDB_ID)[0]
            # IMDb().update(show_imdb)
            e = show[self.video_season()][self.video_episode()]

            print "\nSeries"
            print "=" * (len("Series"))


            dict1 = OrderedDict([("Title", show.SeriesName),
                                 ("Air Time", "%s - %s;  %s (First aired)"
                                  % (show.Airs_DayOfWeek, show.Airs_Time, show.FirstAired)),
                                 ("Genres", ', '.join(str(p) for p in show.Genre)),
                                 ("Runtime", str(show.Runtime) + " mins"),
                                 ("Network", show.Network),
                                 ("Show Rating", "TVDB - %s (%s votes) " % (show.Rating, show.RatingCount)),
                                 ("Overview", show.Overview)])

            dict2 = OrderedDict([(e.season, " Epi %s - %s" % (e.EpisodeNumber, e.EpisodeName)),
                                 ("Episode Air Date", e.FirstAired),
                                 ("Episode Rating", e.Rating),
                                 ("Episode Plot", e.Overview)])
            # for key, value in dict1.iteritems():
            #     # print key, ":", value
            #     print"{:<13}:  {}".format(key, value)
            # print '\n'
            #
            # for key, value in dict2.iteritems():
            #     # print key, ":", value
            #     print"{:<17}:  {}".format(key, value)
            print tabulate(dict1.items(), stralign="left", tablefmt="plain")
            print "\n"
            print tabulate(dict2.items(), stralign="left", tablefmt="plain")

    def info(self):
        if self.video["type"] == "movie":
            return self.format_info()
        if self.video["type"] == "episode":

            return self.format_tvdb()


    def subtitle(self):
        videos = subliminal.scan_videos([self.file.file_path()], subtitles=True, embedded_subtitles=True)
        p = subliminal.download_best_subtitles(videos, {Language("eng")})
        if len(p) == 0:
            print "No subtitle found"
        else:
            subliminal.save_subtitles(p)
            print "Subtitle downloaded"
