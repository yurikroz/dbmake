
import psycopg2
import psycopg2.extras
import copy
import os
import json


class DbType:
    MY_SQL = "mysql"
    ORACLE = "oracle"
    POSTGRES = "pgsql"

    def __init__(self):
        pass


class DbConnectionConfig:

    host = None
    user = None
    port = "5432"
    dbname = None
    password = None
    connection_name = None
    # db_type = DbType.POSTGRES

    def __init__(self, host, dbname, user, password, connection_name, port="5432", db_type=DbType.POSTGRES):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.connection_name = connection_name
        # self.db_type = db_type

    def save(self, config_file):
        """
        Adds current connection in a config_file.
        :param config_file: str A full path to a config file
        """

        def create_config_file(file_, content_):
            print "Create config file... ",
            try:
                f_ = open(file_, 'w+')
            except IOError as e_:
                print "Failure"
                print e_.message.decode()
                return False
            else:
                with f_:
                    f_.write(content_)

        # Convert configuration instance into a string
        connections_list = [self]
        config_string = json.dumps(connections_list, default=lambda o: o.__dict__, sort_keys=True, indent=4)

        print "Check if dbmake config file exists... ",

        if not os.path.exists(config_file):
            # Create dbmake configuration file if such not exists
            print "Not exists"
            create_config_file(config_file, config_string)

        else:
            print "Exists"
            connections_list = self.connections_list(config_file)

            print "Check if such connection is already exists... ",

            for connection in connections_list:
                if (
                    connection["connection_name"] == self.connection_name
                    or (
                        connection["host"] == self.host
                        and connection["dbname"] == self.dbname
                    )
                ):
                    print "Connection is already exists."
                    return False

            print "No"
            print "Add new connection to a config file...",

            # Add new connection to a config file
            try:
                f = open(config_file, 'w+')
            except IOError as e:
                print "Failure"
                print e.message.decode()
                return False
            else:
                with f:
                    connections_list.append(self)
                    config_string = json.dumps(connections_list, default=lambda o: o.__dict__, sort_keys=True, indent=4)
                    f.write(config_string)

            print "OK"

        return True

    @classmethod
    def delete(cls, config_file, connection_name):
        """
        Deletes a connection details from a config_file

        :param config_file: str
        :param connection_name: str
        """
        connections_list = cls.connections_list(config_file)

        for index, connection in enumerate(connections_list):
            if connection["connection_name"] == connection_name:
                connections_list.pop(index)
                break

        # Add new connection to a config file
        with open(config_file, 'w+') as f:
            config_string = json.dumps(connections_list, default=lambda o: o.__dict__, sort_keys=True, indent=4)
            f.write(config_string)

        return True

    @staticmethod
    def connections_list(config_file):
        """
        Reads a database connections configuration file and returns a list
        of database connections as a list of dictionaries
        :param config_file: A full path to a config file
        :return: List of dictionaries or False on failure
        """
        with open(config_file, 'r') as f:
            connections_list = json.load(f)

        return connections_list

    @staticmethod
    def is_connection_name_exists(config_file, connection_name):
        """
        Reads a database connections configuration file and returns a list
        of database connections as a list of dictionaries
        :param config_file: A full path to a config file
        :return: List of dictionaries or False on failure
        """
        with open(config_file, 'r') as f:
            connections_list = json.load(f)

        for connection in connections_list:
            if connection['connection_name'] == connection_name:
                return True

        return False

    @classmethod
    def read(cls, config_file, connection_name):
        """
        Reads a connection details from a config_file and
        returns them as DbConnectionConfig instance.
        In case of failure returns False

        :param config_file: str
        :param connection_name: str
        """

        # Check if dbmake config file exists...
        connections_list = cls.connections_list(config_file)

        for connection in connections_list:
            if connection["connection_name"] == connection_name:
                return DbConnectionConfig(
                    connection["host"],
                    connection["dbname"],
                    connection["user"],
                    connection["password"],
                    connection["connection_name"],
                    connection["port"]
                )

        return False

    @classmethod
    def read_all(cls, config_file):
        """
        Reads all connections details from a config_file and returns them as a list of DbConnectionConfig
        instances. In case of failure returns False

        :param config_file: str
        """

        # Check if dbmake config file exists...
        if not os.path.exists(config_file):
            return False

        connections_list = cls.connections_list(config_file)

        if connections_list is False:
            return False

        connections_list_instances = []
        for connection in connections_list:
            connections_list_instances.append(DbConnectionConfig(
                connection["host"],
                connection["dbname"],
                connection["user"],
                connection["password"],
                connection["connection_name"],
                connection["port"]
                )
            )

        return connections_list_instances


