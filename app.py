import requests
import pygal
import os
from pygal.maps.world import COUNTRIES
from flask import Flask, render_template, request, redirect, url_for
from pygal.style import Style


url = 'https://covid19-api.org/api/status/'
a = requests.get(url)
response_dict = a.json()

covid_dict = {}


def get_dict(x):
    global response_dict
    global covid_dict
    for el in response_dict:
        covid_dict[el['country'].lower()] = el[x]

app = Flask(__name__)
par = 'this_should_be_configured'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', par)


@app.route('/')
def confirmed() -> 'html':
    global covid_dict
    get_dict('cases')
    chart = pygal.maps.world.World()
    chart.title = 'COVID 19'
    chart.add('cases', covid_dict)
    chart = chart.render_data_uri()
    return render_template('confirmed.html', chart=chart)


@app.route('/death')
def death():
    global covid_dict
    get_dict('deaths')
    custom_style = Style(colors=('#000000', '#000000', '#000000'))
    chart = pygal.maps.world.World(style=custom_style)
    chart.title = 'COVID 19'
    chart.add('Deaths', covid_dict)
    chart = chart.render_data_uri()
    return render_template('deaths.html', chart=chart)


@app.route('/recovered')
def recovered():
    global covid_dict
    get_dict('recovered')
    custom_style = Style(colors=('#008000', '#008000', '#008000'))
    chart = pygal.maps.world.World(style=custom_style)
    chart.title = 'COVID 19'
    chart.add('Recovered', covid_dict)
    chart = chart.render_data_uri()
    return render_template('recovered.html', chart=chart)

if __name__ == '__main__':
    app.run(debug=True)
