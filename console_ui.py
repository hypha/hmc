#!/usr/bin/python

__author__ = 'raquel'

# from mfs import Browser
import readline
import sys
import operator


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

    def event_loop(self):

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
            else:
                try:
                    item = self.pwdlist[int(choice)-1]
                    print item
                    if item.is_file():
                        item.play()
                    elif item.is_dir():
                        self.d.chdir(item)
                        self.update_pwd()
                except Exception as e:
                    print "Error in input: %s" % e
                    print "Please enter a correct index for the file."
                # try:
            #     l = self.d.list_files()
            #     item = l[int(choice)-1]
            #     print item
            #     if item.is_file():
            #         item.play()
            # except IndexError:
            #     print "You may only choose a file with a listed number."
            # except ValueError:
            #     print "You may only enter a number."

