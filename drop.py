import os
import csv
import psycopg2

fmaladie_name = "maladies_bovines.txt"
conn = psycopg2.connect("dbname='"+'PPD'+"' user='"+'postgres'+"' host='"+'localhost'+"' password='"+'admin'+"'")

cur1 = conn.cursor()
cur2 = conn.cursor()

cur1.execute(
    'SELECT table_name '
    'FROM INFORMATION_SCHEMA.TABLES '
    'WHERE table_name LIKE \'farm%\';')

maladies = []
with open(fmaladie_name) as f:
    maladies = (f.readlines())

tables = cur1.fetchall()

for table in tables:

    test = table[0]
    if (test == "farm1"):
        print "les tables ........................................"
    elif test == "farm2":
        print "les tables ........................................"
    elif test == "farm3":
        print "les tables ........................................"
    elif test == "farm4":
        print "les tables ........................................"

    elif test == "farm5":
        print "les tables ........................................"

    else:
        print table[0]
        cur2.execute(
            'drop table "' + table[0] + '";'
        )

conn.commit()