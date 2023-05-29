import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="moi",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table



   
   
   
   
   

cur.execute('CREATE TABLE IF NOT EXISTS registration ('
                                 'first_name varchar(20) NOT NULL ,'
                                 'last_name varchar(20) NOT NULL ,'
                                 'phone_number varchar(20) NOT NULL ,'
                                 'email_id varchar(512) NOT NULL ,'
                                 'dob DATE not null,'
                                 'QatarID varchar(11) NOT NULL CONSTRAINT PK_reg PRIMARY KEY,'
                                 'encoding varchar(5000) NOT NULl);'
                                 )




conn.commit()

cur.close()
conn.close()