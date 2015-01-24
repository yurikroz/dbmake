/* Sample migration file #1 used for dbmake demonstration */

-- DBMAKE: MIGRATE UP
ALTER TABLE td_customers ADD COLUMN email VARCHAR(128) DEFAULT '' NOT NULL;


-- DBMAKE: MIGRATE DOWN
ALTER TABLE td_customers DROP COLUMN email;
