#!/usr/bin/python
# coding: utf-8
import os
from flask import Flask, render_template

app = Flask(  # Create a flask app
	__name__,
	template_folder='templates',  # Name of html file folder
	static_folder='static'  # Name of directory for static files
)

@app.route('/')
def entry_point():
    return render_template('home.html')

@app.route('/vwo/abtest/<user_id>/')
def vwo_abtest(user_id):
    dict = {
        'user_id': user_id,
        'variation_name': 'CONTROL'
    }
    return render_template('vwo_abtest.html', dict=dict)

@app.route('/vwo/ff/<user_id>/')
def vwo_ff(user_id):
    return render_template('vwo_ff.html')

if __name__ == '__main__':
    app.run(debug=True)