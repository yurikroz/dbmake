import logging
import sys
import os
import traceback
import psycopg2
from common import DbmakeException, MIGRATIONS_TABLE, SUCCESS, FAILURE
from database import DbConnectionConfig, DbAdapterFactory, DbType
import migrations


class BaseDbTask:
    """
    Base class for all dbmake database tasks
    """
    db_adapter = None
    db_connection_config = None

    def __init__(self, db_connection_config, db_adapter=None):
        """
        :type db_connection_config: DbConnectionConfig
        :type db_adapter:
        """
        self.db_connection_config = db_connection_config

        if db_adapter is None:
            self.db_adapter = DbAdapterFactory.create(db_connection_config)
        else:
            self.db_adapter = db_adapter

    def execute(self, *arguments, **keywords):
        raise NotImplementedError


class DbTaskType:
    """
    Lists all database tasks types that DbTasks factory must support
    """
    INIT = "init"
    DUMP_ZERO_MIGRATION = "dump_zero_migration"


class BaseDbTasksFactory:
    """
    A base database tasks factory, produces database tasks instances
    """
    def __init__(self):
        pass

    @classmethod
    def create(cls, task_name, db_connection_config, db_adapter=None):
        raise NotImplementedError


class AbstractDbTasksFactory:
    """
    Abstract factory to create DbTasksFactories depending on Database System type (MySQL, PostgreSQL, etc.)
    """

    def __init__(self):
        pass

    @staticmethod
    def create(db_type=DbType.POSTGRES):
        """
        Returns a database tasks factory based on the database's type
        """
        if db_type == DbType.POSTGRES:
            return PgDbTasksFactory


class PgDbTasksFactory(BaseDbTasksFactory):
    """
    A database tasks factory, produces PostgreSQL database tasks instances
    """
    def __init__(self):
        pass

    @classmethod
    def create(cls, task_name, db_connection_config, db_adapter=None):

        if task_name == DbTaskType.INIT:
            return PgDbInit(db_connection_config, db_adapter)
        elif task_name == DbTaskType.DUMP_ZERO_MIGRATION:
            return PgDbDumpZeroMigration(db_connection_config, db_adapter)
        else:
            raise DbmakeException('Unknown task name "' + task_name + '"')


class PgDbInit(BaseDbTask):

    def __init__(self, db_connection_config, db_adapter=None):
        """
        :param db_connection_config: DbConnectionConfig
        """
        BaseDbTask.__init__(self, db_connection_config, db_adapter)

    def execute(self):
        """
        Initiates dbmake necessary table/s within a PostgreSQL database
        """
        print "PgDbInit START"

        def _create_migrations_table(db_adapter):
            query = """
            CREATE TABLE %s (
                id SERIAL,
                revision integer NOT NULL,
                migration_name character varying(100),
                create_date TIMESTAMP DEFAULT NOW() NOT NULL
            )
            """ % MIGRATIONS_TABLE
            self.db_adapter.execute_string(query)

        migrations_dao = migrations.MigrationsDao(self.db_adapter)

        if migrations_dao.is_migration_table_exists() is True:
            print "Error! Migrations table is already exists"
            print "DbInit FINISH"
            return False

        print "Creating migrations table"
        _create_migrations_table(self.db_adapter)
        print "PgDbInit FINISH"

        return True


class PgDbDumpZeroMigration(BaseDbTask):

    def __init__(self, db_connection_config, db_adapter=None):
        """
        :param db_connection_config: DbConnectionConfig
        """
        BaseDbTask.__init__(self, db_connection_config, db_adapter)

    def execute(self, zero_migration_file):
        """
        Initiates dbmake necessary table/s within a PostgreSQL database
        """
        print "PgDbDumpZeroMigration START"

        # Dump initial database structure into ZERO-MIGRATION (initial migration) file
        result = os.system(
            'PGPASSWORD="%s" pg_dump --username=%s --host=%s --schema-only --no-privileges --encoding=LATIN1 '
            '--dbname=%s --port=%s --file=%s' % (
                self.db_connection_config.password,
                self.db_connection_config.user,
                self.db_connection_config.host,
                self.db_connection_config.dbname,
                self.db_connection_config.port,
                zero_migration_file
            )
        )

        print "PgDbDumpZeroMigration FINISH"

        if result == FAILURE:
            return False

        return True


class DbForget(BaseDbTask):
    """
    Makes dbmake.sh to remove its subsystem from specified database
    """
    MIGRATIONS_TABLE_NAME = "_dbmake_migrations"

    def __init__(self, options, dbconnection=None):
        BaseDbTask.__init__(self, options)

        if dbconnection is None:
            # Initialize database connection
            conn_string = "host='" + options.db_host + "' dbname='" + options.db_name + "' user='" + \
                          options.db_user + "' password='" + options.db_password + "'"

            # Connect to database
            try:
                dbconnection = psycopg2.connect(conn_string)
            except psycopg2.ProgrammingError as e:
                msg = e.message.decode()
                print "Failed to connect to database server with specified parameters.\n"
                sys.exit(1)

        self.dbconnection = dbconnection

    def execute(self):
        """
        Initializes migration subsystem in specified database.
        """
        logging.info("db:forget BEGIN")
        print "db:forget BEGIN"

        def _drop_migrations_table(dbconnection):
            query = "DROP TABLE %s " % self.MIGRATIONS_TABLE_NAME
            cur = dbconnection.cursor()
            cur.execute(query)
            dbconnection.commit()

        if self._is_db_initialized() is True:
            logging.info("- Going to drop migrations table")
            print "- Going to drop migrations table"
            _drop_migrations_table(self.dbconnection)
        else:
            logging.info("- Database is not initialized, no need to do anything")
            print "- Database is not initialized, no need to do anything"

        logging.info("db:forget FINISH")
        print "db:forget FINISH"

    def _is_db_initialized(self):
        """
        Checks if the database is already initialized

        :returns Boolean
        """

        cursor = self.dbconnection.cursor()

        query = "SELECT * FROM information_schema.tables " \
                + "WHERE table_name='%s'" % self.MIGRATIONS_TABLE_NAME

        cursor.execute(query)

        if cursor.rowcount == 0:
            return False

        return True


