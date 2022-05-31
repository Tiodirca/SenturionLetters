from threading import Thread
import time
# import necessario para usar o PYQT
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import QtCore

from src.Controller import Textos
from src.Controller.Servicos import Servicos_pesquisa_letra
from src.Controller.Gerar_arquivo import gerar_slides
from src.View.tela_principal import Ui_TelaPrincipal
from PyQt5 import QtWidgets

from src.Controller.Tela_baixar_audio import AplicacaoTelaBaixarAudio

retorno_pesquisa = ""
retorno_titulo_letra = ""
pesquisa_usuario = ""
contador_pesquisa = 0
tipo_modelo_slide = Textos.modelo_geral


def exibir_mensagens(mensagem):
    # metodo para exibir mensagem ao usuario
    mbox = QMessageBox()
    mbox.setIcon(QMessageBox.Warning)
    mbox.setText(mensagem)
    mbox.setWindowTitle("Aviso")
    mbox.setStandardButtons(QMessageBox.Ok)
    mbox.exec()


def mudar_estado_radio(item):
    # metodo para mudar estado o radio button
    global tipo_modelo_slide
    if item.text() == "Modelo Geral":
        if item.isChecked():
            tipo_modelo_slide = Textos.modelo_geral
        else:
            tipo_modelo_slide = ''
    if item.text() == "Modelo Geração Fire":
        if item.isChecked():
            tipo_modelo_slide = Textos.modelo_geracao
        else:
            tipo_modelo_slide = ''


