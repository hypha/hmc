__author__ = 'raquel'

import urllib
import json
import re

import guessit
import subliminal
from babelfish import Language
from imdb import IMDb
from rottentomatoes import RT
from pytvdbapi import api
from utils import utf8_decode
import xdg.BaseDirectory
import os
from subliminal import MutexLock

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

    @staticmethod
    def get_subtitle(file_path):
        DEFAULT_CACHE_FILE = os.path.join(xdg.BaseDirectory.save_cache_path('subliminal'), 'subliminal_cache.dbm')
        cache_file = os.path.abspath(os.path.expanduser(DEFAULT_CACHE_FILE))
        subliminal.cache_region.configure('dogpile.cache.dbm', arguments={'filename': cache_file, "lock_factory": MutexLock })
        provider_configs = {}
        provider_configs['addic7ed'] = {'username': "username", 'password': "password"}
        videos = subliminal.scan_videos([file_path], subtitles=True, embedded_subtitles=True)
        subs = subliminal.api.download_best_subtitles(videos, {Language("eng")}, provider_configs=provider_configs)
        subliminal.save_subtitles(subs)
        return subs


class FilmInfo(MediaInfo):
    def __init__(self, uri, guess=None):
        super(FilmInfo, self).__init__(uri)
        self.type = "film"

        if guess is None:
            guess = guessit.guess_file_info(uri)
        self.film_title = guess["title"]
        self.film_year = guess["year"] if "year" in guess.keys() else ""
        self.trailer_url = None
        self.searched = SearchFromFile(self.uri, guess=guess)

    def get_trailer_url(self):
        if self.trailer_url is None:
            url = "https://gdata.youtube.com/feeds/api/videos/?q={0}+{1}+trailer&alt=jsonc&v=2"
            url = url.format(urllib.quote_plus(self.film_title.encode("ascii", "ignore")), self.film_year)
            wdata = utf8_decode(urllib.urlopen(url).read())
            wdata = json.loads(wdata)
            self.trailer_url = wdata['data']['items'][0]['player']['default']
        return self.trailer_url

    def imdb_film(self):
        film = self.searched.imdb_match()
        return film

    def rt_info(self, film):
        # film = self.imdb_film()
        rt_result = self.searched.rt_result(film)
        return rt_result

    def imdb_info(self, film):
        self.searched.imdb_update(film)
        return film


class SeriesInfo(MediaInfo):
    def __init__(self, uri, guess=None):
        super(SeriesInfo, self).__init__(uri)
        self.type = "series"

        if guess is None:
            guess = guessit.guess_file_info(uri)
        self.series_title = guess["series"]
        self.series_year = guess["year"] if "year" in guess.keys() else ""
        self.series_episode = guess["episodeNumber"]
        self.season = guess["season"] if "season" in guess.keys() else 1
        self.searched = SearchFromFile(self.uri, guess=guess)

    def tvdb_match(self):
        return self.searched.tvdb()

    def tvdb_info(self, series):
        return self.searched.tvdb_update(series)


