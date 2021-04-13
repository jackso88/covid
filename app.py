import requests
import pygal
import os
import datetime
from pygal.maps.world import COUNTRIES
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from pygal.style import Style


date_now = datetime.datetime.now().date()
date_end = date_now - datetime.timedelta(29)


def get_latest_info():
    url = 'https://covid19-api.org/api/status/'
    a = requests.get(url)
    latest_dict = a.json()
    return latest_dict


def get_dict(x):
    response_dict = get_latest_info()
    tmp_dict = {}
    for el in response_dict:
        tmp_dict[el['country'].lower()] = el[x]
    return tmp_dict


def get_countries_dict():
    url = 'https://covid19-api.org/api/countries/'
    a = requests.get(url)
    cnt_dict = a.json()
    return cnt_dict


cnt_dict = get_countries_dict()


def get_countries_list():
    global cnt_dict
    countries_list = []
    for el in cnt_dict:
        countries_list.append(el['name'])
    return countries_list


def get_country_code(country_name):
    global cnt_dict
    for el in cnt_dict:
        if el['name'] == country_name:
            return el['alpha2']
            break


def get_timeline(country):
    url = f"https://covid19-api.org/api/timeline/{country}"
    a = requests.get(url)
    timeline_dict = a.json()
    return timeline_dict


def data_proc(data_dict, key):
    global date_end
    date, values = [], []
    for el in data_dict:
        if el['last_update'] >= date_end.\
                strftime("%Y-%m-%dT00:00:00.000"):
            if el['last_update'][:10] not in date:
                date.append(el['last_update'][:10])
                values.append(el[key])
    return date, values


def diff(lst):
    lst2 = []
    i = 0
    for el in lst[1:]:
        x = int(el) - int(lst[i])
        lst2.append(x)
        i += 1
    return lst2


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
        View('Отчет за последний месяц', '.report')
        )
    )

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


@app.route('/report', methods=['GET', 'POST'])
def report():
    countries_list = get_countries_list()
    if request.method == 'POST':
        cnt_code = get_country_code(request.form['teamDropdown'])
        cnt_timeline = get_timeline(cnt_code)

        data = data_proc(cnt_timeline, 'cases')
        case_chart = pygal.Line(x_label_rotation=45)
        case_chart.title = """Общее количество зарегистрированных
                                         случаев за последние 30 дней"""
        case_chart.x_labels = data[0][::-1]
        case_chart.add(request.form['teamDropdown'], data[1][::-1])
        case_chart = case_chart.render_data_uri()

        data_d = diff(data[1][::-1])
        case_chart_d = pygal.Line(x_label_rotation=45)
        case_chart_d.title = """Изменение количества зараженных"""
        case_chart_d.x_labels = data[0][-2::-1]
        case_chart_d.add(request.form['teamDropdown'], data_d)
        case_chart_d = case_chart_d.render_data_uri()

        data_rec = data_proc(cnt_timeline, 'recovered')
        custom_style = Style(colors=('#008000', '#008000', '#008000'))
        rec_chart = pygal.Line(style=custom_style, x_label_rotation=45)
        rec_chart.title = """Общее количество воздоровевших
                                                 за последние 30 дней"""
        rec_chart.x_labels = data_rec[0][::-1]
        rec_chart.add(request.form['teamDropdown'], data_rec[1][::-1])
        rec_chart = rec_chart.render_data_uri()

        rec_data_d = diff(data_rec[1][::-1])
        rec_chart_d = pygal.Line(style=custom_style, x_label_rotation=45)
        rec_chart_d.title = """Изменение количества выздоровевших"""
        rec_chart_d.x_labels = data_rec[0][-2::-1]
        rec_chart_d.add(request.form['teamDropdown'], rec_data_d)
        rec_chart_d = rec_chart_d.render_data_uri()

        data_d = data_proc(cnt_timeline, 'deaths')
        custom_style = Style(colors=('#000000', '#000000', '#000000'))
        d_chart = pygal.Line(style=custom_style, x_label_rotation=45)
        d_chart.title = 'Общее количество умерших за последние 30 дней'
        d_chart.x_labels = data_d[0][::-1]
        d_chart.add(request.form['teamDropdown'], data_d[1][::-1])
        d_chart = d_chart.render_data_uri()

        d_data_d = diff(data_d[1][::-1])
        d_chart_d = pygal.Line(style=custom_style, x_label_rotation=45)
        d_chart_d.title = """Изменение количества умерших"""
        d_chart_d.x_labels = data_d[0][-2::-1]
        d_chart_d.add(request.form['teamDropdown'], d_data_d)
        d_chart_d = d_chart_d.render_data_uri()

        return render_template('report.html', c_list=countries_list,\
                 case_chart=case_chart, rec_chart=rec_chart, d_chart=d_chart,\
                  case_chart_d=case_chart_d, rec_chart_d=rec_chart_d,\
                   d_chart_d=d_chart_d)
    else:
        return render_template('report.html', c_list=countries_list)


if __name__ == '__main__':
    app.run(debug=True)
    
