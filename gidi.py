# -*- coding: utf-8 -*-
"""
"""

import psycopg2
from switch import Switch
import sys
import pprint

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

#File with disease's name
fmaladie_name = "maladies_bovines.txt"

def connect():
    return psycopg2.connect("dbname='"+ session['db_name'] +
                            "' user='"+ session['user'] +
                            "' host='" + session['host'] +
                            "' password='" + session['password'] + "'")

@app.route('/')
def home():
    session.clear()
    return render_template('layout.html')

@app.route('/db_disconnect')
def db_disconnect():
    return redirect(url_for('home'))

@app.route('/db_connect/', methods=['GET', 'POST'])
def db_connect():
    if not session.get('connexion'):
        if request.method == 'POST':
            db_name = request.form['db_name']
            usr = request.form['usr']
            psw = request.form['psw']
            #Localhost is default
            if request.form['host'] == "":
                host = "localhost"
            else:
                host = request.form['host']

            try:
                conn = psycopg2.connect("dbname='"+db_name+"' user='"+usr+"' host='"+host+"' password='"+psw+"'")
                conn.close()

            except:
                return redirect(url_for('error'))

            #set session data
            session['db_name'] = db_name
            session['user'] = usr
            session['password'] = psw
            session['host'] = host
            session['connexion'] = True
            return redirect(url_for('db_action'))

    else:
        return redirect(url_for('db_action'))

    return render_template("db_connect.html")

@app.route('/error')
def error():
    return render_template("db_error.html")

@app.route('/db_action')
def db_action():
    if session.get('connexion'):
        if request.method == 'POST':
            print "which action ?"
            with Switch(val) as case:
                if case(1):
                    values.append('Found 1')

                if case(2, 3):
                    values.append('Found 2 or 3')
        else:
            return render_template('db_action.html')
    else:
        return redirect(url_for('error'))

@app.route('/index_generator/local')
def index_local_generator():
    if session.get('connexion'):
        conn = session['connexion']
        cur1 = conn.cursor()
        cur2 = conn.cursor()

        cur1.execute(
                     'SELECT table_name '
                     'FROM INFORMATION_SCHEMA.TABLES '
                     'WHERE table_name LIKE "farm%";')

        with open(fmaladie_name) as f:
            maladies = (f.readlines())


        tables = cur1.fetchall()

        for table in tables:
            for maladie in maladies:
                print str(maladie)
                cur2.execute(
                    #table -> nom  maladie -> nom
                    'CREATE TABLE "' + table[0] + '_' + str(maladie).rstrip() + '" '
                    '(id INTEGER PRIMARY KEY, proba NUMERIC(10,8)); '
                    'INSERT INTO "' + table[0] + '_' + str(maladie).rstrip() + '" '
                    'SELECT id, proba '
                    'FROM "' + table[0] + '" '
                    'WHERE "maladie" '
                    "= '"+(str(maladie).rstrip())+"' "
                    ';'
                )

        conn.commit()
    else:
        return redirect(url_for('error'))

app.secret_key = '6Mb0JgsZ4HLJpnbSjNiZuTwaSA7RwV3Inf6DUmnu'

if __name__ == '__main__':
    app.run()
