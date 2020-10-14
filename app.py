import requests
import pygal
import os
from pygal.maps.world import COUNTRIES
from flask import Flask, render_template, request, redirect, url_for
from pygal.style import Style


url = 'https://wuhan-coronavirus-api.laeyoung.endpoint.ainize.ai/jhu-edu/latest?onlyCountries=true'
a = requests.get(url)
response_dict = a.json()

def get_country_code(country_name):
    for code, name in COUNTRIES.items():
        if name == country_name:
            return code
        if country_name == 'Russia':
            return 'ru'
        elif country_name == 'US':
            return 'us'
        elif country_name == 'Libya':
            return 'ly'
        elif country_name == 'Venezuela':
            return 've'
        elif country_name == 'Bolivia':
            return 'bo'
        elif country_name == 'India':
            return 'in'
        elif country_name == 'Iran':
            return 'ir'
        elif country_name == 'Korea, South':
            return 'kr'
        elif country_name == 'Burma':
            return 'mm'
        elif country_name == 'Vietnam':
            return 'vn'
        elif country_name == 'Taiwan*':
            return 'tw'
        elif country_name == 'Tanzania':
            return 'tz'
        elif country_name == 'Congo (Brazzaville)':
            return 'cd'
        elif country_name == 'Congo (Kinshasa)':
            return 'cg'
        elif country_name == 'Czechia':
            return 'cz'
    return None

cc, data = [], []
covid_dict = {}


def get_dict(x):
 
    global cc
    global data
    global covid_dict
    global response_dict

    for values in response_dict:
        for key, value in values.items():
            cc.append(values['countryregion'])
            data.append(values[x])

    dic_country = dict(zip(cc, data))

    for key, value in dic_country.items():
        country_name = key
        conf = value
        code = get_country_code(country_name)
        if code:
            covid_dict[code] = conf

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')

@app.route('/')
def confirmed() -> 'html':
    global covid_dict
    get_dict('confirmed')
    chart = pygal.maps.world.World()
    chart.title = 'COVID 19'
    chart.add('confirmed', covid_dict)
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
