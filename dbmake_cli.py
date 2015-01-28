"""
The purpose of this module is to parse user commands passed to "dbmake".
Also the module contains the HELP string describes how to use the utility.
"""
__author__ = 'splanger'

HELP_STRING = """
dbmake - Database Schema Migration Tool

    dbmake [options] [action]

Note: Values for options are passed as follows: -<short option name> <value> or --<long option name>=<value>
Options:
    -h, --help                     Prints the help dialog
    -m, --schema-migrations-dir    Schema migration directory (optional). The working directory will be used by default.
    -c, --config-file              Options file to load
    -H, --host                     Database server host
    -U, --username                 Username to connect with to a database
    -W, --password                 Force password prompt for database connection
    -d, --dbname                   Database name to connect to
    -D, --dry-run                  Dry run (print commands, but do not execute)

Action:
     db:init               Initializes migration subsystem for already existing database
     db:forget             Removes migration subsystem from database
     db:create             Creates new empty database(s) and initializes migrations subsystem.
     db:migrate            Update DB schema using migration files to specified version (with option: VERSION=x)
     db:reset              This will drop the database, recreate it and load the current schema into it.
     db:rollback           Rolls the schema back to the previous version (it is possible to specify the number of rollback steps w/ STEP=n)
     db:migrate:status     Display status of migrations
     db:version            Retrieves the current schema version number
     db:generate:doc       Generates database documentation based on documentation in migration files.
     db:generate:migration Generates a new template migration file.
"""

import sys
import getpass


class Options:
    """
    The class represents options passed via command line
    """
    db_host = None
    db_user = None
    db_password = None
    db_name = None
    drop_existing = False
    migrations_dir = None
    action = None
    print_help = False

    def __init__(self, args=[]):
        """
        Initializes options instance. If args are passed in then it will try to parse them and
        set the fields accordingly.
        """
        if len(args) > 0:
            args.pop(0)
            if len(args) == 0:
                self.print_help = True

            while len(args) > 0:

                # General options
                if args[0] == '-h' or args[0] == '--help':
                    args.pop(0)
                    self.print_help = True
                    break

                # Connection options
                elif (args[0] == '-H' or args[0] == '--host') and len(args) >= 2:
                    args.pop(0)
                    self.db_host = args.pop(0)

                elif args[0].startswith('--host='):
                    self.db_host = args[0].split('=')[1]
                    args.pop(0)

                elif (args[0] == '-U' or args[0] == '--username') and len(args) >= 2:
                    args.pop(0)
                    self.db_user = args.pop(0)

                elif args[0].startswith('--username='):
                    self.db_user = args[0].split('=')[1]
                    args.pop(0)

                elif args[0] == '-W' or args[0] == '--password':
                    args.pop(0)
                    #self.db_password = args.pop(0)
                    self.db_password = getpass.getpass()
                    #print "Entered password: " + self.db_password
                    #sys.exit(0)
                    """
                    elif args[0].startswith('--password='):
                        self.db_password = args[0].split('=')[1]
                        args.pop(0)
                    """

                elif (args[0] == '-d' or args[0] == '--dbname') and len(args) >= 2:
                    args.pop(0)
                    self.db_name = args.pop(0)

                elif args[0].startswith('--dbname='):
                    self.db_name = args[0].split('=')[1]
                    args.pop(0)

                elif args[0] == '--drop-existing':
                    args.pop(0)
                    self.drop_existing = True

                # Action
                elif args[0] == 'db:init' or \
                   args[0] == 'db:forget' or \
                   args[0] == 'db:create' or \
                   args[0] == 'db:migrate':
                    self.action = args.pop(0)

                else:
                    self.print_help = True
                    break

    def __repr__(self):
        return "host=%s, user=%s, password=%s, db_name=%s, migrations_dir=%s, action=%s" % \
               (self.db_host, self.db_user, self.db_password, self.db_name, self.migrations_dir, self.action)


def print_help(exit=True):
    print HELP_STRING
    if exit is True:
        sys.exit(1)

