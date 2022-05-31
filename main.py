import sys

from PyQt5.QtWidgets import QApplication
from src.Controller.Tela_principal import Aplicacao_tela_principal
# pyuic5 tela_principal.ui -o tela_principal.py
# pip install python-pptx
# pip install PyQt5
# pip install beautifulsoup4
# pip install html5lib
# pyuic5 tela_baixar_audio.ui -o tela_baixar_audio.py
# para gerar arquivo executavel instalar pip install pyinstaller
# comando para gerar executavel em um unico arquivo 
# pyinstaller --onefile --windowed .\src\main.py
# depois copiar a pasta src para o diretorio do arquivo .exe criado. 
# deixando somente imagens e modelos_slides na src

if __name__ == "__main__":
    qt = QApplication(sys.argv)
    # instanciando tela para ser executada primeiro
    aplicacao_tela_principal = Aplicacao_tela_principal()
    aplicacao_tela_principal.showMaximized()
    qt.exec_()