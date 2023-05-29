import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="moph",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table



cur.execute('CREATE TABLE IF NOT EXISTS health_status ('
                                 'covid_status varchar(50) NOT NULl,'                                 
                                 'QatarID varchar(11) NOT NULL CONSTRAINT PK_hst PRIMARY KEY);'                                 
                                 )





conn.commit()

cur.close()
conn.close()