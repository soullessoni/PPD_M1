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

    for maladie in maladies:


        cur2.execute(
            # table -> nom  maladie -> nom
            'CREATE TABLE "' + table[0] + '_' + str(maladie).rstrip() + '" '
            '(id INTEGER PRIMARY KEY, proba NUMERIC(10,8)); '
            'INSERT INTO "' + table[0] + '_' + str(maladie).rstrip() + '" '
            'SELECT id, proba '
            'FROM "' + table[0] + '" '
            'WHERE "maladie" '"= '" + (str(maladie).rstrip()) + "' "';'

            'create table "test" (like "' + table[0] + '_' + str(maladie).rstrip() + '"); '
            'INSERT INTO "test" '
            'SELECT * FROM "' + table[0] + '_' + str(maladie).rstrip() + '" ORDER BY proba desc; '
            'drop table "' + table[0] + '_' + str(maladie).rstrip() + '"; '
            'alter table "test" rename to "' + table[0] + '_' + str(maladie).rstrip() + '";'
        )

conn.commit()