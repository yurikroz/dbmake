/* Sample migration file #2 used for dbmake demonstration */

-- DBMAKE: MIGRATE UP
ALTER TABLE td_customers ADD COLUMN address VARCHAR(120);

-- DBMAKE: SEPARATOR

-- DBMAKE: MIGRATE DOWN
ALTER TABLE td_customers DROP COLUMN address;