class DbCreate(BaseDbTask):
    """
    Create new empty database and initializes migration subsystem.
    Attempts tp drop existing database if drop_existing=True
    """
    MIGRATION_SEPARATOR = "-- DBMAKE: SEPARATOR"
    MIGRATIONS_TABLE_NAME = "_dbmake_migrations"

    def __init__(self, options, dbconnection=None):
        BaseDbTask.__init__(self, options)

        if dbconnection is None:
            # Initialize database connection
            #
            conn_string = "host='" + options.db_host + "' user='" + options.db_user + "' password='" + options.db_password + "'"
            conn_string += " dbname='" + options.db_user + "'"

            # Connect to database
            try:
                dbconnection = psycopg2.connect(conn_string)
            except psycopg2.ProgrammingError as e:
                msg = e.message.decode()
                print "Failed to connect to database server with specified parameters.\n"
                sys.exit(1)

        self.dbconnection = dbconnection

    def execute(self):
        # Read migrations directory:
        print os.getcwd()
        #print os.path.dirname(os.path.abspath(__file__))

        migrations_files = []
        for file_name in os.listdir(os.getcwd()):
            if file_name.endswith(".sql"):
                file_name_parts = file_name.split('_')
                migrations_files.append((file_name_parts[1], file_name))

        if migrations_files.__len__() > 0:
            # Sort migration files by version (timestamp - in the future)
            migrations_files = sorted(migrations_files, key=lambda migration_file: migration_file[0])
            #migration_files = migration_files.sort()
            print "Found next migrations file in current working directory:"
            print migrations_files
        else:
            print "Didn't find any migrations in current working directory"
            sys.exit(1)

        logging.info("db:create BEGIN")
        print "db:create BEGIN"

        # For each DB node create database
        # uniq_hosts = set([x['hostname'] for x in self.config.db_nodes()])
        try:
            self.dbconnection.set_isolation_level(0)
            if self.options.drop_existing is True:
                self._drop_db()
            self._create_db()

            # Now let's disconnect from the DBA's default database and connect to the newly created database
            self.dbconnection.close()
            conn_string = "host='" + self.options.db_host + "' user='" + self.options.db_user + \
                          "' password='" + self.options.db_password + "'" + " dbname='" + self.options.db_name + "'"
            # Connect to database
            try:
                self.dbconnection = psycopg2.connect(conn_string)
            except psycopg2.ProgrammingError as e:
                msg = e.message.decode()
                print "Failed to connect to newly created database"
                sys.exit(1)

            self._init_migrations(migrations_files)
        except:
            exc_info = sys.exc_info()
            logging.error("%s: %s" % (exc_info[0], exc_info[1]) )
            print "Please fix error and try again"
            traceback.print_exc()
            sys.exit(1)

        logging.info("db:create FINISH")
        print "db:create FINISH"

    # ----------------------------------------------------------
    def _create_db(self):
        logging.info("Creating database %s at %s" % (self.options.db_name, self.options.db_host))
        print "Creating database %s at %s" % (self.options.db_name, self.options.db_host)

        cursor = self.dbconnection.cursor()
        cursor.execute("create database %s;" % self.options.db_name)
        self.dbconnection.commit()

    # ----------------------------------------------------------
    def _drop_db(self):
        logging.info("Dropping database %s at %s" % (self.options.db_name, self.options.db_host))
        print "Dropping database %s at %s" % (self.options.db_name, self.options.db_host)

        cursor = self.dbconnection.cursor()
        cursor.execute("drop database %s;" % self.options.db_name)
        self.dbconnection.commit()

    def _init_migrations(self, migrations_files):
        cursor = self.dbconnection.cursor()

        query = """
            CREATE TABLE %s (
                id      SERIAL,
                version INTEGER NOT NULL,
                file    character varying(100),
                create_date TIMESTAMP DEFAULT NOW() NOT NULL
            )
            """ % self.MIGRATIONS_TABLE_NAME

        cursor = self.dbconnection.cursor()
        cursor.execute(query)
        self.dbconnection.commit()

        for migration_file_tuple in migrations_files:
            # Get migration file contents
            migration_file = migration_file_tuple[1]
            f = open(migration_file, 'r')
            query = f.read()

            print query

            # Now let's separate UP migration from DOWN migration statements...
            query = query.split(self.MIGRATION_SEPARATOR)[0]

            print "THis is MIGRATION UP:"
            print query

            # Migrate...
            print "Performing migration to version: " + migration_file_tuple[0]

            cursor.execute(query)
            self.dbconnection.commit()

            # Now let's add a new entry into migrations table
            query = "INSERT INTO " + self.MIGRATIONS_TABLE_NAME + " (version, file) VALUES ('" + migration_file_tuple[0] + "', '" + migration_file_tuple[1] + "')"
            cursor.execute(query)
            self.dbconnection.commit()

            #exit(1)


        self.dbconnection.commit()


class DbMigrate(BaseDbTask):
    def execute(self):
        pass

