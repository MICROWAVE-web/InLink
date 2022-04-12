import os
import random
import shutil
import string
import urllib.request
from itertools import groupby
from urllib.error import HTTPError
from progress.bar import IncrementalBar
import requests
from bs4 import BeautifulSoup
from flask import Flask, url_for, redirect, flash, render_template, request, Response
from flask_login import LoginManager, current_user, logout_user, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy.exc import DatabaseError
from tqdm import tqdm
from werkzeug.urls import url_parse

from forms import LoginForm, RegistrationForm, ServiceForm

app = Flask(__name__)
login = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
is_authenticated = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect(app)
csrf.init_app(app)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/service', methods=['GET', 'POST'])
def service():
    form = ServiceForm()
    if form.validate_on_submit():
        url = form.url.data
        context = engine(url)
        return render_template('index.html', **context)
    context = {
        'is_authenticated': is_authenticated,
        'form': form
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


def engine(url='https://fishki.net/video/', local_uses=False):
    response = requests.get(url)
    with urllib.request.urlopen(url) as urllib_adress:
        load_time = f'{round(response.elapsed.total_seconds(), 3)} сек.'
        content_length = human_read_format(urllib_adress.info()['Content-Length'])
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

    _clean_context = {
        'pictures': [],
        'videos': [],
        'links': [],
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
        _clean_context['pictures'].append(src)

    for link in context['videos']:
        source = link.find('source')
        src = source.get('src')
        if src.startswith('//'):
            src = 'https:' + src
        cleaned_context['videos'].append(
            f'<video controls="controls"><source src="{src}"></video>'
        )
        _clean_context['videos'].append(src)

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
        _clean_context['links'].append(href + '\n')
    cleaned_context['images'] = [el for el, _ in groupby(cleaned_context['images'])]
    cleaned_context['videos'] = list(set(cleaned_context['videos']))
    if local_uses:
        return _clean_context
    return cleaned_context


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('service'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('service')
        return redirect(next_page)
    context = {
        'form': LoginForm()
    }
    return render_template("login.html", title="Вход", **context)


@app.route("/logout", )
def logout():
    logout_user()
    return redirect(url_for('service'))


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            return redirect(url_for('login'))
        except DatabaseError as e:
            db.session.rollback()
            return redirect(url_for('registration'))

    context = {
        'form': RegistrationForm()
    }
    return render_template("registration.html", title="Регистрация", **context)


def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


@app.route("/save_files", methods=['POST'])
@csrf.exempt
def save_files():
    url = request.form.get('url')
    links = request.form.get('links')
    pictures = request.form.get('pictures')
    videos = request.form.get('videos')
    random_hash = generate_random_string(10)
    if not url:
        page_not_found(Exception('Нет ссылки'))
        return -1
    if not (links or pictures or videos):
        page_not_found(Exception('Нечего скачивать'))
        return -1
    context_files = engine(url=url, local_uses=True)
    os.mkdir(f'{random_hash}_files')
    os.mkdir(f'{random_hash}_files/links')
    os.mkdir(f'{random_hash}_files/pictures')
    os.mkdir(f'{random_hash}_files/videos')
    for type_files in context_files:
        if type_files == 'links':
            with open(f'{random_hash}_files/links/links.txt', 'w') as f:
                f.writelines(context_files[type_files])
            continue
        if type_files == 'pictures':
            if not pictures:
                continue
        if type_files == 'videos':
            if not videos:
                continue
        for index, file in enumerate(tqdm(context_files[type_files]), start=1):
            try:
                file_extension = file.split('.')[-1]
                r = requests.get(file)
                with open(f'{random_hash}_files/{type_files}/file_{index}.{file_extension}', "wb") as code:
                    code.write(r.content)
            except HTTPError:
                pass
            except FileNotFoundError:
                pass
            except OSError:
                pass

    zip_name = f'zips\\{random_hash}'
    directory_name = f'{random_hash}_files'
    shutil.make_archive(zip_name, 'zip', directory_name)
    filepath = zip_name + '.zip'
    with open(filepath, 'rb') as f:
        data = f.readlines()
    os.remove(filepath)
    for root, dirs, files in os.walk(directory_name, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(directory_name)
    return Response(data, headers={
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename=%s;' % filepath.split('/')[-1]
    })


if __name__ == "__main__":
    from models import initializing, User

    initializing()
    app.run()
