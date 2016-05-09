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

@app.route('/')
def home():
    param = "Hello"
    return render_template('home.html', parameters=param)

@app.route('/db_connect/', methods=['GET', 'POST'])
def db_connect():
    conn = None
    if request.method == 'POST':
#        db_name = request.form['db_name']
#        usr = request.form['usr']
#        psw = request.form['psw']
#        if request.form['host'] == "":
#            host = "localhost"
#        else:
#            host = request.form['host']

        try:
            conn = psycopg2.connect("dbname='PPD_diseases' user='postgres' host='localhost' password='root'")
        except:

            return redirect(url_for('db_error'))

        return redirect(url_for('db_show'))

    return render_template("db_connect.html")

@app.route('/db_error')
def db_error():
    return render_template("db_error.html")

@app.route('/db_show')
def db_show():
    return render_template('db_show.html')

if __name__ == '__main__':
    app.run()
