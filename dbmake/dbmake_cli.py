#!/usr/bin/python

"""
The purpose of this module is to parse user commands passed to "dbmake".
Also the module contains the HELP string describes how to use the utility.
"""

import helper
from common import BadCommandArguments, CommandNotExists


def command_to_class_name(command_name):
    """
    Gets a command name and returns it's class name
    :param command_name:
    :return: str
    """
    class_name = helper.camelcase(command_name, "_")
    class_name = helper.camelcase(class_name, "-")

    return class_name


def get_command(command_name, args=[]):
    """
    Returns Application command instance corresponding to a passed command_name.

    :param str command_name: Command name as it has been parsed from sys.argv
    """

    command_name = command_to_class_name(command_name)

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
       or: dbmake (-v | --version)

    Commands:
         init               Add new database connection details and initialize migrations subsystem.
         status             Show database(s) schema revisions.
         migrate            Update database(s) structure using migration files
         rollback           Roll back database(s) schema(s) to a previous revision. (same as: migrate --down 1)
         forget             Drop migrations table in database and remove its connection details from connections list.
         create             Create a new empty database and initializes migrations subsystem in it.
         reset              Drop a database, recreate it and load the recent schema revision into it.
         new-migration      Create a new migration file
         doc-generate       Generate a database documentation
    """