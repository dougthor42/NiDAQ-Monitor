# -*- coding: utf-8 -*-
"""
@name:          new_program.py
@vers:          0.1.0
@author:        dthor
@created:       Wed Dec 31 09:54:41 2014
@descr:         A new file

Usage:
    new_program.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.
"""

from __future__ import print_function, division#, absolute_import
#from __future__ import unicode_literals
#from docopt import docopt
from configobj import ConfigObj
import os

__author__ = "Douglas Thor"
__version__ = "v0.1.0"


CONFIG_WARN = ("High", "Low", "Email Address")
CONFIG_CRIT = ("High", "Low", "Email Address")
CONFIG_MISC = ("A", "B", "C")

SECTIONS = (("Warning Limits", CONFIG_WARN),
            ("Critical Limits", CONFIG_CRIT),
            ("Misc. Options", CONFIG_MISC),
            )


def read_config_file(fname=None):
    """ Read the configuration file and store things in the dict. """
    if fname is None:
        fname = "config.ini"
    if not os.path.exists(fname):
        # then we create the config file, using our parameters
        print("Config file not found")
        create_config_file(fname)
    else:
        # read from the config file
        print("Config file found!")
        pass
#        config = ConfigObj(fname)


def create_config_file(fname):
    """ Creates the configuration file if it doesn't already exist """
    print("Creating config file")
    config = ConfigObj()
    config.filename = fname

    for sect_name, items in SECTIONS:
        config[sect_name] = {}
        for item in items:
            config[sect_name][item] = ""
    config.write()


def update_config_file(fname, config):
    """ Update the config file with new values """
    pass


def main():
    """ Main Code """
#    docopt(__doc__, version=__version__)


if __name__ == "__main__":
    main()
