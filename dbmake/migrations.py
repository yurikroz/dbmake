
import os
import re
import common


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

    def create(self, migration_vo):
        """
        Inserts a new ValueObject record into a table
        :param migration_vo: MigrationVO
        """
        cursor = self.db_adapter.get_cursor()
        cursor.execute(
            'INSERT INTO ' + self.TABLE_NAME + ' (revision, migration_name) VALUES (%s, %s)',
            (str(migration_vo.revision), migration_vo.migration_name)
        )
        self.db_adapter.commit()
        cursor.close()

    def find_most_recent(self):
        """
        Fetches the most recent record from table by "create_date"
        :return: MigrationVO
        """
        query = 'SELECT * FROM ' + self.TABLE_NAME + ' ORDER BY create_date DESC LIMIT 1'
        result = self.db_adapter.fetch_single_dict(query)

        migration_vo = None

        if result is not None:
            migration_vo = MigrationVO()
            migration_vo.id_ = result["id"]
            migration_vo.revision = result["revision"]
            migration_vo.migration_name = result["migration_name"]
            migration_vo.create_date = result["create_date"]

        return migration_vo

    def is_migration_table_exists(self):
        """
        Checks if the migrations table is already exists
        :returns Boolean
        """
        cursor = self.db_adapter.get_cursor()
        cursor.execute("SELECT * FROM information_schema.tables WHERE table_name='" + self.TABLE_NAME + "'")

        if cursor.rowcount == 0:
            cursor.close()
            return False

        cursor.close()
        return True

    def drop_migrations_table(self):
        """
        Drops dbmake's auxiliary migrations table
        :return: Boolean
        """
        cursor = self.db_adapter.get_cursor()
        cursor.execute('DROP TABLE "' + self.TABLE_NAME + '"')
        self.db_adapter.commit()
        cursor.close()

        return True


class Migration:

    """Separates"""
    MIGRATE_UP_DOWN_SEPARATOR = "-- DBMAKE: SEPARATOR"
    name = None
    revision = None
    migrate_up_statements = None
    migrate_down_statements = None

    MIGRATION_TEMPLATE = '''
    -- DBMAKE: MIGRATE UP
    /*
        Place here all necessary DDL statements describing schema changes to be made

        Example:
        CREATE TABLE my_customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(45),
            update_date TIMESTAMP DEFAULT NOW() NOT NULL,
            create_date TIMESTAMP DEFAULT NOW() NOT NULL
        );
    */

    ''' + MIGRATE_UP_DOWN_SEPARATOR + '''

    -- DBMAKE: MIGRATE DOWN
    /*
        Place here all DDL statements canceling the changes made to schema

        Example:
        DROP TABLE my_customers;
    */

    '''

    def __init__(self, migration_file):
        """
        :param migration_file: Full path to a migration file including the file's name
        :raise AttributeError, IOError
        """
        # print "-----------------------------"
        # print "Migration file: %s" % migration_file

        # Read a migration file and extract from there "Migrate UP" and "Migrate DOWN" statements
        f = open(migration_file, 'r')
        with f:
            migration_file_content = f.read()
            migration_file_parts = migration_file_content.split(self.MIGRATE_UP_DOWN_SEPARATOR)

            self.migrate_up_statements = migration_file_parts[0]

            if len(migration_file_parts) > 1:
                self.migrate_down_statements = migration_file_parts[1]

        # Extract the exact migration file name, and then parse a migraiton revision and a name from it
        result = re.match('^(?P<revision>[0-9]+)_(?P<name>.*)\.sql$', migration_file.split('/')[-1])
        self.revision = int(result.group('revision'))
        self.name = result.group('name')


        # print "Name: %s" % self.name
        # print "Revision: %s" % self.revision
        # print "Content:"
        # print migration_file_content
        # print "Migration UP:"
        # print self.migrate_up_statements
        # print "Migration DOWN:"
        # print self.migrate_down_statements
        # print "-----------------------------"

    def migrate(self, db_adapter):
        """
        Applies the migration's "Migrate UP" statements on a database via db_adapter's connection
        """
        if self.migrate_up_statements is None:
            return False

        # Apply migrations statements
        cursor = db_adapter.get_cursor()
        cursor.execute(self.migrate_up_statements)
        db_adapter.commit()
        cursor.close()

        return True

    def rollback(self, db_adapter):
        """
        Applies the migration's "Migrate DOWN" statements on a database via db_adapter's connection
        """
        if self.migrate_down_statements is None:
            return False

        cursor = db_adapter.get_cursor()
        cursor.execute(self.migrate_down_statements)
        db_adapter.commit()
        cursor.close()

        return True

    def get_vo(self):
        """
        Returns MigrationVO that represents a new migration record with the Migration's params
        """
        migration_vo = MigrationVO()
        migration_vo.migration_name = self.name
        migration_vo.revision = self.revision

        return migration_vo