class BaseDbAdapter:
    """
    :type _db_connection_config: DbConnectionConfig
    """

    _connection = None

    _db_connection_config = None

    def __init__(self, db_connection_config):
        """
        :param DbConnectionConfig db_connection_config: Database connection params
        """
        self._db_connection_config = copy.copy(db_connection_config)

    def _connect(self):
        raise NotImplementedError

    def get_db_connection_config(self):
        """
        :return: DbConnectionConfig
        """
        return copy.copy(self._db_connection_config)

    def query(self, query):
        """
        Executes an SQL query

        :param query: str
        :return Query result
        """
        raise NotImplementedError

    def execute_string(self, sql_string, cursor_factory=None):
        raise NotImplementedError

    def get_cursor(self):
        raise NotImplementedError


class DbAdapterFactory:
    """
    Use this class statically to create database adapters based on db_connection_config
    """
    def __init__(self):
        pass

    @classmethod
    def create(cls, db_connection_config):
        """
        :return: BaseDbAdapter
        """

        # For sake of first project version only PostgreSQL support is provided
        return PgAdapter(db_connection_config)


class PgAdapter(BaseDbAdapter):
    """
    Wrapper adapter for PostgreSQL
    """

    def __init__(self, db_connection_config):
        BaseDbAdapter.__init__(self, db_connection_config)
        self._connect()

    def _connect(self):
        # Initialize database connection
        conn_string = "host='%s' dbname='%s' user='%s' password='%s' connect_timeout='3'" % (
            self._db_connection_config.host,
            self._db_connection_config.dbname,
            self._db_connection_config.user,
            self._db_connection_config.password
        )
        self._connection = psycopg2.connect(conn_string)

    def disconnect(self):
        self._connection.close()

    def query(self, sql_string, cursor_factory=None):
        """
        Executes an SQL query and returns a cursor that a result can be fetched from
        :param sql_string:
        :param cursor_factory:
        :return: Cursor
        """
        cur = self.get_cursor(cursor_factory)
        cur.execute(sql_string)
        return cur

    def execute_string(self, sql_string, cur_factory=None):
        """
        Executes an SQL query and commits it
        :param sql_string:
        :param cur_factory:
        """
        with self._connection.cursor(cursor_factory=cur_factory) as cur:
            cur.execute(sql_string)
            self._connection.commit()

    def commit(self):
        self._connection.commit()

    def fetch_dict(self, sql_string):
        """
        Executes an SQL string and returns the result as a list of dictionary instances,
        each one is representing a record
        :param sql_string: str
        """
        with self._connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql_string)
            result = cur.fetchall()

        records = []
        for row in result:
            records.append(dict(row))

        return records

    def fetch_single_dict(self, sql_string):
        """
        Executes an SQL string and returns tthe only record represented by dictionary
        :param sql_string: str
        """
        with self._connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql_string)
            result = cur.fetchone()

        if result is not None:
            return dict(result)

        return None

    def get_cursor(self, cur_factory=None):
        if cur_factory is None:
            return self._connection.cursor()
        else:
            return self._connection.cursor(cursor_factory=cur_factory)

    def get_tables(self):
        """
        Returns a list of "BASE TABLE"s names in "public" schema of a database that
        the adapter's connection is associated with
        """
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_type='BASE TABLE'
        """
        with self._connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(query)
            result = cur.fetchall()

        records = []
        for row in result:
            records.append(dict(row)["table_name"])

        return records

    def set_isolation_level(self, isolation_level):
        self._connection.set_isolation_level(isolation_level)