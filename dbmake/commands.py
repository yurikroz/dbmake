
import sys
import os
import getpass
import psycopg2
import database
from common import BadCommandArguments, FAILURE, SUCCESS, DBMAKE_CONFIG_DIR, DBMAKE_CONFIG_FILE, ZERO_MIGRATION_NAME


class BaseCommand:
    """
    A base class for all application's command line commands
    """

    def __init__(self, args=[]):
        """
        :param args: a list of applications command line arguments
        """
        self._parse_options(args)

    def print_help(self):
        raise NotImplementedError

    def execute(self):
        """
        Execute command
        """
        raise NotImplementedError

    def _parse_options(self, args=[]):
        """
        Parses all command options from command line arguments
        """
        raise NotImplementedError


class Init(BaseCommand):

    db_host = None
    db_user = None
    db_port = None
    db_pass = None
    db_name = None
    connection_name = None
    db_connection_config = None
    migrations_dir = None
    drop_existing = False

    def __init__(self, args=[]):
        BaseCommand.__init__(self, args)

    def execute(self):

        if self.db_pass is None:
            self.db_pass = getpass.getpass("Enter database password: ")

        self.db_connection_config = database.DbConnectionConfig(
            self.db_host,
            self.db_name,
            self.db_user,
            self.db_pass,
            self.connection_name
        )

        # Check connection parameters by establishing a connection to db
        try:
           db_adapter = database.PgAdapter(self.db_connection_config)
        except psycopg2.OperationalError as e:
            print "Failed to connect to a database server with specified parameters."
            print e.message.decode()
            return FAILURE

        # Create .dbmake directory if it doesn't exist
        result = self._create_config_dir()

        if result is False:
            return FAILURE

        # Save connection configuration (also creates config file if it doesn't exist)
        dbmake_config_file = str(self.migrations_dir) + "/" + DBMAKE_CONFIG_DIR + "/" + DBMAKE_CONFIG_FILE
        result = self.db_connection_config.save(dbmake_config_file)

        if result is False:
            return FAILURE

        # Now let's check if Zero-Migration exists and if true, check whether database is empty
        # If Zero-Migration doesn't exist, generate it out of database's current structure,
        # If it does exist, check whether the database is empty, if it is not then return FAILURE

        zero_migration_file = self.migrations_dir + "/" + ZERO_MIGRATION_NAME
        if not os.path.exists(zero_migration_file):
            # Dump initial database structure into ZERO-MIGRATION (initial migration) file
            result = os.system(
                'PGPASSWORD="%s" pg_dump -U %s -h %s -s -x -c -E LATIN1 -c -d %s -p %s -f %s' % (
                    self.db_connection_config.password,
                    self.db_connection_config.user,
                    self.db_connection_config.host,
                    self.db_connection_config.dbname,
                    self.db_connection_config.port,
                    zero_migration_file
                )
            )

            if result != SUCCESS:
                print "Failed to dump database schema into ZERO-MIGRATION file."
                return FAILURE
        else:
            try:
                schema_table_list = db_adapter.get_tables()
            except psycopg2.Error as e:
                print e.message.decode()
                return FAILURE

            if len(schema_table_list) > 0:
                print "Error! Database is not empty while ZERO-MIGRATION file exists."
                return FAILURE

        return SUCCESS

    def _create_config_dir(self):
        """
        Creates a dbmake config directory within migrations folder if it yet doesn't exist.
        :return: Returns True on success, otherwise returns False
        """
        if self.migrations_dir is None:
            self.migrations_dir = os.path.abspath(os.getcwd())

        print "Check if .dbmake directory does not exist in: %s ..." % self.migrations_dir,

        dbmake_config_dir = str(self.migrations_dir) + "/" + DBMAKE_CONFIG_DIR
        if not os.path.exists(dbmake_config_dir):
            print "Not exists"
            try:
                print "Create .dbmake directory... ",
                os.makedirs(dbmake_config_dir)
                print "OK"
            except OSError as e:
                msg = e.message()
                print "Failure"
                print msg
                return False
        else:
            print "Exists"

        return True

    @staticmethod
    def print_help():
        # --no-dump               Don't dump database structure into ZERO MIGRATION file
        print """
        usage: dbmake init [(-m | --migrations-dir) <path>] <connection name> (options) [OPTIONAL]

        Note:
        <connection name> is used to refer to database connection parameters.

        Optional:
            -m, --migrations-dir    Where migrations reside
            -p, --port              Database server port
            -P, --password          Database username password

        Required options:
            -h, --host      Database server host
            -d, --dbname    Database name
            -u, --user      Database username
        """

    def _parse_options(self, args):
        if len(args) == 0:
            raise BadCommandArguments

        # Parse optional [(-m | --migrations-dir) <path>]
        if args[0] == '-m' or args[0] == '--migrations-dir':
            if len(args) < 2:
                raise BadCommandArguments
            args.pop(0)
            self.migrations_dir = args.pop(0)

        elif args[0].startswith("--migrations-dir="):
            self.migrations_dir = args[0].split('=')[1]
            args.pop(0)

        # Parse required <connection name>
        if len(args) == 0:
            raise BadCommandArguments
        else:
            self.connection_name = args.pop(0)

        # Parse all the remaining necessary options
        while len(args) > 0:

            # Parse (-h, --host) option
            if (args[0] == '-h' or args[0] == '--host') and len(args) >= 2:
                args.pop(0)
                self.db_host = args.pop(0)

            elif args[0].startswith('--host='):
                self.db_host = args[0].split('=')[1]
                args.pop(0)

            # Parse (-u, --user) option
            elif (args[0] == '-u' or args[0] == '--user') and len(args) >= 2:
                args.pop(0)
                self.db_user = args.pop(0)

            elif args[0].startswith('--user='):
                self.db_user = args[0].split('=')[1]
                args.pop(0)

            # Parse (-d, --dbname) option
            elif (args[0] == '-d' or args[0] == '--dbname') and len(args) >= 2:
                args.pop(0)
                self.db_name = args.pop(0)

            elif args[0].startswith('--dbname='):
                self.db_name = args[0].split('=')[1]
                args.pop(0)

            # Parse [-p, --port] option
            elif (args[0] == '-p' or args[0] == '--port') and len(args) >= 2:
                args.pop(0)
                self.db_port = args.pop(0)

            elif args[0].startswith('--port='):
                self.db_port = args[0].split('=')[1]
                args.pop(0)

            # Parse [-P, --password] option
            elif (args[0] == '-P' or args[0] == '--password') and len(args) >= 2:
                args.pop(0)
                self.db_pass = args.pop(0)

            elif args[0].startswith('--password='):
                self.db_pass = args[0].split('=')[1]
                args.pop(0)

            # Prevent infinite loop caused by wrong arguments
            else:
                args.pop(0)

        print self.__repr__()

        # Create DbConnectionConfig from parsed arguments
        if (
            self.db_host is None
            or self.db_name is None
            or self.db_user is None
            or self.connection_name is None
        ):
            raise BadCommandArguments

    def __repr__(self):
        return "dbhost=%s, dbuser=%s dbname=%s dbpass=%s, conn_name=%s" % (
            self.db_host, self.db_user, self.db_name, self.db_pass, self.connection_name
        )