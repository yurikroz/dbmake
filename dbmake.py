#!/usr/bin/python

"""
@author: Yuri Kroz
Created on Jan 14, 2015
"""
__author__ = 'splanger'

import sys
import dbmake_cli


def main(args):
    options = dbmake_cli.Options(args)

    if options.print_help is True:
        dbmake_cli.print_help(True)

    #if options.action == 'db:init':


    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
