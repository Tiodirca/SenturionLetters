# import a biblioteca usada para consultar uma URL
import urllib.request

# import as funções BeautifulSoup para analisar os dados retornados do site
import requests as requests
from bs4 import BeautifulSoup
# import a biblioteca usada para consultar uma URL
from urllib.request import Request, urlopen

from src.Controller import Textos

titulo_video = ""
lista_resultado = []


def verificar_conexao():
    # metodo para verificar se existe conecao com internet
    url = 'https://www.google.com'
    timeout = 10
    try:
        requests.get(url, timeout=timeout)
        return True
    except:
        return False


def realizar_pesquisa_video(pesquisa_usuario):
    # metodo para realizar a pesquisa no google
    global lista_resultado
    lista_resultado = []
    if not verificar_conexao():  # verificando se o usuario tem conexao com a internet
        return Textos.erro_conexao
    else:
        # especificando a URL
        resultado = []
        pesquisa = str(pesquisa_usuario.replace(' ', '+').encode('utf-8'))
        req = Request(
            'https://www.google.com/search?q=' + pesquisa,
            headers={'User-Agent': 'Mozilla/5.0'})
        # lendo a pagina html
        web_pagina = urlopen(req).read()

        # Parse do html na variável e armazenando no formato BeautifulSoup
        soup = BeautifulSoup(web_pagina, 'html5lib')
        # Insirindo a classe que deve ser feita a pesquisa
        lista_items = soup.find_all(attrs="kCrYT")
        # pegando todos os elementos que a pagina html retorna
        for site in lista_items:
            # pegando todos os links disponiveis e reescrevendo o caractere da string para o caracte desejado
            if "www.youtube.com" in site.prettify():
                #.get('href')[7:].split('&')[0].replace('%3F', '?').replace('%3D', '=')
                resultado.append(
                    site.find_next('a'))
                for elemento in resultado:
                    if elemento not in lista_resultado:
                        lista_resultado.append(elemento)
        # verificando caso a variavel seja vazia
        if not lista_resultado:
            return Textos.erro_pesquisa
        else:
            return lista_resultado


def retornar_nome_video():
    # metodo para retornar o nome da letra
    global titulo_video
    return titulo_video
