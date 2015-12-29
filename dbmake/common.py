
ZERO_MIGRATION_NAME = "initial_migration"
ZERO_MIGRATION_FILE_NAME = "0_" + ZERO_MIGRATION_NAME + ".sql"
DBMAKE_CONFIG_DIR = ".dbmake"
DBMAKE_CONFIG_FILE = "databases.json"
MIGRATIONS_TABLE = "_dbmake_migrations"
DOCUMENTATION_DIR = "doc"
DBMAKE_VERSION = 'dbmake 0.1.2'

FAILURE = 1
SUCCESS = 0


class DbmakeException(Exception):
    pass


class BadCommandArguments(DbmakeException):
    pass


class CommandNotExists(DbmakeException):
    pass