class Aplicacao_tela_principal(QMainWindow, Ui_TelaPrincipal, Thread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.leganda_tipo_slide = None
        self.radio_slide_frase = None
        self.radio_slide_verso = None
        self.janela_baixar_audio = None
        super().setupUi(self)
        # definindo acao para o botao
        self.btn_pesquisar.clicked.connect(lambda: self.chamar_fazer_pesquisa())
        self.btn_salvar.clicked.connect(
            lambda: self.chamar_tela_salvar_arquivo())
        self.barra_progresso.setVisible(False)
        self.radio_modelo_geral.setChecked(True)
        self.radio_geracao_fire.toggled.connect(
            lambda: mudar_estado_radio(self.radio_geracao_fire))
        self.radio_modelo_geral.toggled.connect(
            lambda: mudar_estado_radio(self.radio_modelo_geral))
        self.ocultar_campo_tipo_modelo()
        self.barra_progresso.setStyleSheet("QProgressBar "
                                           "{"

                                           "border-radius:10px;"
                                           "}"
                                           "QProgressBar::chunk"
                                           "{"
                                           "background-color : green;"
                                           "border-radius:7px;"
                                           "}"
                                           )

        self.btn_baixar_musica.clicked.connect(lambda: self.chamar_tela_baixar_audio())

    def chamar_tela_baixar_audio(self):
        # metodo para chamar a outra tela
        self.janela_baixar_audio = AplicacaoTelaBaixarAudio()
        self.janela_baixar_audio.show()

    def ocultar_campo_tipo_modelo(self):
        # metodo para ocultar campos
        self.radio_modelo_geral.setVisible(False)
        self.radio_geracao_fire.setVisible(False)
        self.descricao_tipo_modelo.setVisible(False)
        self.icon_geracao_fire.setVisible(False)
        self.icon_modelo_geral.setVisible(False)

    def ocultar_campo_tipo_slide(self):
        # metodo para ocultar campos
        self.radio_slide_verso.setVisible(False)
        self.radio_slide_frase.setVisible(False)
        self.leganda_tipo_slide.setVisible(False)

    def pegar_letra_editada(self):
        # metodo para pegar a letra completa apos o usuario editar
        letra_editada = []
        for estrofes in range(self.lista_letra.count()):  # pegando os itens da lista
            # adicionando os itens em outra lista pegando o texto dela
            letra_editada.append(self.lista_letra.item(estrofes).text())
        return letra_editada

    def chamar_gerar_arquivo_slides(self):
        # metodo para chamar metodo para gerar o arquivo de slides
        # abrindo tela para o usuario selecionar o caminho onde sera salvo o arquivo
        # a variavel vai receber o caminho junto ao nome da musica e o formato que sera salvo
        caminho_arquivo = \
            QtWidgets.QFileDialog.getSaveFileName(self, Textos.salvar_arquivo, retorno_titulo_letra, Textos.tipo_arquivo
                                                  )[0]
        if caminho_arquivo != "":
            self.barra_progresso.setVisible(True)
            for interacao in range(100):
                time.sleep(0.01)
                self.barra_progresso.setValue(interacao + 2)
            retorno_metodo = gerar_slides(self.pegar_letra_editada(), retorno_titulo_letra, tipo_modelo_slide,
                                          caminho_arquivo)
            if retorno_metodo:
                self.barra_progresso.setVisible(False)
                exibir_mensagens(Textos.arquivo_gerado)

    def iniciar_pesquisa_web(self, numero_for):
        # metodo para iniciar a pesquisa na web e exibir a barra de progresso
        # criando uma nova thread para realizar a pesquisa na web
        class Thead_pesquisa(Thread):
            def __init__(self):
                Thread.__init__(self)

            def run(self):
                global pesquisa_usuario
                global retorno_pesquisa
                global contador_pesquisa
                global retorno_titulo_letra
                # definindo que as variaveis vao receber o retorno dos seguintes metodos
                retorno_pesquisa = Servicos_pesquisa_letra.realizar_pesquisa(
                    pesquisa_usuario)
                retorno_titulo_letra = Servicos_pesquisa_letra.retornar_titulo_letra()
                contador_pesquisa += 1

        iniciar_thead = Thead_pesquisa()
        iniciar_thead.start()

        self.barra_progresso.setVisible(True)
        for interacao in range(numero_for):
            time.sleep(0.01)
            self.barra_progresso.setValue(interacao + 2)

    def chamar_tela_salvar_arquivo(self):
        # metodo para chamar tela de salvamento do arquivo
        # verificando antes de chamar a tela se a variavel que recebe o valor do input esta vazia
        global retorno_pesquisa
        if not retorno_pesquisa:
            retorno_pesquisa = ""
            exibir_mensagens(Textos.txt_erro_btn_salvar)
        elif Textos.erro_pesquisa in retorno_pesquisa:
            retorno_pesquisa = ""
            exibir_mensagens(Textos.txt_erro_btn_salvar)
        elif Textos.erro_conexao in retorno_pesquisa:
            retorno_pesquisa = ""
            exibir_mensagens(Textos.txt_erro_btn_salvar)
        else:
            self.chamar_gerar_arquivo_slides()

    def chamar_fazer_pesquisa(self):
        # metodo para resetar valores das variaveis e chamar metodo da pesquisa
        global retorno_pesquisa
        global pesquisa_usuario
        global contador_pesquisa
        retorno_pesquisa = ""
        pesquisa_usuario = ""
        contador_pesquisa = 0
        self.label_nome_letra.setText("")
        self.ocultar_campo_tipo_modelo()
        self.fazer_pesquisa()

    def fazer_pesquisa(self):
        # metodo para realizar a pesquisa do que o usuario digitou
        # pegando o que o usuario digitou no campo
        global pesquisa_usuario
        pesquisa_usuario = self.input_barra_pesquisa.text()
        if not pesquisa_usuario:  # verificando se o input nao esta vazio
            exibir_mensagens(Textos.txt_erro_btn_pesquisa)
        else:
            self.btn_pesquisar.setEnabled(False)
            self.btn_salvar.setEnabled(False)
            self.input_barra_pesquisa.setEnabled(False)
            # limpando a lista antes de adicionar elementos nela
            self.lista_letra.clear()
            if contador_pesquisa == 0:  # verificando se o contador e igual a zero para iniciar metodo
                self.iniciar_pesquisa_web(100)  # chamando metodo para realizar pesquisa na web
                self.fazer_pesquisa()  # chamando o proprio metodo
            else:
                global retorno_pesquisa
                if not retorno_pesquisa:  # verificando caso a variavel esteja vazia chamar o proprio metodo
                    self.fazer_pesquisa()
                else:
                    if Textos.erro_pesquisa in retorno_pesquisa:
                        retorno_pesquisa = ""
                        exibir_mensagens(Textos.txt_erro_pesquisa_nao_encontrada)
                        self.btn_pesquisar.setEnabled(True)
                        self.barra_progresso.setVisible(False)
                        self.input_barra_pesquisa.setEnabled(True)
                        self.btn_salvar.setEnabled(True)
                    elif Textos.erro_conexao in retorno_pesquisa:
                        retorno_pesquisa = ""
                        exibir_mensagens(Textos.txt_erro_sem_conexao)
                        self.btn_pesquisar.setEnabled(True)
                        self.btn_salvar.setEnabled(True)
                        self.barra_progresso.setVisible(False)
                        self.input_barra_pesquisa.setEnabled(True)
                    else:
                        retorno_pesquisa.pop(0)  # removendo o primeiro index da lista
                        # adicionando cada linha do array list retornado na lista para exibir
                        for verso in retorno_pesquisa:
                            self.lista_letra.setSpacing(10)
                            self.lista_letra.addItem(verso.replace('</p>', ' ').replace(
                                '<p>', 'A').replace('</div>', '').replace('<br/>', '\n'))
                        # definindo que cada index da lista podera ser editavel
                        for index in range(self.lista_letra.count()):
                            item = self.lista_letra.item(index)
                            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                        self.radio_modelo_geral.setVisible(True)
                        self.radio_geracao_fire.setVisible(True)
                        self.descricao_tipo_modelo.setVisible(True)
                        self.icon_geracao_fire.setVisible(True)
                        self.icon_modelo_geral.setVisible(True)
                        self.btn_pesquisar.setEnabled(True)
                        self.barra_progresso.setVisible(False)
                        self.btn_salvar.setEnabled(True)
                        self.input_barra_pesquisa.setEnabled(True)
                        self.label_nome_letra.setText(retorno_titulo_letra)
