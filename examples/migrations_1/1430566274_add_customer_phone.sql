
    -- DBMAKE: MIGRATE UP
    ALTER TABLE td_customers ADD COLUMN phone VARCHAR(12);

    -- DBMAKE: SEPARATOR

    -- DBMAKE: MIGRATE DOWN
    ALTER TABLE td_customers DROP COLUMN phone;

    
