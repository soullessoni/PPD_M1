# -*- coding: utf-8 -*-
"""
"""

import psycopg2
import sys

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def home():
    param = "Hello"
    return render_template('home.html', parameters=param)

@app.route('/db_show/<db_name>/')
def db_show(db_name):
    try:
        conn = psycopg2.connect("dbname='" + db_name + "' user='postgres' host='localhost' password='admin'")
    except:
        return render_template('db_show_error.html', db_name=db_name)

    cur = conn.cursor()
    cur.execute("SELECT " + db_name + " from pg_database")
    rows = cur.fetchall()

    print "\nShow me the databases:\n"
    for row in rows:
        print "   ", row[0]


    return render_template('db_show.html', db_name=db_name, db_show=rows)

if __name__ == '__main__':
    app.run()