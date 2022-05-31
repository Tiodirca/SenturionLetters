# import a biblioteca usada para consultar uma URL
import urllib.request

# import as funções BeautifulSoup para analisar os dados retornados do site
import requests as requests
from bs4 import BeautifulSoup
# import a biblioteca usada para consultar uma URL
from urllib.request import Request, urlopen

from src.Controller import Textos

titulo_letra = ""
letra_completa = ""


def verificar_conexao():
    # metodo para verificar se existe conecao com internet
    url = 'https://www.google.com'
    timeout = 10
    try:
        requests.get(url, timeout=timeout)
        return True
    except:
        return False


def pegar_letra_completa(link_letra):
    # metodo para pegar a letra completa
    # Consulta o site e retorna o html para a variável
    pagina_html = urllib.request.urlopen(link_letra)
    # Parse do html da variável e armazenando no formato BeautifulSoup
    soup = BeautifulSoup(pagina_html, 'html5lib')
    # pegando todos os elementos que contem dentro da tag que contem a class passada como parametro
    lista_items = soup.find('div', attrs={'class': 'cnt-letra p402_premium'})
    titulo_letra_site = soup.find('div', attrs={'class': 'cnt-head_title'})
    global letra_completa
    # a variavel vai receber uma lista dividida pelo parametro passado ao split
    letra_completa = str(lista_items).split('<p>')
    global titulo_letra
    # definindo que a varivel vai receber o seguinte valor comecando de um determidado index
    titulo_letra = str(titulo_letra_site)[33:].split(
        '/">')[0].replace('</h1> <h2> <a href="/', '_').replace('-', ' ').replace('_', ' - ')
    return letra_completa


def retornar_titulo_letra():
    # metodo para retornar o nome da letra
    global titulo_letra
    return titulo_letra.title()


def realizar_pesquisa(pesquisa_usuario):
    # metodo para realizar a pesquisa no google
    if not verificar_conexao():  # verificando se o usuario tem conexao com a internet
        return Textos.erro_conexao
    else:
        # especificando a URL
        resultado = ''
        pesquisa = str(pesquisa_usuario.replace(' ', '+').encode('utf-8'))
        req = Request(
            'https://www.google.com/search?q=' +
            pesquisa,
            headers={'User-Agent': 'Mozilla/5.0'})
        # lendo a pagina html
        web_pagina = urlopen(req).read()

        # Parse do html na variável e armazenando no formato BeautifulSoup
        soup = BeautifulSoup(web_pagina, 'html5lib')
        # Insirindo a classe que deve ser feita a pesquisa
        lista_items = soup.find_all(attrs="kCrYT")
        # pegando todos os elementos que a pagina html retorna
        for site in lista_items:
            # verificando se o html retornado contem o seguinte site
            if "www.letras.mus.br" in site.prettify():
                # definindo que a variavel vai receber o valor que contem na seguinte tag
                resultado = site.find_next('a')
        # verificando caso a variavel seja vazia
        if not resultado:
            return Textos.erro_pesquisa
        else:
            # definindo que o metodo vai retornar uma string comecando do index 7 e finalzando no index que conter &
            # para tal pega-se somente o primeiro index da lista gerada pelo split
            return pegar_letra_completa(resultado.get('href')[7:].split('&')[0])
