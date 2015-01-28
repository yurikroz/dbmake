#!/usr/bin/python

"""
@author: Yuri Kroz
Created on Jan 14, 2015
"""
__author__ = 'splanger'

import sys
import logging
import dbmake_cli
from dbmake_tasks import TasksFactory,DbmakeException


def main(args):
    options = dbmake_cli.Options(args)

    print "Running dbmake with options: " + options.__repr__() + "\n"

    if options.print_help is True:
        dbmake_cli.print_help(True)

    # Try to create and execute a task
    try:
        db_task = TasksFactory.create_task(options)
        db_task.execute()
    except DbmakeException as e:
        msg = e.message.decode()
        print msg
        exit(1)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
