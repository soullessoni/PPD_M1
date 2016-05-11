# -*- coding: utf-8 -*-
"""
"""

import psycopg2
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
            return redirect(url_for('db_show'))

    else:
        return redirect(url_for('db_show'))

    return render_template("db_connect.html")

@app.route('/error')
def error():
    return render_template("db_error.html")

@app.route('/db_show')
def db_show():
    if session.get('connexion'):
        conn = connect()
        #DO THINGS
        param = "parameters to display"
        conn.close()
        return render_template('db_show.html', param=param)
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
                cur2.execute(
                    #table -> nom  maladie -> nom
                    "CREATE TABLE " + table + "_" + maladie + " "
                    "   (id integer PRIMARY KEY, proba numeric(10,8), "
                    "INSERT INTO " + table + "_" + maladie + " (id, proba) "
                    "SELECT id, proba "
                    "FROM " + table + " "
                    "WHERE maladie = '" + maladie + "';")
        conn.commit()
    else:
        return redirect(url_for('error'))

app.secret_key = '6Mb0JgsZ4HLJpnbSjNiZuTwaSA7RwV3Inf6DUmnu'

if __name__ == '__main__':
    app.run()
