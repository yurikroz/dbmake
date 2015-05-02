/* Sample migration file #1 used for dbmake demonstration */

-- DBMAKE: MIGRATE UP

/**
 * Billings table contains all billing records related to customers 
 * by a customer ID.
 */
CREATE TABLE td_billings
(
    id SERIAL PRIMARY KEY,    
    /** Customer ID stored in customers table  */
    customer_id INTEGER /** test redundant comment */,
    amount_payed INTEGER /** How much a customer has payed in this bill */,
    update_date TIMESTAMP DEFAULT NOW() NOT NULL,
    create_date TIMESTAMP DEFAULT NOW() NOT NULL,
    CONSTRAINT billings_customer_fk FOREIGN KEY (customer_id) REFERENCES td_customers(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- DBMAKE: SEPARATOR

-- DBMAKE: MIGRATE DOWN
DROP TABLE td_billings;
