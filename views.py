from flask import Flask
import requests
from bs4 import BeautifulSoup
from flask import render_template

# тест-ссылки
# https://fishki.net/video/ <-- есть видео

app = Flask(__name__)


@app.route('/')
def index():
    context = engine()
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
        cleaned_context['links'].append(
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


if __name__ == "__main__":
    app.run()
