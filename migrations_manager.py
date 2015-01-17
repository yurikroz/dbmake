"""
@author: Yuri Kroz
Created on Jan 14, 2015
"""

import psycopg2

#Define our connection string
conn_string = "host='54.68.72.64' dbname='testdb' user='splanger' password='dd123a1a2'"

# Connect to an existing database
conn = psycopg2.connect(conn_string)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
#cur.execute("SELECT * FROM tabledb;")

# Pass data to fill a query placeholders and let Psycopg perform
# the correct conversion (no more SQL injections!)
# cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))

# Query the database and obtain data as Python objects
#>>> cur.execute("SELECT * FROM test;")
#>>> cur.fetchone()
#(1, 100, "abc'def")
cur.execute("SELECT * FROM td_customers")
result = cur.fetchone()
print result

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()

exit