/* Sample migration file #1 used for dbmake demonstration */

-- DBMAKE: MIGRATE UP
CREATE TABLE td_customers
(
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(80),
    last_name VARCHAR(45),
    age INT CHECK(age > 0),
    update_date TIMESTAMP DEFAULT NOW() NOT NULL,
    create_date TIMESTAMP DEFAULT NOW() NOT NULL
);


-- DBMAKE: MIGRATE DOWN
DROP TABLE td_customers;
