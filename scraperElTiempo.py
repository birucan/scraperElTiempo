from bs4 import BeautifulSoup
import csv
import html5lib
from urllib.request import urlopen
import schedule
import time
import datetime
import redis
import os
import requests

class articulo:
    titulo=''
    link=''
    contenido=''

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"

def scrape():
    listaArticulos=[]
    log("solicitando principal")
    page = request("http://eltiempo.com")

    soup = BeautifulSoup( page , 'html5lib')

    for unArticulo in soup.find_all('div',class_="main_article"):
        nuevoArticulo=articulo()
        nuevoArticulo.titulo=unArticulo.a.string
        nuevoArticulo.link=unArticulo.a['href']
        nuevoArticulo.contenido=""

        is_relative_article_link = nuevoArticulo.link.startswith('/')
        if is_relative_article_link:
            nuevoArticulo.link = "http://www.eltiempo.com" + nuevoArticulo.link
        noodles = BeautifulSoup(request(nuevoArticulo.link),'html5lib')
        nuevoArticulo.contenido = (noodles.find('div',id="contenido"))
        listaArticulos.append(nuevoArticulo)

    elcsv = serialize_articles(listaArticulos)
    store(elcsv)
    print(datetime.datetime.now())

def request(url):
    log("requesting " + url)
    custom_headers = {'user-agent' : USER_AGENT , 'accept': "text/html;charset=UTF-8"  }
    response = requests.get(url , headers = custom_headers)
    response.encoding="utf-8"
    return response.text



def log(algo):
    prefix = '[' + timestamp() + '] '
    print( prefix + algo)

def timestamp():
    return datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")


def serialize_articles(lista):
    articulos = "titulo,link,contenido \n"
    articulos += map(serialize_article, lista)
    return '\n'.join(articulos)

def serialize_article(article):
    line_elements = [
        str(article.titulo),
        str(article.link),
        str(article.contenido)
    ]
    final_line = ','.join(line_elements)
    return final_line

def store(content):
    r = redis.from_url(os.environ.get('REDIS_URL'))
    r.set('news' , content.encode('utf8'))



scrape()
schedule.every(5).minutes.do(scrape)
while True:
    schedule.run_pending()
    time.sleep(1)
