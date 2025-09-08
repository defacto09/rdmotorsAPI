from importlib.metadata import pass_none

import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Qndr1@n4",
    database="rdmotorsdb"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM services")
for row in cursor.fetchall():
    print(row)

