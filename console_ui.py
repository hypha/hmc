__author__ = 'raquel'
#!/usr/bin/python

__author__ = 'raquel'
__version__ = '0.1'
import readline
import sys
import re
import random
from mfs import Media
import time


class Console_ui:

    item_list = r'(?<![-\d])(\d+-\d+|-\d+|\d+-|\d+)(?![-\d])'

    cmds = {
        "quit":             r'q',
        "cdup":             r'\.\.',
        "trailer":          r'^\s*trailer\s+',
        "info":             r'^\s*info\s+(?P<index>[1-9]+)',
        "play":             r'^\s*(play\s+)?[1-9]+',
        "shuffle_play":     r'^\s*shuffle\s+play\s+|^\s*shuffle\s+|^\s*\s+shuffle',
        "shuffle_trailer":  r'shuffle\s+trailer\s+'
    }

    def __init__(self, d):
        self.d = d
        self.update_pwd()

    def update_pwd(self):
        self.pwdlist = []
        dirs = sorted([i for i in self.d.list_dirs() if not i.name.startswith('.')], key=lambda x: x.name)
        av_f = sorted([i for i in self.d.list_files() if not i.name.startswith('.') and i.is_av()], key=lambda x: x.name)
        self.pwdlist.extend(dirs + av_f)

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
        items = re.findall(self.item_list, c)
        alltracks = []
        for x in items:
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
            item = self.pwdlist[int(info_choice)-1]
            try:
                print '\n\n'
                Media(item).format_info()
                return "prompt"
            except Exception as e:
                print "Error in input: %s" % e
            return "prompt"

    def get_input(self):
        try:
            choice = raw_input("\nChoose a media file to play: ")
        except KeyboardInterrupt:
            print '\nKeyboard interrupt caught, exiting...'
            sys.exit()
        except EOFError:
            print '\nKeyboard interrupt caught, exiting...'
            sys.exit()
        return choice

    def event_loop(self):
        # readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')

        next_state = "ls"
        while True:
            # print "next-state: %s" % next_state
            if next_state == "ls":
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

    def play_list(self, selection, shuffle=False, repeat=False, trailer=False):
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
                else:
                    if v.is_file():
                        v.play()

            except KeyboardInterrupt:
                break
            n += 1

    # def play_all(self, c=None):
    #     if all(item.is_file() for item in self.pwdlist):
    #         if not re.match(r'shuffle', c, re.IGNORECASE) is None:
    #             random.shuffle(self.pwdlist)
    #             self.play_range(c)
    #         if not re.match(r'all', c, re.IGNORECASE) is None:
    #             self.play_range(c)
