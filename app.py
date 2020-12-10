#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g
import flask_sijax 
import os
import time

DEVELOPMENT_ENV  = True

app = Flask(__name__)

app_data = {
    "name":         "Peter's Starter Template for a Flask Web App",
    "description":  "A basic Flask app using bootstrap for layout",
    "author":       "Peter Simeth",
    "html_title":   "Peter's Starter Template for a Flask Web App",
    "project_name": "Starter Template",
    "keywords":     "flask, webapp, template, basic"
}

path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
app.config['SIJAX_STATIC_PATH'] = path
flask_sijax.Sijax(app)


@app.route('/')
def index():
    return render_template('index.html', app_data=app_data)

@flask_sijax.route(app, '/ardu/<int:req>')
def ardu(req):
    if req == 100:
        with open("test.txt", 'w') as f:
                f.write(str(100))
                f.close()
                time.sleep(1)
    elif req == 0:
        with open("test.txt", 'w') as f:
                f.write(str(0))
                f.close()

    content = None
    def retrieve_data(obj_response):
        with open("test.txt", "r") as f:
            content = f.read()
            if int(content) == 100:
                obj_response.html("#element", "We have <br>a new node:")
                obj_response.css("#img_element", "display","block")
                obj_response.script("$('#exampleModal').modal('show');")
                obj_response.script("routes()")                
            else:
                obj_response.script("$('#exampleModal').modal('hide')")


        f.close()
        with open("test.txt", 'w') as f:
                f.write(str(0))
                f.close()

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('ardu', retrieve_data) 
        return g.sijax.process_request()
          
    return render_template("ardu.html")

@app.route('/about')
def about():
    return render_template('about.html', app_data=app_data)


@app.route('/service')
def service():
    return render_template('service.html', app_data=app_data)


@app.route('/contact')
def contact():
    return render_template('contact.html', app_data=app_data)


if __name__ == '__main__':
    app.run(debug=DEVELOPMENT_ENV)