#!/usr/bin/python

"""
The purpose of this module is to parse user commands passed to "dbmake".
Also the module contains the HELP string describes how to use the utility.
"""

import helper
from common import BadCommandArguments, CommandNotExists


def get_command(command_name, args=[]):
    """
    Returns Application command instance corresponding to a passed command_name.

    :param str command_name: Command name as it has been parsed from sys.argv
    """

    command_name = helper.underscore_to_camelcase(command_name)

    try:
        command_class = helper.get_class("commands." + command_name)
    except AttributeError:
        raise CommandNotExists

    try:
        command_instance = command_class(args)
    except BadCommandArguments:
        command_class.print_help()
        raise BadCommandArguments

    return command_instance


def print_help():
    print """
    dbmake - Database Schema Migration Tool

    usage: dbmake <command> [options]
       or: dbmake (-h | --help) [<command name>]

    Commands:
         init               Initializes migration subsystem for already existing database
         forget             Removes dbmake tables from database and removes its connection from databases list
         create             Creates new empty database(s) and initializes migrations subsystem.
         migrate            Update DB schema using migration files to specified version (with option: VERSION=x)
         reset              This will drop the database, recreate it and load the current schema into it.
         rollback           Rolls the schema back to the previous version (it is possible to specify the number of rollback steps w/ STEP=n)
         status             Display status of migrations
         version            Retrieves the current schema version number
         generate_doc       Generates database documentation based on documentation in migration files.
         generate_migration Generates a new template migration file.
    """