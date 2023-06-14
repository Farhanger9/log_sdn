import psycopg2
from db_config import *

#establishing the connection
conn = psycopg2.connect(
   database=database, user=user, password=password, host=host, port= port
)
conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Preparing query to create a database
sql = '''CREATE database PLAYLOG_DATABASE''';

#Creating a database
cursor.execute(sql)
print("Database created successfully........")

#Closing the connection
conn.close()