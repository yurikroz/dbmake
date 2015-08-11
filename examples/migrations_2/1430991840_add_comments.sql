
    -- DBMAKE: MIGRATE UP
	
	COMMENT ON TABLE customers IS 'This is a customer table for dbmake demonstration';

    -- DBMAKE: SEPARATOR

    -- DBMAKE: MIGRATE DOWN
    	COMMENT ON TABLE customers IS '';

    
