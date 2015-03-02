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

    logging.getLogger('subliminal').addHandler(ch)
    logging.getLogger('subliminal').setLevel(logging.ERROR)
    logging.getLogger('subliminal.api').addHandler(ch)
    logging.getLogger('subliminal.api').setLevel(logging.ERROR)


    logging.getLogger('subliminal').addHandler(fh)
    logging.getLogger('subliminal').setLevel(logging.DEBUG)

    logging.getLogger('subliminal.api').addHandler(fh)
    logging.getLogger('subliminal.api').setLevel(logging.DEBUG)


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
