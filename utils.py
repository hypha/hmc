__author__ = 'raquel'

import os
import sys
import StringIO
import contextlib

import subliminal
import xdg.BaseDirectory
import terminal_size as terminalsize

import collections
uni, byt, xinput = str, bytes, input


def utf8_encode(x):
    return x.encode("utf8") if isinstance(x, uni) else x


def utf8_decode(x):
    return x.decode("utf8") if isinstance(x, byt) else x


def __shell_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def subliminal_cache():
    DEFAULT_CACHE_FILE = os.path.join(xdg.BaseDirectory.save_cache_path('subliminal'), 'subliminal_cache.dbm')
    cache_file = os.path.abspath(os.path.expanduser(DEFAULT_CACHE_FILE))
    subliminal.cache_region.configure('dogpile.cache.dbm',
                                      arguments={'filename': cache_file, "lock_factory": subliminal.MutexLock})


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def getxy():
    """ Get terminal size, terminal width and max-results. """
    x, y = terminalsize.get_terminal_size()
    max_results = y - 4 if y < 54 else 50
    max_results = 1 if y <= 5 else max_results
    XYTuple = collections.namedtuple('XYTuple', 'width height max_results')
    return XYTuple(x, y, max_results)

class Struct:
    def __init__(self, obj):
        for k, v in obj.iteritems():
            if isinstance(v, dict):
                setattr(self, k, Struct(v))
            else:
                setattr(self, k, v)

    def __getitem__(self, val):
        return self.__dict__[val]

    def __repr__(self):
        return '{%s}' % str(', '.join('%s : %s' % (k, repr(v)) for (k, v) in self.__dict__.iteritems()))