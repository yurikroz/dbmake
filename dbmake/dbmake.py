#!/usr/bin/python

import sys
from common import FAILURE, SUCCESS
from dbmake_cli import get_command, print_help, get_command_class_reference
from common import CommandNotExists, BadCommandArguments, DBMAKE_VERSION


class App:

    def __init__(self):
        self.ide_stop_bothering_with_static_method = "!!!"

    def run(self, args=sys.argv):
        self.ide_stop_bothering_with_static_method = "!!!"

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
                try:
                    command_class = get_command_class_reference(command_name)
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
            print "Unrecognized command!"
            print_help()
            return FAILURE
        except BadCommandArguments:
            print "Bad command arguments"
            return FAILURE

        return result


def main(argv=sys.argv):
    app = App()
    sys.exit(app.run(argv))

if __name__ == "__main__":
    sys.exit(main(sys.argv))

