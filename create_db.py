# pip install mysql-connector
# pip install mysql-connector-python
# pip install mysql-connector-python-rf
# pip install pymysql
# pip install cryptography
import os

import pymysql

# Establish connection to MySQL server
mydb = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"), # Use MYSQL_USER here
    password=os.getenv("DB_PASSWORD", "fanfic_passwords"), # Use MYSQL_PASSWORD here
    database=os.getenv("DB_NAME", "fanfics")
)

my_cursor = mydb.cursor()

# my_cursor.execute("CREATE DATABASE fanfics")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)