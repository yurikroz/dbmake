/* Sample migration file #1 used for dbmake demonstration */

-- DBMAKE: MIGRATE UP
CREATE TABLE td_billings
(
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    amount_payed INTEGER,
    update_date TIMESTAMP DEFAULT NOW() NOT NULL,
    create_date TIMESTAMP DEFAULT NOW() NOT NULL,
    CONSTRAINT billings_customer_fk FOREIGN KEY (customer_id) REFERENCES td_customers(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- DBMAKE: SEPARATOR

-- DBMAKE: MIGRATE DOWN
DROP TABLE td_billings;