class SearchFromFile():
    def __init__(self, uri, guess=None):
        if guess is None:
            guess = guessit.guess_file_info(uri)

        if guess["type"] == "movie":
            self.film_title = guess["title"]
            self.film_year = guess["year"] if "year" in guess.keys() else ""

        if guess["type"] == "episode":
            self.series_title = guess["series"]
            self.series_year = guess["year"] if "year" in guess.keys() else ""
            self.series_episode = guess["episodeNumber"]
            self.season = guess["season"] if "season" in guess.keys() else 1

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
            c += 1
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
        year_l = [ind for ind, x in enumerate(r) if "year" in x.keys() and x["year"] == self.film_year]
        return year_l

    def akas(self, f):
        self.imdb_update(f)
        if "akas" in f.keys():
            akas = f["akas"]
            return akas

    def imdb_akas(self, f):
        akas = self.akas(f)
        if akas is not None:
            if self.score_title(f["title"], self.film_title) <= 0.2:
                return f
            elif not [j for j in [re.match(r'([a-zA-Z]+)::', i, re.U).group(1) for i in akas
                      if not re.match(r'([a-zA-Z]+)::', i, re.U) is None]
                      if self.score_title(j, self.film_title) <= 0.2] is []:
                return f
            else:
                print "Currently there is no information for this film"

    def shrunk_film_result(self, title, year, results):
        shrunk = [t for t in self.shrink_title(title)]
        matches = []
        for idx, result in enumerate(results):
            if len(result) != 0:
                if year != "":
                    d = [[i, self.levenshtein(i["title"], shrunk[idx])]
                         for i in result if i["year"] == year]
                    match = min(d, key=lambda x: x[1])
                    matches.append(match)
                else:
                    d = [[i, self.levenshtein(i["title"], shrunk[idx])]
                         for i in result]
                    match = min(d, key=lambda x: x[1])
                    matches.append(match)
        match = min(matches, key=lambda x: x[1])[0]
        return match

    def imdb_match(self):
        results = self.imdb_get_results(self.search_string(self.film_title, self.film_year))
        results = [f for f in results if f["kind"] == "movie"]
        if len(results) != 0:                               # 1. has results
            right_year = self.filter_year(results)       # 1.1 right year
            if len(right_year) != 0:                             # 1.11 has year
                films = [results[y] for y in right_year if          # a. get the film that match with the title
                         self.score_title(results[y]["title"], self.film_title) <= 0.2]
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
                scores = [[i, self.levenshtein(i["title"], self.film_title)] for i in results]
                film = min(scores, key=lambda x: x[1])[0]
                return film
        else:                                               # no results, shrink title
            results = [self.imdb_get_results(self.search_string(t, self.film_year))
                       for t in self.shrink_title(self.film_title)]
            results = [f for f in results if len(f) != 0]
            return self.shrunk_film_result(self.film_title, self.film_year, results)


    def imdb_update(self, f):
        return IMDb().update(f)

    def rt_match(self, year, title, rt_results):
        film_l = [x for x in rt_results if year - 2 <= x["year"] <= year + 2
                  and self.score_title(x["title"], title) <= 1.5]
        if len(film_l) == 1:
            film = film_l[0]
            return film
        elif len(film_l) > 1:
            title_score = [self.score_title(x["title"], title) for x in film_l]
            film = film_l[title_score.index(min(title_score))]
            return film
        else:
            pass

    def rt_aka_match(self, f, rt):
        imdb_akas = self.akas(f)
        if imdb_akas is not None:
            akas = [j for j in [re.match(r'([a-zA-Z]+)::', i, re.U).group(1) for i in imdb_akas
                    if not re.match(r'([a-zA-Z]+)::', i, re.U) is None]]
            for aka in akas:
                search = self.search_string(aka, f["year"])
                rt_results = rt.search(search)
                film = self.rt_match(f["year"], aka, rt_results)
                return film

    def rt_result(self, f):
        # set up rotten tomato api key
        rt = RT("qzqe4rz874rhxrkrjgrj95g3")
        if "title" in f.keys():
            t = f["title"]
        if "year" in f.keys():
            y = f["year"]
        search = self.search_string(t, y)
        if UnicodeEncodeError:
            search = search.encode("ascii", "ignore")

        rt_results = rt.search(search)
        if len(rt_results) != 0:
            result = self.rt_match(f["year"], f["title"], rt_results)
            if result is not None:
                return result
            else:
                return self.rt_aka_match(f, rt)
        elif len(rt_results) == 0:
            if self.rt_aka_match(f, rt) is not None:
                return self.rt_aka_match(f, rt)
            else:
                pass

    def init_tvdb(self):
        return api.TVDB("B1F9E70454EBEB3C")

    def shrink_tv_result(self, title, results):
        shrunk = [t for t in self.shrink_title(title)]
        print shrunk
        matches = []
        for idx, result in enumerate(results):
            if len(result) != 0:
                d = [[i, self.levenshtein(i.SeriesName, shrunk[idx])] for i in result]
                match = min(d, key=lambda x: x[1])
                matches.append(match)
        match = min(matches, key=lambda x: x[1])[0]
        return match

    def tvdb(self):
        db = self.init_tvdb()
        results = db.search(self.series_title, "en")
        if len(results) == 0:
            # results = [db.search(t, "en") for t in self.shrink_title(self.series_title)]
            # results = [show for show in results if len(show) != 0]
            # print len(results)
            # return self.shrink_tv_result(self.series_title, results)
            return results
        else:
            if len(results) == 1:
                show = results[0]
            elif len(results) > 1:
                shows = [x for x in results if self.score_title(x.SeriesName, self.series_title) < 1.5]

                if len(shows) == 1:
                    show = shows[0]
                else:
                    for idx, x in enumerate(results):
                        print idx+1, ": ", x
                    show = results[int(raw_input()) - 1]
            return show

    def tvdb_update(self, series):
        series.update()
        return series


