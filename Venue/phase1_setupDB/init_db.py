import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="mall",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table



   
   
   
   
   

cur.execute('CREATE TABLE IF NOT EXISTS mallentry ('
                                 'entry_time timestamptz NOT NULL ,'
                                 'covid_status varchar(20) NOT NULL ,'
                                 'QatarID varchar(11) NOT NULL);'
                                 )



conn.commit()



cur.execute('CREATE TABLE IF NOT EXISTS contacttracing ('                                                                
                                 'QatarID1 varchar(11) NOT NULL,'
                                 'QatarID2 varchar(11) NOT NULL);'
                                 )



conn.commit()

cur.close()
conn.close()
