
ZERO_MIGRATION_NAME = "0_initial_migration.sql"
DBMAKE_CONFIG_DIR = ".dbmake"
DBMAKE_CONFIG_FILE = "databases.json"
MIGRATIONS_TABLE_NAME = "_dbmake_migrations"

FAILURE = 1
SUCCESS = 0


class BadCommandArguments(BaseException):
    pass


class CommandNotExists(BaseException):
    pass