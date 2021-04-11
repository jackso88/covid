import requests
import pygal
import os
from pygal.maps.world import COUNTRIES
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from pygal.style import Style


url = 'https://covid19-api.org/api/status/'
a = requests.get(url)
response_dict = a.json()


def get_dict(x):
    global response_dict
    tmp_dict = {}
    for el in response_dict:
        tmp_dict[el['country'].lower()] = el[x]
    return tmp_dict

app = Flask(__name__)
bootstrap = Bootstrap(app)
nav = Nav()
par = 'this_should_be_configured'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', par)


nav.register_element('top', Navbar(
        'COVID19',
        View('Случаев', '.confirmed'),
        View('Смертей', '.death'),
        View('Выздоровело', '.recovered'),
    ))

nav.init_app(app)


@app.route('/')
def confirmed() -> 'html':
    covid_dict = get_dict('cases')
    chart = pygal.maps.world.World()
    chart.title = 'Количество зарегистрированных случаев COVID 19'
    chart.add('cases', covid_dict)
    chart = chart.render_data_uri()
    return render_template('index.html', chart=chart)


@app.route('/death')
def death():
    covid_dict = get_dict('deaths')
    custom_style = Style(colors=('#000000', '#000000', '#000000'))
    chart = pygal.maps.world.World(style=custom_style)
    chart.title = 'Количество умерших от COVID 19'
    chart.add('Deaths', covid_dict)
    chart = chart.render_data_uri()
    return render_template('index.html', chart=chart)


@app.route('/recovered')
def recovered():
    covid_dict = get_dict('recovered')
    custom_style = Style(colors=('#008000', '#008000', '#008000'))
    chart = pygal.maps.world.World(style=custom_style)
    chart.title = 'Количество излечившихся от COVID 19'
    chart.add('Recovered', covid_dict)
    chart = chart.render_data_uri()
    return render_template('index.html', chart=chart)


if __name__ == '__main__':
    app.run(debug=True)
