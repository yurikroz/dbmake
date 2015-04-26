
import psycopg2
import psycopg2.extras
import copy
import os
import json


class DbConnectionConfig:

    host = None
    user = None
    port = "5432"
    dbname = None
    password = None
    connection_name = None

    def __init__(self, host, dbname, user, password, connection_name, port="5432"):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.connection_name = connection_name

    def save(self, config_file, connection_to_update=None):
        """
        Adds current connection in a config_file.
        :param config_file: str
        :param connection_to_update: Name of a connection in config file you want to update its details
        """

        # Convert configuration instance into a string
        connections_list = [self]
        config_string = json.dumps(connections_list, default=lambda o: o.__dict__, sort_keys=True, indent=4)

        print "Check if dbmake config file exists... ",

        if not os.path.exists(config_file):
            print "Not exists"

            # Create dbmake configuration file
            try:
                print "Create config file... ",
                f = open(config_file, 'w+')
                print "OK"
            except IOError as e:
                msg = e.message()
                print "Failure"
                print msg
                return False

            f.write(config_string)
            f.close()
        else:
            print "Exists"
            try:
                f = open(config_file, 'r')
            except IOError as e:
                msg = e.message()
                print "Failure"
                print msg
                return False
            connections_list = json.load(f)
            f.close()

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
                msg = e.message()
                print "Failure"
                print msg
                return False

            connections_list.append(self)
            config_string = json.dumps(connections_list, default=lambda o: o.__dict__, sort_keys=True, indent=4)
            f.write(config_string)
            f.close()

            print "OK"

        return True

    @staticmethod
    def delete(config_file, connection_name):
        """
        Deletes a connection details from a config_file

        :param config_file: str
        :param connection_name: str
        """
        # TODO: Implement


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

    def get_cursor(self):
        raise NotImplementedError


class PgAdapter(BaseDbAdapter):
    """
    Wrapper adapter for PostgreSQL
    """

    def __init__(self, db_connection_config):
        BaseDbAdapter.__init__(self, db_connection_config)
        self._connect()

    def _connect(self):
        # Initialize database connection
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
            self._db_connection_config.host,
            self._db_connection_config.dbname,
            self._db_connection_config.user,
            self._db_connection_config.password
        )
        self._connection = psycopg2.connect(conn_string)

    def query(self, sql_string, cursor_factory=None):
        cur = self.get_cursor(cursor_factory)
        cur.execute(sql_string)
        return cur

    def execute_string(self, sql_string, cursor_factory=None):
        cur = self.get_cursor(cursor_factory)
        cur.execute(sql_string)
        self._connection.commit()

    def fetch_dict(self, sql_string):
        """
        Executes an SQL string and returns the result as a list of dictionary
        instances representing records
        :param sql_string: str
        """
        cur = self.query(sql_string, cursor_factory=psycopg2.extras.DictCursor)
        result = cur.fetchall()
        records = []
        for row in result:
            records.append(dict(row))
        return records

    def get_cursor(self, cur_factory=None):
        if cur_factory is None:
            return self._connection.cursor()
        else:
            return self._connection.cursor(cursor_factory=cur_factory)

    def get_tables(self):
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_type='BASE TABLE'
        """
        return self.fetch_dict(query)