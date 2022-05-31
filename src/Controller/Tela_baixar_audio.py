from threading import Thread

import requests
from PyQt5.QtWidgets import QMainWindow, QMessageBox
import time

from PyQt5 import QtWidgets
from src.Controller import Textos
from src.View.tela_baixar_audio import Ui_TelaBaixarAudio
from src.Controller.Servicos import Servicos_pesquisa_video
# importa para baixar
import youtube_dl

pesquisa_audio = ""
contador_pesquisa = 0
retorno_pesquisa = ""
retorno_download_concluido = ""
video_informacoes = ""
caminho_salvar = ""
caminho_arquivo = ""
nome_arquivo = ""
links_final = []
id_item_lista = -1


def exibir_mensagens(mensagem):
    # metodo para exibir caixa de mensagem ao usuario
    mbox = QMessageBox()
    mbox.setIcon(QMessageBox.Warning)
    mbox.setText(mensagem)
    mbox.setWindowTitle("Aviso")
    mbox.setStandardButtons(QMessageBox.Ok)
    mbox.exec()


def verificar_conexao():
    # metodo para verificar se existe conecao com internet
    url = 'https://www.google.com'
    timeout = 10
    try:
        requests.get(url, timeout=timeout)
        return True
    except:
        return False


def pesquisar_video(caixa_pesquisa):
    # metodo para realizar a busca
    class TheadPesquisa(Thread):  # colocando em thead separada para evitar travar thead principal
        def __init__(self):
            Thread.__init__(self)

        def run(self):
            global video_informacoes, contador_pesquisa, retorno_pesquisa
            if "youtube.com" in caixa_pesquisa:  # pesquisa via URL
                retorno_pesquisa = pegar_info_video(caixa_pesquisa)
            else:  # pesquisa via nome
                retorno_pesquisa = Servicos_pesquisa_video.realizar_pesquisa_video(caixa_pesquisa)
            contador_pesquisa += 1
            return retorno_pesquisa

    iniciar_thead_pesquisa = TheadPesquisa()
    iniciar_thead_pesquisa.start()


def pegar_info_video(link):
    # metodo para pegar informacoes do video que sera convertido
    global video_informacoes, nome_arquivo
    try:
        video_informacoes = youtube_dl.YoutubeDL().extract_info(
            url=str(link), download=False
        )
        nome_arquivo = f"{video_informacoes['title']}.mp3"  # pegando somente o titulo do video
        return nome_arquivo
    except:
        return Textos.erro_pesquisa


