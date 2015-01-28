#!/usr/bin/python

__author__ = 'raquel'
__version__ = '0.1'
import readline
import sys
import re
import random

class Console_ui:
    def __init__(self, d):
        self.d = d
        self.update_pwd()

    def update_pwd(self):
        self.pwdlist = sorted([i for i in self.d.list_dirs() if not i.name.startswith('.')], key=lambda x: x.name)
        tmp = sorted([i for i in self.d.list_files() if not i.name.startswith('.')], key=lambda x: x.name)
        self.pwdlist.extend(tmp)
        # self.tmp.extend(pwdlist)

    def print_list_pwd(self):
        print '\n', "Listing of %s: " % self.d.path
        print "=" * (len(self.d.path)+13)
        for x in range(len(self.pwdlist)):
            print "{:3d} : {}".format(x+1, self.pwdlist[x])

    def shuffle_op(self, c):
        if not re.match(r'shuffle', c, re.IGNORECASE) is None:
            return self.option == "shuffle"

    def repeat_op(self, c):
        if not re.match(r'repeat', c, re.IGNORECASE) is None:
            return self.option == "repeat"


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
        end = end or str(len(self.pwdlist)-1)
        pattern = r'(?<![-\d])(\d+-\d+|-\d+|\d+-|\d+)(?![-\d])'
        items = re.findall(pattern, c)
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

    def event_loop(self, post=""):
        # readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')

        while True:
            self.print_list_pwd()
            try:
                choice = raw_input("Choose a media file to play: ")
            except KeyboardInterrupt:
                print '\nKeyboard interrupt caught, exiting...'
                sys.exit()

            if choice == "q":
                print "exiting..."
                break
            elif choice == "..":
                self.d.cdup()
                self.update_pwd()
            elif choice.isdigit():
                item = self.pwdlist[int(choice)-1]
                print item
                if item.is_file():
                    item.play()
                elif item.is_dir():
                    self.d.chdir(item)
                    self.update_pwd()
            else:

                try:
                    self.play_list(choice)
                except Exception as e:
                    print "Error in input: %s" % e
                    print "Please enter a correct index for the file."

    def play_list(self, c, shuffle=False, repeat=False):
        if not re.findall(r'shuffle', c, re.IGNORECASE) is None:
            shuffle = True
        if self.repeat_op(c):
            repeat= "repeat" in self.option + ""
        selection = self.multi_c(c)
        # selection = list(set(selection))
        songlist = [self.pwdlist[x-1] for x in selection]
        if shuffle:
            random.shuffle(songlist)
        n = 0
        while 0 <= n <= len(songlist)-1:
            song = songlist[n]

            try:
                p = song.play()
            except KeyboardInterrupt:
                break
            n += 1
#
    # def play_all(self, c=None):
    #     if all(item.is_file() for item in self.pwdlist):
    #         if not re.match(r'shuffle', c, re.IGNORECASE) is None:
    #             random.shuffle(self.pwdlist)
    #             self.play_range(c)
    #         if not re.match(r'all', c, re.IGNORECASE) is None:
    #             self.play_range(c)
