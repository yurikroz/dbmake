"""
The purpose of this module is to parse user commands passed to "dbmake".
Also the module contains the HELP string describes how to use the utility.
"""
__author__ = 'splanger'

HELP_STRING = """
dbmake - database management utility

Usage:
    dbmake [options] [action]

Options:
     -h, --help                   Prints this help dialog
     -m, --schema-migrations-dir  Schema migration directory (optional). The working directory will be used by default.

     -H, --host         Database server host
     -U, --username     Username to connect with to a database
     -W, --password     Password to a database for a given username
     -d, --dbname       Database name to connect to

Action:
     db:init             Initializes migration subsystem for an already existing database
     db:create           Create new empty database(s) and initializes migrations subsystem.
                         Use additional option --drop-existing to drop current database if exists
     db:migrate          Update DB schema using migration files (options: VERSION=x)
     db:reset            This will drop the database, recreate it and load the current schema into it.
     db:rollback         Rolls the schema back to the previous version (specify steps w/ STEP=n)
     db:migrate:status   Display status of migrations
     db:version          Retrieves the current schema version number
"""

import sys


class Options:
    """
    The class represents options passed via command line
    """
    db_host = None
    db_user = None
    db_password = None
    db_name = None
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

                elif (args[0] == '-W' or args[0] == '--password') and len(args) >= 2:
                    args.pop(0)
                    self.db_password = args.pop(0)

                elif args[0].startswith('--password='):
                    self.db_password = args[0].split('=')[1]
                    args.pop(0)

                elif (args[0] == '-d' or args[0] == '--dbname') and len(args) >= 2:
                    args.pop(0)
                    self.db_name = args.pop(0)

                elif args[0].startswith('--dbname='):
                    self.db_name = args[0].split('=')[1]
                    args.pop(0)

                # Action
                elif args[0] == 'db:init':
                    self.action = args.pop(0)
                    """if (len(args)>0) and (not args[0].startswith('-')):
                        options.migration_ver = args.pop(0)
                    else:
                        options.migration_ver = '99999999_0'"""

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