class AplicacaoTelaBaixarAudio(QMainWindow, Ui_TelaBaixarAudio):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.barra_progresso_baixar.setStyleSheet("QProgressBar "
                                                  "{"

                                                  "border-radius:10px;"
                                                  "}"
                                                  "QProgressBar::chunk"
                                                  "{"
                                                  "background-color : green;"
                                                  "border-radius:7px;"
                                                  "}"
                                                  )
        self.barra_progresso_baixar.setVisible(False)
        self.btn_baixar_audio.setVisible(False)
        self.btn_baixar_audio.clicked.connect(lambda: self.chamar_baixar_audio())
        self.btn_pesquisar_audio.clicked.connect(lambda: self.pegar_texto_digitado())
        self.lista_musicas_baixar.itemClicked.connect(self.pegar_id_item_lista)

    def pegar_id_item_lista(self):
        # metodo para pegar  o id do item da lista
        global id_item_lista
        id_item_lista = self.lista_musicas_baixar.currentRow()

    def pegar_texto_digitado(self):
        # metodo para pegar texto que foi digitado e setar valores iniciais para as variaveis
        global pesquisa_audio, contador_pesquisa, retorno_pesquisa, nome_arquivo, links_final
        pesquisa_audio = ""
        retorno_pesquisa = ""
        nome_arquivo = ""
        contador_pesquisa = 0
        links_final = []
        self.btn_baixar_audio.setVisible(False)
        self.lista_musicas_baixar.clear()
        self.label_avisos_download.setText("")
        pesquisa_audio = self.input_barra_pesquisa_audio.text()

        if not pesquisa_audio:  # caso a variavel esteja vazia exibir mensagem de erro
            exibir_mensagens(Textos.txt_erro_btn_pesquisa_audio)
        else:
            self.chamar_pesquisa_video()

    def chamar_pesquisa_video(self):
        # metodo para fazer chmar a pesquisa de video a depender do tipo de pesquisa
        self.incrementar_barra_progresso()
        if not retorno_pesquisa:
            pesquisar_video(pesquisa_audio)
        else:
            self.barra_progresso_baixar.setVisible(False)
            if Textos.erro_conexao in retorno_pesquisa:
                exibir_mensagens(Textos.txt_erro_sem_conexao)
            else:
                self.btn_baixar_audio.setVisible(True)
                if "youtube.com" in pesquisa_audio:
                    if Textos.erro_pesquisa in retorno_pesquisa:
                        self.btn_baixar_audio.setVisible(False)
                        exibir_mensagens(Textos.txt_erro_pesquisa_audio_nao_encontrada)
                    else:
                        self.lista_musicas_baixar.addItem(retorno_pesquisa.replace('.mp3', ''))
                elif Textos.erro_pesquisa in retorno_pesquisa:
                    self.btn_baixar_audio.setVisible(False)
                    exibir_mensagens(Textos.txt_erro_pesquisa_audio_nao_encontrada)
                else:
                    nome_videos = []
                    links = []
                    for item in retorno_pesquisa:
                        if item not in nome_videos:
                            # colocando somente os links em uma lista
                            links.append(item.get('href')[7:].split('&')[0].replace('%3F', '?').replace('%3D', '='))
                            # coloando somente o nome dos videos em uma lista
                            nome_videos.append(
                                str(item.find('h3')).replace(
                                    '<h3 class="zBAuLc l97dzf"><div class="BNeawe vvjwJb AP7Wnd">',
                                    '').replace('</div></h3>', ''))

                    global links_final
                    # removendo qualquer link que seja repetido e adicionando em uma nova lista
                    for remove_link_repetido in links:
                        if remove_link_repetido not in links_final:
                            links_final.append(remove_link_repetido)
                    # removendo da lista os index que contem informacoes desnecessarias
                    for remove in nome_videos:
                        if "None" in remove:
                            nome_videos.remove(remove)
                    self.lista_musicas_baixar.addItems(nome_videos)
        if contador_pesquisa == 0:  # caso seja vazio quer dizer que a pesquisa ainda nao retornou nada
            self.chamar_pesquisa_video()

    def desativar_botoes(self):
        # metodo para desativar os botoes
        self.btn_pesquisar_audio.setEnabled(False)
        self.btn_baixar_audio.setEnabled(False)
        self.input_barra_pesquisa_audio.setEnabled(False)
        self.lista_musicas_baixar.setEnabled(False)

    def chamar_baixar_audio(self):
        # metodo para chamar metodo para baixar audio do video
        if not retorno_pesquisa:  # caso seja vazio retornar erro
            exibir_mensagens(Textos.txt_erro_btn_salvar_audio)
        else:
            global id_item_lista
            if id_item_lista == -1:  # caso seja vazio retornar erro
                exibir_mensagens(Textos.erro_selecao_item_lista)
            else:
                global caminho_arquivo, nome_arquivo
                if not verificar_conexao():
                    exibir_mensagens(Textos.txt_erro_sem_conexao)
                else:
                    # definindo como sera pego o nome do arquivo mediante o tipo de pesquisa realizada
                    if not nome_arquivo:  # pesquisa via URL
                        self.incrementar_barra_progresso()
                        nome = pegar_info_video(links_final[id_item_lista])
                        self.barra_progresso_baixar.setVisible(False)
                    else:  # pesquisa via nome do video
                        nome = nome_arquivo
                    # caminho de onde sera salvo o arquivo
                    caminho_arquivo = QtWidgets.QFileDialog.getSaveFileName(self, Textos.salvar_arquivo, nome,
                                                                            Textos.tipo_audio)[0]
                    if caminho_arquivo != "":  # caso seja vazio quer dizer que o usuario cancelou
                        self.baixar_audio_video(caminho_arquivo)  # metodo para baixar video

    def baixar_audio_video(self, caminho):
        # metodo para baixar audio do video
        self.barra_progresso_baixar.setVisible(True)
        self.barra_progresso_baixar.setValue(0)
        self.barra_progresso_baixar.setTextVisible(True)
        self.barra_progresso_baixar.setMaximum(1000)
        self.desativar_botoes()
        self.label_avisos_download.setText(Textos.txt_download_iniciado)
        # opcoes do video que sera baixado
        opcoes = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'progress_hooks': [self.atualizar_barra_progresso_download],
            'outtmpl': caminho,
        }

        # colocando o processo para ser executado em outra thead evitando a tela travar
        class TheadDownload(Thread):
            def __init__(self):
                Thread.__init__(self)

            def run(self):
                with youtube_dl.YoutubeDL(opcoes) as ydl:
                    ydl.download([video_informacoes["webpage_url"]])

        iniciar_thead_download = TheadDownload()
        iniciar_thead_download.start()

    def atualizar_barra_progresso_download(self, d):
        # metodo para atualizar a barra de progresso durante o download do arquivo
        if d['status'] == 'finished':  # caso o download tenha terminado
            self.barra_progresso_baixar.setVisible(False)
            self.btn_baixar_audio.setEnabled(True)
            self.btn_pesquisar_audio.setEnabled(True)
            self.input_barra_pesquisa_audio.setEnabled(True)
            self.lista_musicas_baixar.setEnabled(True)
            self.label_avisos_download.setText(Textos.txt_download_concluido)
            global nome_arquivo
            nome_arquivo = ""
        elif d['status'] == 'downloading':  # caso esta ainda baixando
            # pegando a porcentagem do download
            porcentagem = str(d['_percent_str']).replace('%', '').replace('.', '')
            if int(porcentagem) > 50:
                self.label_avisos_download.setText(Textos.txt_download_aguarde)
            self.barra_progresso_baixar.setValue(int(porcentagem))

    def incrementar_barra_progresso(self):
        # metodo para exibir a barra de progresso e incrementar um valor para a mesma
        self.barra_progresso_baixar.setVisible(True)
        self.barra_progresso_baixar.setTextVisible(False)
        self.barra_progresso_baixar.setMaximum(100)
        for interacao in range(100):
            time.sleep(0.01)
            self.barra_progresso_baixar.setValue(interacao + 2)
