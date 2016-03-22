# -*- coding: utf-8 -*-
"""
"""

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


# create our little application :)
app = Flask(__name__)



@app.route('/')
def home():
    return render_template('home.html')
