__author__ = 'raquel'
__version__ = '1.0'

import os
import readline
import sys
import re
import random
from collections import OrderedDict

from tabulate import tabulate

from mfs import Media


class Console_ui:

    item_list = r'(?<![-\d])(\d+-\d+|-\d+|\d+-|\d+|all)(?![-\d])'

    cmds = {
        "quit":             r'q',
        "cdup":             r'\.\.',
        "trailer":          r'^\s*trailer\s+',
        "info":             r'^\s*info\s+(?P<index>\d+)\s*',
        "play":             r'^\s*(play\s+)?(\d+|all)\s*',
        "shuffle_play":     r'^\s*shuffle\s+play\s+|^\s*shuffle\s+(\d+|all|-)|^\s*\s+shuffle',
        "shuffle_trailer":  r'shuffle\s+trailer\s+',
        "subtitle":              r'^\s*sub\s+',

    }

    def __init__(self, d):
        self.d = d
        self.update_pwd()

    def history_log(self):
        home = os.path.expanduser("~/")
        config = os.path.join(home, ".config/")
        if not os.path.exists(config):
            os.makedirs(config)
        hmc = os.path.join(config, "hmc/")
        if not os.path.exists(hmc):
            os.makedirs(hmc)
        history_file = os.path.join(hmc, "cmd_history")
        return history_file

    def init_readline(self):
        # readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')
        readline.set_history_length(2000)
        history_file = self.history_log()
        if os.path.exists(history_file):
            readline.read_history_file(history_file)

    def update_pwd(self):

        """ Update self.pwdlist from d """
        self.pwdlist = []
        dirs = sorted([i for i in self.d.list_dirs() if not i.name.startswith('.')], key=lambda x: x.name)
        self.av_f = sorted([i for i in self.d.list_files() if not i.name.startswith('.')
                            and i.is_av()], key=lambda x: x.name)
        self.pwdlist.extend(dirs + self.av_f)

    # def print_list_pwd(self):
    #     print '\n', "Listing of %s: " % self.d.path
    #     print "=" * (len(self.d.path)+13)
    #
    #     for x in range(len(self.pwdlist)):
    #         if self.pwdlist[x] in self.av_f:
    #             try:
    #                 m = Media(self.pwdlist[x]).media
    #                 if re.match("^RARBG.com", self.pwdlist[x].name, re.IGNORECASE) is not None:
    #                     pass
    #                 elif len(re.findall("sample", self.pwdlist[x].name, re.IGNORECASE)) != 0:
    #                     print u"{:3d} : {}".format(x+1, m.film_title), "[%s]" % m.film_year, "- Sample"
    #                 elif hasattr(m, "film_title"):
    #                     if m.film_year != "":
    #                         print u"{:3d} : {}".format(x+1, m.film_title), "[%s]" % m.film_year
    #                     else:
    #                         print u"{:3d} : {}".format(x+1, m.film_title)
    #                 elif hasattr(m, "series_title"):
    #                     print u"{:3d} : {} -".format(x+1, m.series_title), \
    #                         "Season %s Episode %s" % (m.season, m.series_episode)
    #             except Exception:
    #                 print "{:3d} : {}".format(x+1, self.pwdlist[x])
    #         else:
    #             print "{:3d} : {}".format(x+1, self.pwdlist[x])

    def print_list_pwd(self):
        print '\n', "Listing of %s: " % self.d.path
        print "=" * (len(self.d.path)+13)
        for x in range(len(self.pwdlist)):
            print "{:3d} : {}".format(x+1, self.pwdlist[x])


    def _bi_range(self, start, end):
        """
        Inclusive range function, works for reverse ranges.
            eg. 5,2 returns [5,4,3,2] and 2, 4 returns [2,3,4]
        """
        if start == end:
            return start,
        elif end < start:
            return reversed(range(end, start + 1))
        else:
            return range(start, end + 1)

    def multi_c(self, c, end=None):
        end = end or str(len(self.pwdlist))
        items = re.findall(self.item_list, c, re.IGNORECASE)
        alltracks = []

        for x in items:
            if x.lower() == "all":
                start = [x for x in self.pwdlist if x.is_av()][0]
                x = str(self.pwdlist.index(start) + 1) + "-"

            if x.startswith("-"):
                x = "1" + x

            elif x.endswith("-"):
                x = x + end

            if "-" in x:
                nrange = x.split("-")
                startend = map(int, nrange)
                alltracks += self._bi_range(*startend)

            else:
                alltracks.append(int(x))
        return alltracks

    @staticmethod
    def format_info(file):
        info_method = Media(file)
        info = info_method.load_info()
        if "imdb" in info.keys():
            film_info = info
            if film_info["imdb"] is None:
                print "Currently there is no information for this film"
            else:
                print film_info["imdb"].summary().encode('utf8')
                if film_info["rt"] is None:
                    print "\nNo Rotten Tomato score available for the film"
                else:
                    rt_rating = film_info["rt"]["ratings"]
                    print "\nRotten Tomato scores: ",
                    for key, value in rt_rating.iteritems():
                        print "%s: %s    " % (key, value),
                    print
        if "tvdb" in info.keys():
            show_info = info
            if show_info is None:
                print "No information on the show or film"
            else:
                show = show_info["tvdb"]
                # show_imdb = self.imdb_get_results(show.IMDB_ID)[0]
                # IMDb().update(show_imdb)

                e = show_info["episode"]
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

                dict2 = OrderedDict([(e.SeasonNumber, " Epi %s - %s" % (e.EpisodeNumber, e.EpisodeName)),
                                     ("Episode Air Date", e.FirstAired),
                                     ("Episode Rating", e.Rating),
                                     ("Episode Plot", e.Overview)])

                print tabulate(dict1.items(), stralign="left", tablefmt="plain")
                print "\n"
                print tabulate(dict2.items(), stralign="left", tablefmt="plain")

    def execute(self, cmd=None, match=None, choice=None):

        if cmd == "quit":
            print "exiting..."
            return "exit"

        if cmd == "cdup":
            self.d.cdup()
            self.update_pwd()
            return "ls"

        if cmd == "trailer":
            try:
                self.play_list(choice, trailer=True)
                return "ls"
            except Exception as e:
                print "Error in input: %s" % e
                print "Please enter a correct index for the file."
                return "prompt"

        if cmd == "subtitle":
            try:
                self.play_list(choice, sub=True)
                return "prompt"
            except Exception as e:
                print "Error in input: %s" % e
                print "Please enter a correct index for the file."
                return "prompt"

        if cmd == "play":
            try:
                self.play_list(choice)
                return "ls"
            except Exception as e:
                print "Error in input: %s" % e
                print "Please enter a correct index for the file."
                return "prompt"

        if cmd == "shuffle_trailer":
            try:
                self.play_list(choice, shuffle=True, trailer=True)
                return "ls"
            except Exception as e:
                print "Error in input: %s" % e
                print "Please enter a correct index for the file."
                return "prompt"

        if cmd == "shuffle_play":
            try:
                self.play_list(choice, shuffle=True)
                return "ls"
            except Exception as e:
                print "Error in input: %s" % e
                print "Please enter a correct index for the file."
                return "prompt"

        if cmd == "info":
            info_choice = match.group('index')
            try:
                item = self.pwdlist[int(info_choice)-1]
                print '\n\n'
                self.format_info(item)
                return "prompt"
            except Exception as e:
                print "Error in input: %s" % e
            return "prompt"

    @staticmethod
    def prompt_for_exit():
        print "Press ctrl+c again to exit"
        try:
            userinput = raw_input()
        except (KeyboardInterrupt, EOFError):
            sys.exit()
        return userinput

    @staticmethod
    def get_input():
        try:
            choice = raw_input("\nChoose a media file to play: ")
        except (KeyboardInterrupt, EOFError):
            print '\n\nKeyboard interrupt caught, press Ctrl+c to exit.'
            try:
                choice = raw_input("\nChoose a media file to play: ")
            except (KeyboardInterrupt, EOFError):
                print "\n\nExiting...\n"
                sys.exit()
        return choice

    def event_loop(self):

        self.init_readline()

        next_state = "ls"
        while True:
            # print "next-state: %s" % next_state
            if next_state == "ls":
                self.d.refresh(self.d.path)
                self.update_pwd()
                self.print_list_pwd()

            if next_state == "exit":
                sys.exit(0)

            if next_state == "prompt":
                print "\nPress Enter to list files or directories"
                next_state = "ls"
            choice = self.get_input()
            play_items = self.multi_c(choice)

            for cmd in self.cmds.keys():
                m = re.match(self.cmds[cmd], choice, re.IGNORECASE)
                if m is not None:
                    try:
                        next_state = self.execute(cmd, m, choice=play_items)

                    except NotImplementedError:
                        print "Sorry, command '%s' is not yet implemented" % cmd
            readline.write_history_file(self.history_log())

    def play_list(self, selection, shuffle=False, repeat=False, trailer=False, sub=False):
        v_list = [self.pwdlist[int(x)-1] for x in self.multi_c(str(selection))]
        # Where else can we better handle a directory?!
        if len(v_list) == 1 and v_list[0].is_dir():
            self.d.chdir(v_list[0])
            self.update_pwd()

        if shuffle:
            random.shuffle(v_list)
        n = 0

        while 0 <= n <= len(v_list)-1:
            v = v_list[n]
            try:
                if trailer:
                    Media(v).play_trailer()
                elif sub:
                    Media(v).subtitle()
                else:
                    if v.is_file():
                        Media(v).play()

            except KeyboardInterrupt:
                break
            n += 1

