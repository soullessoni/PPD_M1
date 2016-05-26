# -*- coding: utf-8 -*-
"""
"""

import psycopg2
from switch import Switch
import re
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

def drop_index_local():
        conn = connect()
        cur1 = conn.cursor()
        cur2 = conn.cursor()
        cur1.execute(
            'SELECT table_name '
            'FROM INFORMATION_SCHEMA.TABLES '
            'WHERE table_name LIKE \'farm%\';'
        )
        tables = cur1.fetchall()
        #Please a good RegEx
        for table in tables:
            print table[0]
            is_farm = re.compile('\\bfarm[0-9]+\\b', re.IGNORECASE)
            if (is_farm.match(table[0]) != None):
                print table[0]
            else:
                cur2.execute(
                    'drop table "' + table[0] + '";'
                    )
        conn.commit()


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

@app.route('/db_action', methods=['GET', 'POST'])
def db_action():
    if session.get('connexion'):
        if request.method == 'POST':
            with Switch(request.form['action']) as case:
                if case("top_K"):
                    return redirect(url_for("top_k"))
                if case("threshold"):
                    return redirect(url_for("threshold"))
                if case("index_local"):
                    return redirect(url_for("index_local"))
                if case("index_global"):
                    return redirect(url_for("index_global"))
                if case("db_link"):
                    return redirect(url_for("db_link"))
                if case.default:
                    return redirect(url_for('error'))
        else:
            return render_template('db_action.html')
    else:
        return redirect(url_for('error'))

@app.route('/index/local')
def index_local():
    if session.get('connexion'):
        drop_index_local()
        conn = connect()
        cur1 = conn.cursor()
        cur2 = conn.cursor()

        print fmaladie_name
        with open(fmaladie_name) as f:
            maladies = (f.readlines())

        cur1.execute(
            'SELECT table_name '
            'FROM INFORMATION_SCHEMA.TABLES '
            'WHERE table_name LIKE \'farm%\';'
        )
        tables = cur1.fetchall()
        for table in tables:
            for maladie in maladies:
                cur2.execute(
                    'CREATE TABLE "' + table[0] + '_' + str(maladie).rstrip() + '" '
                    '(id INTEGER PRIMARY KEY, proba NUMERIC(10,8)); '
                    'INSERT INTO "' + table[0] + '_' + str(maladie).rstrip() + '" '
                    'SELECT id, proba '
                    'FROM "' + table[0] + '" '
                    'WHERE "maladie" '"= '" + (str(maladie).rstrip()) + "' "';'

                    'CREATE TABLE "test" (LIKE "' + table[0] + '_' + str(maladie).rstrip() + '"); '
                    'INSERT INTO "test" '
                    'SELECT * FROM "' + table[0] + '_' + str(maladie).rstrip() + '" ORDER BY proba DESC; '
                    'DROP TABLE "' + table[0] + '_' + str(maladie).rstrip() + '"; '
                    'ALTER TABLE "test" RENAME TO "' + table[0] + '_' + str(maladie).rstrip() + '";'
                )
        conn.commit()
        return redirect(url_for('db_action'))
    else:
        return redirect(url_for('error'))

@app.route('/index_global', methods=['GET', 'POST'])
def index_global():
    if session.get('connexion'):
        if request.method == 'POST':
            conn = connect()
            cur1 = conn.cursor()
            cur2 = conn.cursor()
            cur3 = conn.cursor()
            cur4 = conn.cursor()
            cur1.execute(
                "DROP TABLE IF EXISTS index_global;"
                "CREATE TABLE index_global(adress CHAR(100), proba NUMERIC(10,8));"
            )
            sick = request.form['maladie']
            print sick
            cur2.execute(
                #creation de table_path et la remplir
                'DROP TABLE IF EXISTS table_path;'
                'CREATE TABLE table_path(adress CHAR(100));'
                'insert into table_path (adress)'
                'SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_name LIKE \'%_' + sick + '\';'
            )
            cur3.execute(
                #pour remplir la listeTablesSick en bas
                'SELECT adress FROM table_path;'
            )
            listeTablesSick = cur3.fetchall()
            print listeTablesSick
            i = 0
            for liste in listeTablesSick:
                print '-----------------------'
                print liste[0]
                cur3.execute(
                    #remplir l'index global
                    'INSERT INTO index_global(adress, proba)'
                    'SELECT table_path.adress, "'+ liste[0].rstrip() +'".proba FROM table_path, "'+ liste[0].rstrip() +'" LIMIT 1;'
                    'DELETE FROM table_path WHERE ctid IN (SELECT ctid FROM table_path LIMIT 1)'



                )
                i = i + 1
            print 'en haut pas touche'
            test = 'toto2'
            cur4.execute(
                # mettre en ordre l'index global
                """CREATE TABLE test (LIKE index_global);
                    INSERT INTO test
                    SELECT * FROM index_global ORDER BY proba DESC;
                    DROP TABLE index_global;
                    ALTER TABLE test RENAME TO index_global;
                """
                #Suppression de table_path à ajjouter si necessaire
                #dblink
                """
                    select dblink_connect('"""+test+"""', 'host=localhost port=5432 dbname=PPD user=postgres password=admin');
                    SELECT * FROM dblink('toto2','SELECT proba FROM farm1') AS t(c numeric) LIMIT 1;
                """

            )
            print 'okkkkkkkkkkkkkkk'
            conn.commit()
            return redirect(url_for('db_action'))
    else:
        return redirect(url_for('error'))
    return render_template('index_global.html')

@app.route('/top_k')
def top_k():
    return render_template('top_k.html')

@app.route('/threshold')
def threshold():
    return render_template('threshold.html')

@app.route('/db_link')
def db_link():

    return render_template('db_link.html')

@app.route('/error')
def error():
    return render_template("db_error.html")

app.secret_key = '6Mb0JgsZ4HLJpnbSjNiZuTwaSA7RwV3Inf6DUmnu'

if __name__ == '__main__':
    app.run()
