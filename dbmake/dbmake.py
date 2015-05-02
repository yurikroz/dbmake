#!/usr/bin/python

import sys
from common import FAILURE, SUCCESS
from dbmake_cli import get_command, print_help
from helper import get_class, underscore_to_camelcase
from common import CommandNotExists, BadCommandArguments, DBMAKE_VERSION


class App:

    @staticmethod
    def run(args=[]):

        # Pop the script's name from arguments and fetch the command name
        try:
            args.pop(0)
            command_name = args.pop(0)
        except IndexError:
            print_help()
            return FAILURE

        # Print help if necessary
        if command_name == '-h' or command_name == '--help':
            if args.__len__() > 0:
                command_name = args.pop(0)
                command_name = underscore_to_camelcase(command_name)
                try:
                    command_class = get_class("commands." + command_name)
                    command_class.print_help()
                except AttributeError:
                    print "Error! No such a command %s" % command_name
                    print_help()
                    return FAILURE
                return SUCCESS
            else:
                print_help()
                return SUCCESS
        elif command_name == '-v' or command_name == '--version':
            print DBMAKE_VERSION
            return SUCCESS

        # Get a command instance to execute and execute it
        try:
            command = get_command(command_name, args)
            result = command.execute()
        except CommandNotExists:
            print_help()
            return FAILURE
        except BadCommandArguments:
            return FAILURE

        return result


if __name__ == "__main__":
    sys.exit(App.run(sys.argv))