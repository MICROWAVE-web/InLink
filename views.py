import requests
from bs4 import BeautifulSoup
from flask import Flask, url_for, redirect, make_response
from flask import render_template
from flask import request
from flask_login import current_user

# тест-ссылки
# https://fishki.net/video/ <-- есть видео
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
is_authenticated = False


@app.route('/service')
def service():
    context = engine()
    print(request.method)
    return render_template('index.html', **context)


def engine(url='https://fishki.net/video/'):
    url = url
    response = requests.get(url)
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
        'is_authenticated': is_authenticated
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
            f'<img alt="{alt}" src="{src}"></img>'
        )
        # print("IMG Inner Text is: {}".format(alt))
        # print("IMG src is: {}".format(src))

    for link in context['videos']:
        source = link.find('source')
        src = source.get('src')
        if src.startswith('//'):
            src = 'https:' + src
        cleaned_context['videos'].append(
            f'<video><source src="{src}"></video>'
        )
        # print("VIDEO Inner Text is: {}".format(link.get("title")))
        # print("VIDEO src is: {}".format(src))

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
            f'<a href="{href}"></a>'
        )
        # print("LINK Inner Text is: {}".format(link.text.strip()))
        # print("LINK href is: {}".format(href))
    return cleaned_context


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        language = request.form.get('language')
        framework = request.form.get('framework')
        return redirect(url_for('login'))
    return render_template("login.html", title="Авторизация")


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
    print(is_authenticated)


if __name__ == "__main__":
    from models import initializing, User

    initializing()
    # users = User.query.all()
    # print(users[0].email)

    app.run()
