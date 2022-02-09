import time
import urllib.request
from itertools import groupby

import requests
from bs4 import BeautifulSoup
from flask import Flask, url_for, redirect, make_response
from flask import render_template
from flask import request
# тест-ссылки
# https://fishki.net/video/ <-- есть видео
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
is_authenticated = False


@app.route('/service', methods=['GET', 'POST'])
def service():
    if request.method == 'POST':
        url = request.form.get('url')
        context = engine(url)
        return render_template('index.html', **context)
    context = {
        'is_authenticated': is_authenticated
    }
    return render_template("service.html", **context)


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('service'))


def human_read_format(size):
    if not size:
        size = 0
    size = int(size)
    if size >= 1024 ** 4:
        return f'{round(size / (1024 ** 4))}ТБ'
    elif size >= 1024 ** 3:
        return f'{round(size / (1024 ** 3))}ГБ'
    elif size >= 1024 ** 2:
        return f'{round(size / (1024 ** 2))}МБ'
    elif size >= 1024:
        return f'{round(size / 1024)}КБ'
    else:
        return f'{round(size)}Б'


def engine(url='https://fishki.net/video/'):
    url = url
    response = requests.get(url)
    with urllib.request.urlopen(url) as urllib_adress:
        load_time = f'{round(response.elapsed.total_seconds(), 3)} сек.'
        content_length = human_read_format(urllib_adress.info()['Content-Length'])
        print(load_time, content_length)
        # print(urllib_adress.info())
    soup = BeautifulSoup(response.content, 'html.parser')
    context = {
        'images': soup.find_all('img'),
        'videos': soup.find_all('video'),
        'links': soup.find_all('a'),
    }
    cleaned_context = {
        'images': [],
        'videos': [],
        'links': [],
        'url': url,
        'is_authenticated': is_authenticated,
        'meta': {
            'load_time': load_time,
            'content_length': content_length,
        }
    }

    for link in context['images']:
        alt = link.get("alt")
        src = link.get("src")
        if src.startswith('data:'):
            continue
        if alt:
            alt = alt.strip()
        if src.startswith('//'):
            src = 'https:' + src
        if '//' not in src:
            src = '//'.join(url.split('/')[:3]) + '/' + src.strip('/')
            src = src.replace('////', '//')
        cleaned_context['images'].append(
            [f'<img alt="{alt}" src="{src}"></img>',
             f'<a target="_blank" href="{src}" class="banner-btn-2" download>Скачать</a>']
        )

    for link in context['videos']:
        source = link.find('source')
        src = source.get('src')
        if src.startswith('//'):
            src = 'https:' + src
        cleaned_context['videos'].append(
            f'<video controls="controls"><source src="{src}"></video>'
        )

    for link in context['links']:
        href = link.get("href")
        if link.text == '' or not href:
            continue
        if ':void' in href:
            continue
        if '//' not in href:
            href = '//'.join(url.split('/')[:3]) + '/' + href.strip('/')
            href = href.replace('////', '//')
        if href.startswith('//'):
            href = 'https:' + href
        cleaned_context['links'].append(
            [href, f'<a target="_blank" class="banner-btn-2" href="{href}">Перейти</a>']
        )
    cleaned_context['images'] = [el for el, _ in groupby(cleaned_context['images'])]
    cleaned_context['videos'] = list(set(cleaned_context['videos']))
    return cleaned_context


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        resp = make_response(redirect(url_for('service')))
        resp.set_cookie('inlink_email', email)
        resp.set_cookie('inlink_password', password)
        return resp
    email = request.form.get('email')
    password = request.form.get('password')
    context = {
        'is_authenticated': is_authenticated
    }
    return render_template("login.html", **context)


@app.route("/logout", )
def logout():
    resp = make_response(redirect(url_for('service')))
    resp.set_cookie('inlink_email', '')
    resp.set_cookie('inlink_password', '')
    context = {
        'is_authenticated': is_authenticated
    }
    return resp


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            print('SUCCESS!')
            resp = make_response(redirect(url_for('login')))
            resp.set_cookie('inlink_email', email)
            resp.set_cookie('inlink_password', password)
            return resp
        except DatabaseError as e:
            print('ERROR!')
            db.session.rollback()
            return redirect(url_for('registration'))

    context = {
        'is_authenticated': is_authenticated
    }
    return render_template("registration.html", title="Регистрация", **context)


@app.before_request
def before_request():
    global is_authenticated
    email = request.cookies.get('inlink_email')
    password = request.cookies.get('inlink_password')
    if bool(email) and bool(password):
        user_object = User.query.filter(
            User.email.like(email),
            User.password.like(password)
        ).all()
        if len(user_object) != 0:
            is_authenticated = True
        else:
            is_authenticated = False
    else:
        is_authenticated = False


if __name__ == "__main__":
    from models import initializing, User

    initializing()
    # users = User.query.all()
    # print(users[0].email)

    app.run()
