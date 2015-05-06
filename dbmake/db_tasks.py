import logging
import sys
import os
import traceback
import psycopg2
from common import DbmakeException, MIGRATIONS_TABLE, SUCCESS, FAILURE
from database import DbConnectionConfig, DbAdapterFactory, DbType
import migrations
from doc_generator import DbSchemaType, DocGenerator, TableType, ColumnType


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
    CREATE = "create"
    DUMP_ZERO_MIGRATION = "dump_zero_migration"
    DOC_GENERATE = "doc_generate"


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
        :return: BaseDbTasksFactory
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
        elif task_name == DbTaskType.CREATE:
            return PgDbCreate(db_connection_config, db_adapter)
        elif task_name == DbTaskType.DOC_GENERATE:
            return PgDbDocGenerate(db_connection_config, db_adapter)
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


class PgDbCreate(BaseDbTask):
    """
    Create new empty database and initializes migration subsystem.
    """

    def __init__(self, db_connection_config, db_adapter=None):
        BaseDbTask.__init__(self, db_connection_config, db_adapter)

    def execute(self, dbname, drop_existing=False):

        print self.__class__.__name__ + " BEGIN"

        self.db_adapter.set_isolation_level(0)

        if drop_existing:
            try:
                self._drop_db(dbname)
            except psycopg2.ProgrammingError as e:
                print e.message.decode()
                return False

        try:
            self._create_db(dbname)
        except psycopg2.ProgrammingError as e:
            print e.message.decode()
            return False

        print self.__class__.__name__ + " FINISH"

        return True

    # ----------------------------------------------------------
    def _create_db(self, dbname):
        print "Creating database %s" % dbname
        cursor = self.db_adapter.get_cursor()
        cursor.execute("CREATE DATABASE %s;" % dbname)
        self.db_adapter.commit()

    # ----------------------------------------------------------
    def _drop_db(self, dbname):
        print "Dropping database %s" % dbname
        cursor = self.db_adapter.get_cursor()
        cursor.execute("DROP DATABASE %s;" % dbname)
        self.db_adapter.commit()


class PgDbDocGenerate(BaseDbTask):
    """
    Generates database documentation.
    """

    def __init__(self, db_connection_config, db_adapter=None):
        BaseDbTask.__init__(self, db_connection_config, db_adapter)

    def execute(self, dbname, revision):
        """
        Generates database documentation with a specified doc_generator_. If the latter is not specified
        then will use a default generator.
        """
        import sys
        print self.__class__.__name__ + " BEGIN"

        db_schema = self._db_schema(dbname, revision)
        doc_generator_ = DocGenerator(db_schema)
        html = doc_generator_.generate()

        print self.__class__.__name__ + " FINISH"

        return html

    def _db_schema(self, dbname, revision):
        """
        Assembles database schema structure as doc_generator.DbSchemaType class
        :return: DbSchemaType
        """

        def _columns(dbname_, table, db_adapter, schema='public'):
            """
            Returns a list of table's columns

            :param table: TableType
            :param db_adapter:
            """
            query_table_columns_with_descriptions = """
            SELECT
                cols.column_name,
                cols.data_type,
                (
                    SELECT
                        pg_catalog.col_description(c.oid, cols.ordinal_position::int)
                    FROM
                        pg_catalog.pg_class c
                    WHERE
                        c.oid = (SELECT '{table_name}'::regclass::oid) AND
                        c.relname = cols.table_name
                ) as column_comment

            FROM
                information_schema.columns cols
            WHERE
                cols.table_catalog = '{dbname}' AND
                cols.table_name    = '{table_name}'    AND
                cols.table_schema  = '{schema_name}';
            """.format(table_name=table.name, dbname=dbname_, schema_name=schema)

            result = db_adapter.fetch_dict(query_table_columns_with_descriptions)

            columns = []
            for column_ in result:
                column = ColumnType()
                column.name = column_['column_name']
                column.data_type = column_['data_type']
                column.comment = column_['column_comment']
                columns.append(column)

            return columns

        def _tables(dbname_, db_adapter, schema='public'):
            """
            Returns a list of schema tables
            """
            query_tables_with_descriptions = """
            SELECT table_name, pg_catalog.obj_description(('public.'||table_name)::regclass::oid) AS description
              FROM information_schema.tables
              WHERE table_schema='%s'
            """ % schema

            result = db_adapter.fetch_dict(query_tables_with_descriptions)

            tables = []
            for table_ in result:
                table = TableType()
                table.name = table_['table_name']
                table.comment = table_['description']
                table.columns = _columns(dbname_, table, db_adapter)
                tables.append(table)

            return tables

        # Create schema instance
        db_schema = DbSchemaType()
        db_schema.dbname = dbname
        db_schema.revision = revision

        # Get tables list
        db_schema.tables = _tables(dbname, self.db_adapter)

        return db_schema