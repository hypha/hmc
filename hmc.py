#!/usr/bin/env python

__author__ = 'raquel'
__version__ = '1.0'

import logging
import os

from mfs import Browser
from console_ui import Console_ui
import utils


def log():
    home = os.path.expanduser("~/")
    log = os.path.join(home, "hmc.log")
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(asctime)s %(levelname)-8s [%(name)s-%(funcName)s:%(lineno)d] %(message)s',
    #                     filename= log,
    #                     filemode="w")


    imdb_logger = logging.getLogger('imdbpy')
    subliminal_logger = logging.getLogger("subliminal")
    subliminal_api_logger = logging.getLogger("subliminal.api")
    tvdb_logger = logging.getLogger("pytvdbapi")
    hmc_logger = logging.getLogger(__name__)


    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    fh = logging.FileHandler(log)
    fh.setLevel(logging.DEBUG)

    formatter_fh = logging.Formatter('%(asctime)s %(levelname)-8s [%(name)s-%(funcName)s:%(lineno)d] %(message)s')
    formatter_ch = logging.Formatter('%(levelname)-8s [%(name)s-%(funcName)s:%(lineno)d] %(message)s')

    fh.setFormatter(formatter_fh)
    ch.setFormatter(formatter_ch)


    imdb_logger.addHandler(fh)
    imdb_logger.setLevel(logging.DEBUG)

    subliminal_logger.addHandler(ch)
    subliminal_logger.setLevel(logging.ERROR)

    subliminal_api_logger.addHandler(ch)
    subliminal_api_logger.setLevel(logging.ERROR)


    subliminal_logger.addHandler(fh)
    subliminal_logger.setLevel(logging.DEBUG)

    subliminal_api_logger.addHandler(fh)
    subliminal_api_logger.setLevel(logging.DEBUG)

    # tvdb_logger.addHandler(ch)              # choose not to print error message for tvdb because of
    # tvdb_logger.setLevel(logging.ERROR)     # some weird error that I do not understand from the library

    tvdb_logger.addHandler(fh)
    tvdb_logger.setLevel(logging.DEBUG)

    hmc_logger.addHandler(ch)
    hmc_logger.setLevel(logging.ERROR)

    hmc_logger.addHandler(fh)
    hmc_logger.setLevel(logging.DEBUG)

def main(mypath):
    ui = Console_ui(Browser())
    ui.event_loop()


if __name__ == "__main__":
    utils.subliminal_cache()
    # logging.basicConfig(filename="/home/raquel/hmc.log",
    #                     format='%(asctime)s %(levelname)-8s [%(name)s-%(funcName)s:%(lineno)d] %(message)s',
    #                     level=logging.DEBUG)
    log()
    main(".")
