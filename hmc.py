#!/usr/bin/env python

__author__ = 'raquel'
__version__ = '1.0'

import logging

from mfs import Browser
from console_ui import Console_ui
import utils


def logging_init(log_level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)-8s [%(name)s-%(funcName)s:%(lineno)d] %(message)s'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(log_level)
    logging.getLogger('subliminal').addHandler(handler)
    logging.getLogger('subliminal').setLevel(log_level)
    logging.getLogger('subliminal.api').addHandler(handler)
    logging.getLogger('subliminal.api').setLevel(log_level)


def main(mypath):
    ui = Console_ui(Browser())
    ui.event_loop()

utils.subliminal_cache()
logging_init(logging.INFO)
logger = logging.getLogger(__name__)
main(".")
