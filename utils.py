__author__ = 'raquel'

import subliminal
from subliminal import MutexLock
import os
import xdg.BaseDirectory

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
    subliminal.cache_region.configure('dogpile.cache.dbm', arguments={'filename': cache_file, "lock_factory":MutexLock})