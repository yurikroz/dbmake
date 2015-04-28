
import common
import database


class Migration:

    name = None
    revision = None
    migrate_up_statements = None
    migrate_down_statements = None

    def init(self, migration_file):
        # TODO: Read a migration file and extract from there "Migrate UP" and "Migrate DOWN" statements
        pass


class MigrationVO:
    """
    Migration ValueObject, represents the dbmake migrations table record
    """
    id_ = None
    revision = None
    create_date = None
    migration_name = None


class MigrationsDao:

    TABLE_NAME = common.MIGRATIONS_TABLE
    db_adapter = None

    def __init__(self, db_adapter):
        self.db_adapter = db_adapter

    def create(self, migration):
        """
        Inserts a new ValueObject record into a table
        :param migration: MigrationVO
        """
        cursor = self.db_adapter.get_cursor()
        cursor.execute(
            'INSERT INTO ' + self.TABLE_NAME + ' (revision, migration_name) VALUES (%s, %s)',
            (migration.revision, migration.migration_name)
        )
        self.db_adapter.commit()
        cursor.close()

    def find_most_recent(self):
        """
        Fetches the most recent record from table by "create_date"
        :return: MigrationVO
        """
        query = 'SELECT * FROM ' + self.TABLE_NAME + ' ORDER BY create_date LIMIT 1'
        result = self.db_adapter.fetch_single_dict(query)

        migration_vo = None

        if result is not None:
            migration_vo = MigrationVO()
            migration_vo.id_ = result["id"]
            migration_vo.revision = result["revision"]
            migration_vo.migration_name = result["migration_name"]
            migration_vo.create_date = result["create_date"]

        return migration_vo

