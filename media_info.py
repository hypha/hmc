__author__ = 'raquel'

import urllib
import json
import re
from collections import OrderedDict

import guessit
import tabulate
import subliminal
from babelfish import Language
from imdb import IMDb
from rottentomatoes import RT
from pytvdbapi import api
from utils import utf8_decode


class MediaInfo(object):
    def __init__(self, uri):
        # if file.is_dir():
        #     raise ValueError("Item instance of type file required")
        self.uri = uri

    @staticmethod
    def factory(uri):
        video = guessit.guess_file_info(uri)
        if video["type"] == "movie":
            return FilmInfo(uri, guess=video)
        elif video["type"] == "episode":
            return SeriesInfo(uri, guess=video)


class FilmInfo(MediaInfo):
    def __init__(self, uri, guess=None):
        super(FilmInfo, self).__init__(uri)
        self.type = "film"

        if guess is None:
            guess = guessit.guess_file_info(uri)
        self.film_title = guess["title"]
        self.film_year = guess["year"] if "year" in guess.keys() else ""
        self.trailer_url = None

    def get_trailer_url(self):
        if self.trailer_url is None:
            url = "https://gdata.youtube.com/feeds/api/videos/?q={0}+{1}+trailer&alt=jsonc&v=2"
            url = url.format(urllib.quote_plus(self.film_title.encode("ascii", "ignore")), self.film_year)
            wdata = utf8_decode(urllib.urlopen(url).read())
            wdata = json.loads(wdata)
            self.trailer_url = wdata['data']['items'][0]['player']['default']
        return self.trailer_url


class SeriesInfo(MediaInfo):
    def __init__(self, uri, guess=None):
        super(SeriesInfo, self).__init__(uri)
        self.type = "episode"

        if guess is None:
            guess = guessit.guess_file_info(uri)
        self.series_title = guess["series"]
        self.series_year = guess["year"] if "year" in guess.keys() else ""
        self.series_episode = guess["episodeNumber"]
        self.season = guess["season"] if "season" in guess.keys() else 1


class Search_from_file():
    def __init__(self, uri, guess=None):
        if guess is None:
            guess = guessit.guess_file_info(uri)
        self.guess = guess

    @staticmethod
    def search_string(t, y):
        if y is not None:
            return t + str("+") + str(y)
        else:
            return t

    @staticmethod
    def shrink_title(t):
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

    def shrunk_result(self, r):
        shrunk = [t for t in self.shrink_title(self.video_title())]
        films = []
        for idx, result in enumerate(r):
            if len(result) != 0:
                d = [[i, self.levenshtein(i["title"], shrunk[idx])]
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
            return self.shrunk_result(results)

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

    def imdb_update(self, f):
        return IMDb().update(f)


    def subtitle(self):
        videos = subliminal.scan_videos([self.file.file_path()], subtitles=True, embedded_subtitles=True)
        p = subliminal.download_best_subtitles(videos, {Language("eng")})
        if len(p) == 0:
            print "No subtitle found"
        else:
            subliminal.save_subtitles(p)
            print "Subtitle downloaded"
