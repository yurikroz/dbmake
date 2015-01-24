__author__ = 'splanger'

import psycopg2
from dbmake_cli import Options


class TaskBase:
    def __init__(self, options):
        """
        :type options: Options
        """
        self.options = options

        """if options.makefile is not None:
            makefile = options.makefile
        else:
            makefile = os.path.join(os.getcwd(), 'dbmake.yml')
        self.config = DbConfig(makefile)"""


class DbInit(TaskBase):
    """
    Initializes dbmake subsystem for a database according to specified options
    """
    def __init__(self, options):
        TaskBase.__init__(self, options)

    # ----------------------------------------------------------
    def execute(self):
        """
        Create new empty database and initializes migration subsystem.
        Attempts tp drop existing database if drop_existing=True
        """
        logging.info("db:create BEGIN")
        dbs = self.config.databases()
        if dbs is None:
            raise DbmakeException("Invalid dbmake file format. Please refer documentation")

        # For each DB node create database
        # uniq_hosts = set([x['hostname'] for x in self.config.db_nodes()])
        for d in dbs:
            try:
                dba1 = PgAdapter(d['host'], "postgres", d['user'], d['password'])
                if self.options.drop_existing is True:
                    self._drop_db(dba1, d['name'])
                self._create_db(dba1, d['name'])

                dba2 = PgAdapter(d['host'], d['name'], d['user'], d['password'])
                self._init_migrations(dba2)
                logging.info('')
            except:
                exc_info = sys.exc_info()
                logging.error("%s: %s" % (exc_info[0], exc_info[1]) )
                print "Please fix error and try again"
                traceback.print_exc()
                sys.exit(1)

        logging.info("db:create FINISH\n")

    # ----------------------------------------------------------
    def _isDbInitialized(self):
        # Define our connection string
        conn_string = "host='54.68.72.64' dbname='testdb' user='splanger' password='dd123a1a2'"

        # Connect to an existing database
        conn = psycopg2.connect(conn_string)

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute a command: this creates a new table
        # cur.execute("SELECT * FROM tabledb;")

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        # cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))

        # Query the database and obtain data as Python objects
        # >>> cur.execute("SELECT * FROM test;")
        # >>> cur.fetchone()
        # (1, 100, "abc'def")
        cur.execute("SELECT * FROM td_customers")
        result = cur.fetchone()
        print result

        # Make the changes to the database persistent
        conn.commit()

        # Close communication with the database
        cur.close()
        conn.close()