class MigrationsManager:
    """
    Performs and rollbacks migrations
    """

    # _db_adapter = None
    _migrations_dir = None
    _cur_revision = None

    # , db_adapter
    def __init__(self, migrations_dir):
        # self._db_adapter = db_adapter
        self._migrations_dir = migrations_dir

    def migrate_to_revision(self, target_revision, db_adapter, dry_run=False):
        """
        :param target_revision: Migration revision to migrate to
        :return:
        """
        revision = int(target_revision)
        migrations = self._migrations_list()

        if len(migrations) == 0:
            raise common.DbmakeException("Error! No migrations found in %s" % self._migrations_dir)

        # migrations_dao = MigrationsDao(self._db_adapter)
        migrations_dao = MigrationsDao(db_adapter)

        # Check schema's current revision against the migration's revision
        # and decide whether to migrate or not
        migration_vo = migrations_dao.find_most_recent()

        # If database has no revision, then first apply the ZERO-MIGRATION
        applied_zero_migration = False
        if migration_vo is None:
            if migrations[0].revision != 0:
                raise common.DbmakeException("Error! No ZERO-MIGRATION was found in %s" % self._migrations_dir)

            print "Migrating up to revision: 0...",

            if not dry_run:
                # result = migrations[0].migrate(self._db_adapter)
                result = migrations[0].migrate(db_adapter)
                if result is True:
                    # Update migrations table
                    migrations_dao.create(migrations[0].get_vo())
                    current_revision = 0
                else:
                    print "Failure"
                    raise common.DbmakeException("Error! Failed to migrate to revision %s" % str(migrations[0].revision))
            else:
                current_revision = 0

            print "OK"
            applied_zero_migration = True
        else:
            current_revision = int(migration_vo.revision)

        # Now let's find indices of current migration and target migration within migrations list
        current_index = None
        target_index = None
        for index, elem in enumerate(migrations):
            if elem.revision == current_revision:
                current_index = index

            if elem.revision == target_revision:
                target_index = index

        if current_index is None:
            raise common.DbmakeException("Error! A migration file of current revision was not found. "
                                         "Current revision: %s" % current_revision)
        if target_index is None:
            raise common.DbmakeException("Error! A migration file of target revision was not found. "
                                         "Target revision: %s" % target_revision)

        if current_index == target_index:
            if not applied_zero_migration:
                print "Current revision is already equals to target revision"
            return True

        elif (target_index - current_index) > 0:
            for i in range(current_index + 1, target_index + 1, 1):
                print "Migrating up to revision: %s..." % str(migrations[i].revision),

                if not dry_run:
                    # migrations[i].migrate(self._db_adapter)
                    migrations[i].migrate(db_adapter)
                    migrations_dao.create(migrations[i].get_vo())
                print "OK"
        else:
            for i in range(current_index, target_index, -1):
                print "Migrating down to revision: %s..." % str(migrations[i-1].revision),

                if not dry_run:
                    # migrations[i].rollback(self._db_adapter)
                    migrations[i].rollback(db_adapter)
                    migrations_dao.create(migrations[i-1].get_vo())
                print "OK"

        return True

    def _migrations_list(self):
        """
        Returns a sorted list of migrations instances representing migrations files
        within the manager's migrations directory
        """
        def _sort_by_revision(m):
            """
            A key function to sort migrations list by revision
            """
            return m.revision

        migrations = []
        for file_ in os.listdir(self._migrations_dir):
            if file_.endswith(".sql"):
                migration_file = self._migrations_dir + os.sep + file_

                try:
                    migrations.append(Migration(migration_file))
                except AttributeError:
                    pass

        # Sort migrations in ascending order by migration.revision field
        migrations = sorted(migrations, key=_sort_by_revision)

        return migrations

    def revisions(self):
        """
        Returns a sorted list in ascending order of available migration revisions
        in the migration directory
        :return:
        """

        revisions = []
        for file_ in os.listdir(self._migrations_dir):
            if file_.endswith(".sql"):
                try:
                    result = re.match('^(?P<revision>[0-9]+)_(?P<name>.*)\.sql$', file_)
                    revisions.append(int(result.group('revision')))
                except AttributeError:
                    pass

        # Sort migrations in ascending order by migration.revision field
        revisions = sorted(revisions)

        return revisions

    def is_revision_exists(self, revision):
        if int(revision) in self.revisions():
            return True
        return False

    def latest_revision(self):
        """
        Returns a value of the most recent migrations revision
        :return: int
        """
        return self.revisions()[-1]