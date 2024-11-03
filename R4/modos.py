import configparser
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont

import mysql.connector

#Inicio da classe Modo
class Modo:
    def __init__(self):
        self.modo_atual = 'claro'
        self.config = self.carregar_configuracao()
        if self.config:
            self.icone_modo_escuro = self.config.get('icone_modo_escuro', '')
            self.icone_modo_claro = self.config.get('icone_modo_claro', '')
        else:
            self.icone_modo_escuro = ''
            self.icone_modo_claro = ''

    def carregar_configuracao(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        config.read(config_path)

        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        database = config['mysql']['database']
        port = config['mysql'].getint('port')

        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT icone_modo_escuro, icone_modo_claro FROM config_programa WHERE id = 1')
                config_data = cursor.fetchone()
                return config_data
        except mysql.connector.Error as e:
            print(e)
            return None

    def trocar_modo(self):
        if self.modo_atual == 'claro':
            self.modo_atual = 'escuro'
        else:
            self.modo_atual = 'claro'
        self.atualizar_switch()

    def atualizar_switch(self):
        if self.modo_atual == 'escuro':
            estilo = {
                "icone": self.icone_modo_escuro,
                "botao": {
                    "background-color": "#555555",
                    "color": "#FFFFFF",
                    "border": "2px solid #FFFFFF",
                    "border-radius": "15px",
                    "padding": "5px",
                    "text-align": "right",
                    "padding-right": "30px"
                },
                "botao_checked": {
                    "background-color": "#2E2E2E",
                    "color": "#FFFFFF",
                    "text-align": "right",
                    "padding-right": "30px"
                },
                "widget": {
                    "background-color": "#2E2E2E",
                    "color": "#FFFFFF",
                    "font-family": "fonte_principal",
                    "font-size": "tamanho_fonte"
                },
                "line_edit": {
                    "background-color": "#555555",
                    "color": "#FFFFFF"
                },
                "label": {
                    "color": "#FFFFFF"
                }
            }
        else:
            estilo = {
                "icone": self.icone_modo_claro,
                "botao": {
                    "background-color": "#DDDDDD",
                    "color": "#000000",
                    "border": "2px solid #000000",
                    "border-radius": "15px",
                    "padding": "5px",
                    "text-align": "left",
                    "padding-left": "30px"
                },
                "botao_checked": {
                    "background-color": "#FFFFFF",
                    "color": "#000000",
                    "text-align": "left",
                    "padding-left": "30px"
                },
                "widget": {
                    "background-color": "#FFFFFF",
                    "color": "#000000",
                    "font-family": "fonte_principal",
                    "font-size": "tamanho_fonte"
                },
                "line_edit": {
                    "background-color": "#FFFFFF",
                    "color": "#000000"
                },
                "label": {
                    "color": "#000000"
                }
            }
        return estilo
#Fim da classe Modo

class ModosPrincipais(QMainWindow):
    def __init__(self):
        super().__init__()
        self.modo = Modo()
        self.fonte_padrao = "Arial"
        self.tamanho_fonte_padrao = 18

        self.carregar_preferencias_usuario()
        self.initUI()

    def carregar_preferencias_usuario(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        config.read(config_path)

        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        database = config['mysql']['database']
        port = config['mysql'].getint('port')

        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT modo_tela, fonte_perso, tamanho_fonte_perso FROM preferenciais_usuarios WHERE usuario_id = %s', (1,))
                preferencia = cursor.fetchone()
                if preferencia:
                    self.modo.modo_atual = 'escuro' if preferencia['modo_tela'] == 1 else 'claro'
                    self.fonte_padrao = preferencia['fonte_perso'] if preferencia['fonte_perso'] else self.fonte_padrao
                    self.tamanho_fonte_padrao = preferencia['tamanho_fonte_perso'] if preferencia['tamanho_fonte_perso'] else self.tamanho_fonte_padrao
        except mysql.connector.Error as e:
            print(f"Erro ao carregar preferência de modo: {e}")

    def initUI(self):
        self.setWindowTitle("Modo Claro/Escuro")

        self.switch_button = QPushButton("Trocar Modo", self)
        self.switch_button.clicked.connect(self.trocar_modo)

        layout = QVBoxLayout()
        layout.addWidget(self.switch_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.aplicar_modo()

    def trocar_modo(self):
        self.modo.trocar_modo()
        self.salvar_preferencia_usuario()
        self.aplicar_modo()

    def salvar_preferencia_usuario(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        config.read(config_path)

        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        database = config['mysql']['database']
        port = config['mysql'].getint('port')

        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conn:
                cursor = conn.cursor()
                modo_tela = 1 if self.modo.modo_atual == 'escuro' else 0
                cursor.execute('UPDATE preferenciais_usuarios SET modo_tela = %s, fonte_perso = %s, tamanho_fonte_perso = %s WHERE usuario_id = %s', 
                               (modo_tela, self.fonte_padrao, self.tamanho_fonte_padrao, 1))
                conn.commit()
        except mysql.connector.Error as e:
            print(f"Erro ao salvar preferência de modo: {e}")

    def aplicar_modo(self):
        estilo = self.modo.atualizar_switch()
        self.setStyleSheet(f"""
        QWidget {{
            background-color: {estilo["widget"]["background-color"]};
            color: {estilo["widget"]["color"]};
            font-family: {self.fonte_padrao};
            font-size: {self.tamanho_fonte_padrao}px;
        }}
        QPushButton {{
            background-color: {estilo["botao"]["background-color"]};
            color: {estilo["botao"]["color"]};
        }}
        QLineEdit {{
            background-color: {estilo["line_edit"]["background-color"]};
            color: {estilo["line_edit"]["color"]};
        }}
        QLabel {{
            color: {estilo["label"]["color"]};
        }}
        """)
        if self.fonte_padrao and self.tamanho_fonte_padrao:
            self.setFont(QFont(self.fonte_padrao, self.tamanho_fonte_padrao))

    def carregar_fontes_personalizadas(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        config.read(config_path)

        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        database = config['mysql']['database']
        port = config['mysql'].getint('port')

        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT fonte_perso, tamanho_fonte_perso, fonte_alterada, tamanho_fonte_alterado FROM preferenciais_usuarios WHERE usuario_id = %s', (1,))
                preferencia = cursor.fetchone()
                if preferencia:
                    if preferencia['fonte_alterada'] == 0 or preferencia['tamanho_fonte_alterado'] == 0:
                        cursor.execute('SELECT fonte_padrao, tamanho_fonte_padrao FROM config_programa WHERE id = 1')
                        config_programa = cursor.fetchone()
                        if config_programa:
                            self.fonte_padrao = config_programa['fonte_padrao'] if preferencia['fonte_alterada'] == 0 else preferencia['fonte_perso']
                            self.tamanho_fonte_padrao = config_programa['tamanho_fonte_padrao'] if preferencia['tamanho_fonte_alterado'] == 0 else preferencia['tamanho_fonte_perso']
                    else:
                        self.fonte_padrao = preferencia['fonte_perso']
                        self.tamanho_fonte_padrao = preferencia['tamanho_fonte_perso']
        except mysql.connector.Error as e:
            print(f"Erro ao carregar fontes personalizadas: {e}")

    def initUI(self):
        self.carregar_fontes_personalizadas()
        self.setWindowTitle("Modo Claro/Escuro")

        self.switch_button = QPushButton("Trocar Modo", self)
        self.switch_button.clicked.connect(self.trocar_modo)

        layout = QVBoxLayout()
        layout.addWidget(self.switch_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.aplicar_modo()
        
if __name__ == "__main__":
    app = QApplication([])
    window = ModosPrincipais()
    window.show()
    app.exec_()
