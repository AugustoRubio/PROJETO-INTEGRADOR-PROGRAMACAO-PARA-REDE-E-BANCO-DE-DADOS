import sys
import subprocess
import importlib.util
class CheckDependencias:
    @staticmethod
    def check_and_install_dependencies():
        dependencies = {
            "PyQt5": "PyQt5",
            "requests": "requests",
            "nmap": "python-nmap",
            "mysql": "mysql-connector-python"
        }
    
        missing_dependencies = []
        for module, package in dependencies.items():
            if not importlib.util.find_spec(module):
                missing_dependencies.append(package)

        if missing_dependencies:
            print(f"Instalando dependências ausentes: {', '.join(missing_dependencies)}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_dependencies])
        else:
            print("Todas as dependências estão instaladas.")

CheckDependencias.check_and_install_dependencies()

import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QDesktopWidget, QCheckBox, QListWidget, QListWidgetItem, QCalendarWidget, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractScrollArea, QInputDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QMovie, QIcon
from PyQt5.QtCore import Qt, QEvent, QTimer, QByteArray, QThreadPool, QRunnable
from PyQt5.QtGui import QFont, QFontDatabase

import os
import configparser
import requests
#Para evitar erros de variável não definida, inicializamos as variáveis do Scanner de Rede usando o try e except
try:
    from scanner_rede import RedeAtual, ScannerRede as ScannerRedeExterno
except ImportError:
    class RedeAtual:
        def obter_rede_atual(self):
            return None
from datetime import datetime
#Importa as classes do arquivo usuarios.py, que cuida das funções de adicionar, editar, remover e listar usuários do banco de dados
from usuarios import ConfigUsuarios
#Importa as classes do arquivo modos.py, que cuida das funções de trocar o modo de cores do programa
from modos import Modo
#Importa as classes do arquivo criar_db.py, que cuida das funções de criar o banco de dados e verificar se o banco de dados já existe
from criar_db import GerenciadorBancoDados
from config_programa import CarregarConfiguracoes, CarregarPreferenciasUsuario, SalvarConfiguracoes
#Importa as classes do arquivo dashboard.py, que cuida das funções de monitorar o hardware e extrair informações do hardware
from dashboard import MonitorDeHardware, ExtratorDeInfoHardware
from scanner_rede import PingIP, RedeAtual, CarregarResultadosCalendario
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QHeaderView
from modos import ModosPrincipais
import ipaddress

class ScannerRede:
    def __init__(self, portas_selecionadas, escaneamento_rapido):
        self.portas_selecionadas = portas_selecionadas
        self.escaneamento_rapido = escaneamento_rapido
    def escanear(self):
        return [("Host1", "00:11:22:33:44:55", "192.168.1.1", self.portas_selecionadas)]

class VerificadorBancoDados:
    def __init__(self, host, user, password, database, port):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port

    def verificar_ou_criar_bd(self):
        gerenciador_bd = GerenciadorBancoDados(self.host, self.user, self.password, self.database, self.port)
        gerenciador_bd.criar_tabelas()
        print(f"Banco de dados verificado/criado com sucesso: {self.database}")

if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'config.ini'))

host = config['mysql']['host']
user = config['mysql']['user']
password = config['mysql']['password']
database = config['mysql']['database']
port = config['mysql'].getint('port')

verificador_bd = VerificadorBancoDados(host, user, password, database, port)
verificador_bd.verificar_ou_criar_bd()

#Inicio da classe JanelaLogin
class JanelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.modo = Modo()
        self.carregar_configuracoes()
        self.inicializarUI()
        self.timer = QTimer(self)
        try:
            response = requests.get('https://augusto.tec.br/pi/f5.png')
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(response.content))
            self.setWindowIcon(QIcon(pixmap))
        except requests.RequestException as e:
            self.mostrar_erro(f"Erro ao carregar ícone da janela: {e}")

    def carregar_configuracoes(self):
        try:
            carregar_config = CarregarConfiguracoes()
            carregar_config.carregar_configuracoes()
            self.logo_principal = carregar_config.logo_principal
            self.logo_rodape = carregar_config.logo_rodape
            self.fonte_padrao = carregar_config.fonte_padrao
            self.tamanho_fonte_padrao = carregar_config.tamanho_fonte_padrao
            self.modo_global = 1 if carregar_config.modo_atual == 'escuro' else 0
            self.modo.modo_atual = carregar_config.modo_atual
        except Exception as e:
            self.mostrar_erro(f"Erro ao carregar configurações: {e}")

    def inicializarUI(self):
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.layout = QVBoxLayout()

        if self.logo_principal:
            self.label_logo_principal = QLabel(self)
            self.label_logo_principal.setAlignment(Qt.AlignCenter)
            try:
                response = requests.get(self.logo_principal)
                response.raise_for_status()
                image_data = response.content
                if self.logo_principal.endswith('.gif'):
                    self.gif_logo_principal_byte_array = QByteArray(image_data)
                    self.movie_logo_principal = QMovie(self.gif_logo_principal_byte_array)
                    self.label_logo_principal.setMovie(self.movie_logo_principal)
                    self.movie_logo_principal.start()
                else:
                    self.pixmap_logo_principal = QPixmap()
                    self.pixmap_logo_principal.loadFromData(image_data)
                    self.label_logo_principal.setPixmap(self.pixmap_logo_principal.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                self.mostrar_erro(f"Erro ao carregar logo principal: {e}")
            self.layout.addWidget(self.label_logo_principal)

        if self.fonte_padrao and self.tamanho_fonte_padrao:
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))

        self.label_usuario = QLabel('Usuário:', self)
        self.label_usuario.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_usuario, alignment=Qt.AlignCenter)

        self.input_usuario = QLineEdit(self)
        self.input_usuario.setMaximumWidth(300)
        self.input_usuario.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.input_usuario, alignment=Qt.AlignCenter)
        self.input_usuario.setFocus()

        self.label_senha = QLabel('Senha:', self)
        self.label_senha.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_senha, alignment=Qt.AlignCenter)

        self.input_senha = QLineEdit(self)
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setMaximumWidth(300)
        self.input_senha.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.input_senha, alignment=Qt.AlignCenter)

        self.botao_login = QPushButton('Login', self)
        self.botao_login.setMaximumWidth(300)
        self.botao_login.setStyleSheet("margin-left: auto; margin-right: auto;")
        self.botao_login.clicked.connect(self.verificar_login)
        self.layout.addWidget(self.botao_login, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        self.input_senha.returnPressed.connect(self.verificar_login)

        if self.logo_rodape:
            self.label_logo_rodape = QLabel(self)
            self.label_logo_rodape.setAlignment(Qt.AlignCenter)
            try:
                response = requests.get(self.logo_rodape)
                response.raise_for_status()
                image_data = response.content
                self.pixmap_logo_rodape = QPixmap()
                self.pixmap_logo_rodape.loadFromData(image_data)
                self.label_logo_rodape.setPixmap(self.pixmap_logo_rodape.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                self.mostrar_erro(f"Erro ao carregar logo rodapé: {e}")
            self.layout.addWidget(self.label_logo_rodape)

        self.aplicar_modo()

    def verificar_login(self):
        usuario = self.input_usuario.text()
        senha = self.input_senha.text()

        if not usuario or not senha:
            QMessageBox.warning(self, 'Erro', 'Por favor, preencha todos os campos.')
            return

        config_usuarios = ConfigUsuarios(None, host, user, password, database, port)
        try:
            resultado = config_usuarios.verificar_login(usuario, senha)
            if resultado == "alterar_senha":
                self.mostrar_tela_alterar_senha(usuario)
            elif resultado == "login_sucesso":
                self.usuario_logado = self.obter_usuario_logado()
                self.abrir_janela_principal()
        except ValueError as e:
            QMessageBox.warning(self, 'Erro', str(e))
        except ConnectionError as e:
            self.mostrar_erro(str(e))

    def mostrar_tela_alterar_senha(self, usuario):
        self.janela_alterar_senha = QWidget()
        self.janela_alterar_senha.setWindowTitle('Alterar Senha')
        self.janela_alterar_senha.setGeometry(100, 100, 400, 300)
        self.center(self.janela_alterar_senha)

        layout = QVBoxLayout()

        aviso = QLabel('Por favor, altere sua senha no primeiro login.', self.janela_alterar_senha)
        aviso.setAlignment(Qt.AlignCenter)
        layout.addWidget(aviso)

        self.input_nova_senha = QLineEdit(self.janela_alterar_senha)
        self.input_nova_senha.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Nova Senha:', self.janela_alterar_senha))
        layout.addWidget(self.input_nova_senha)

        self.input_confirmar_senha = QLineEdit(self.janela_alterar_senha)
        self.input_confirmar_senha.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Confirmar Nova Senha:', self.janela_alterar_senha))
        layout.addWidget(self.input_confirmar_senha)

        botao_salvar = QPushButton('Salvar', self.janela_alterar_senha)
        botao_salvar.clicked.connect(lambda: self.salvar_nova_senha(usuario))
        layout.addWidget(botao_salvar)

        self.input_confirmar_senha.returnPressed.connect(lambda: self.salvar_nova_senha(usuario))

        self.janela_alterar_senha.setLayout(layout)
        self.janela_alterar_senha.show()

    def center(self, janela):
        qr = janela.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        janela.move(qr.topLeft())

    def salvar_nova_senha(self, usuario):
        nova_senha = self.input_nova_senha.text()
        confirmar_senha = self.input_confirmar_senha.text()

        if not nova_senha or not confirmar_senha:
            self.mostrar_erro("Todos os campos são obrigatórios.")
            return

        if nova_senha != confirmar_senha:
            self.mostrar_erro("As senhas não coincidem.")
            return

        config_usuarios = ConfigUsuarios(None, host, user, password, database, port)
        try:
            config_usuarios.salvar_nova_senha(usuario, nova_senha, confirmar_senha)
            QMessageBox.information(self, 'Sucesso', 'Senha alterada com sucesso.')
            self.janela_alterar_senha.close()
            self.registrar_login(usuario)
            self.abrir_janela_principal()
        except ValueError as e:
            self.mostrar_erro(str(e))
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao alterar senha: {e}")

    def registrar_login(self, usuario_id):
        config_usuarios = ConfigUsuarios(None, host, user, password, database, port)
        try:
            config_usuarios.registrar_login(usuario_id)
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao registrar login: {e}")

    def abrir_janela_principal(self):
        usuario_logado = self.obter_usuario_logado()
        if usuario_logado:
            self.janela_principal = JanelaPrincipal(usuario_logado, self.modo)
            self.janela_principal.show()
            self.hide()
        else:
            self.mostrar_erro('Erro ao obter informações do usuário logado.')

    def obter_usuario_logado(self):
        config_usuarios = ConfigUsuarios(None, host, user, password, database, port)
        usuario_logado = config_usuarios.obter_usuario_logado(self.input_usuario.text())
        if usuario_logado:
            return usuario_logado
        else:
            self.mostrar_erro("Erro ao obter informações do usuário logado.")
            return None

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
        self.raise_()

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
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))
#Fim da classe JanelaLogin

#Inicio da classe JanelaPrincipal
class JanelaPrincipal(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.carregar_preferencias_usuario()
        self.inicializarUI()

    def carregar_preferencias_usuario(self):
        try:
            carregar_preferencias = CarregarPreferenciasUsuario()
            preferencias = carregar_preferencias.carregar_preferencias_usuario(self.usuario_logado['id'])
            if preferencias:
                self.modo.modo_atual = 'escuro' if preferencias['modo_tela'] == 'escuro' else 'claro'
                self.icone_modo_escuro_url = preferencias['icone_modo_escuro']
                self.icone_modo_claro_url = preferencias['icone_modo_claro']
                
                if preferencias['fonte_alterada']:
                    self.fonte_padrao = preferencias['fonte_perso']
                else:
                    carregar_config = CarregarConfiguracoes()
                    carregar_config.carregar_configuracoes()
                    self.fonte_padrao = carregar_config.fonte_padrao

                if preferencias['tamanho_fonte_alterado']:
                    self.tamanho_fonte_padrao = preferencias['tamanho_fonte_perso']
                else:
                    carregar_config = CarregarConfiguracoes()
                    carregar_config.carregar_configuracoes()
                    self.tamanho_fonte_padrao = carregar_config.tamanho_fonte_padrao
            else:
                self.mostrar_erro("Erro ao carregar preferências do usuário.")
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao carregar preferências do usuário: {e}")
                    
    def inicializarUI(self):
        self.setWindowTitle('Janela Principal')
        self.setGeometry(0, 0, 300, 200)
        self.center()

        layout = QVBoxLayout()

        # Informações do usuário logado
        self.label_usuario_logado = QLabel(f"Usuário: {self.usuario_logado['usuario']} ({'Admin' if self.usuario_logado['is_admin'] else 'Técnico'})", self)
        self.label_usuario_logado.setAlignment(Qt.AlignLeft)

        # Switch de modo claro/escuro
        self.switch_modo = QPushButton(self)
        self.switch_modo.setMaximumWidth(150)
        self.switch_modo.setCheckable(True)
        self.switch_modo.setChecked(self.modo.modo_atual == 'escuro')
        self.switch_modo.clicked.connect(self.trocar_modo)
        self.atualizar_switch()

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.label_usuario_logado, alignment=Qt.AlignLeft)
        top_layout.addWidget(self.switch_modo, alignment=Qt.AlignRight)
        layout.addLayout(top_layout)

        self.botao_dashboard = QPushButton('DASHBOARD', self)
        self.botao_dashboard.clicked.connect(self.abrir_dashboard)
        layout.addWidget(self.botao_dashboard)

        self.botao_scanner_rede = QPushButton('Scanner de rede', self)
        self.botao_scanner_rede.clicked.connect(self.executar_scanner_rede)
        layout.addWidget(self.botao_scanner_rede)

        self.botao_config_usuarios = QPushButton('Configurações de usuários', self)
        self.botao_config_usuarios.clicked.connect(self.abrir_janela_config_usuarios)
        layout.addWidget(self.botao_config_usuarios)

        self.botao_config_programa = QPushButton('Configurações do programa', self)
        self.botao_config_programa.clicked.connect(self.abrir_janela_config_programa)
        layout.addWidget(self.botao_config_programa)

        self.botao_sair = QPushButton('SAIR', self)
        self.botao_sair.clicked.connect(self.confirmar_saida)
        layout.addWidget(self.botao_sair)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        self.confirmar_saida(event)

    def confirmar_saida(self, event=None):
        reply = QMessageBox(self)
        reply.setWindowTitle('Confirmação')
        reply.setText('Tem certeza que deseja sair?')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button_yes = reply.button(QMessageBox.Yes)
        button_yes.setText('Sim')
        button_no = reply.button(QMessageBox.No)
        button_no.setText('Não')
        reply.exec_()

        if reply.clickedButton() == button_yes:
            QApplication.instance().quit()
        else:
            if event:
                event.ignore()

    def executar_scanner_rede(self):
        self.janela_scanner_rede = JanelaScannerRede(self.usuario_logado, self.modo)
        self.janela_scanner_rede.show()
        self.hide()

    def abrir_janela_config_usuarios(self):
        self.janela_config_usuarios = JanelaConfigUsuarios(self.usuario_logado, self.modo)
        self.janela_config_usuarios.show()
        self.hide()

    def abrir_janela_config_programa(self):
        self.janela_config_programa = JanelaConfigPrograma(self.usuario_logado, self.modo)
        self.janela_config_programa.show()
        self.hide()

    def abrir_dashboard(self):
        self.janela_dashboard = JanelaDashboard(self.usuario_logado, self.modo)
        self.janela_dashboard.show()
        self.hide()

    def trocar_modo(self):
        self.modo.trocar_modo()
        self.atualizar_switch()
        self.salvar_preferencia_modo()

    def salvar_preferencia_modo(self):
        try:
            salvar_config = SalvarConfiguracoes()
            salvar_config.salvar_preferencia_modo(self.modo.modo_atual, self.usuario_logado)
        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar preferência de modo: {e}")

    def atualizar_switch(self):
        # Carregar ícone do URL
        try:
            if self.modo.modo_atual == 'escuro':
                icon_url = self.icone_modo_escuro_url
            else:
                icon_url = self.icone_modo_claro_url

            response = requests.get(icon_url)
            response.raise_for_status()
            image_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            icon = QIcon(pixmap)
            self.switch_modo.setIcon(icon)
        except Exception as e:
            self.mostrar_erro(f"Erro ao carregar ícone do modo: {e}")

        estilo = self.modo.atualizar_switch()
        self.switch_modo.setStyleSheet(f"""
        QPushButton {{
            background-color: {estilo["botao"]["background-color"]};
            color: {estilo["botao"]["color"]};
            border: {estilo["botao"]["border"]};
            border-radius: {estilo["botao"]["border-radius"]};
            padding: {estilo["botao"]["padding"]};
            text-align: {estilo["botao"]["text-align"]};
            padding-right: {estilo["botao"].get("padding-right", "0px")};
            padding-left: {estilo["botao"].get("padding-left", "0px")};
        }}
        QPushButton:checked {{
            background-color: {estilo["botao_checked"]["background-color"]};
            color: {estilo["botao_checked"]["color"]};
            text-align: {estilo["botao_checked"]["text-align"]};
            padding-right: {estilo["botao_checked"].get("padding-right", "0px")};
            padding-left: {estilo["botao_checked"].get("padding-left", "0px")};
        }}
        """)
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

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaPrincipal

#Inicio da classe JanelaScannerRede
class JanelaScannerRede(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.carregar_preferencias_usuario()
        self.inicializarUI()
        self.aplicar_modo()

    def carregar_preferencias_usuario(self):
        carregar_preferencias = CarregarPreferenciasUsuario()
        preferencias = carregar_preferencias.carregar_preferencias_usuario(self.usuario_logado['id'])
        if preferencias:
            self.fonte_padrao = preferencias['fonte_perso'] if preferencias['fonte_alterada'] else ModosPrincipais().fonte_padrao
            self.tamanho_fonte_padrao = preferencias['tamanho_fonte_perso'] if preferencias['tamanho_fonte_alterado'] else ModosPrincipais().tamanho_fonte_padrao
        else:
            modos = ModosPrincipais()
            modos.carregar_preferencias_usuario()
            self.fonte_padrao = modos.fonte_padrao
            self.tamanho_fonte_padrao = modos.tamanho_fonte_padrao

    def inicializarUI(self):
        self.setWindowTitle('Scanner de Rede')
        self.setGeometry(100, 100, 400, 300)
        self.center()

        layout = QVBoxLayout()

        self.botao_ping = QPushButton('PING', self)
        self.botao_ping.clicked.connect(self.abrir_janela_ping)
        layout.addWidget(self.botao_ping)

        self.botao_escanear_rede = QPushButton('Escanear a própria rede', self)
        self.botao_escanear_rede.clicked.connect(self.abrir_janela_opcoes_scanner)
        layout.addWidget(self.botao_escanear_rede)

        self.botao_ver_dados = QPushButton('Ver dados armazenados', self)
        self.botao_ver_dados.clicked.connect(self.abrir_janela_ver_informacoes)
        layout.addWidget(self.botao_ver_dados)

        self.botao_voltar = QPushButton('Voltar ao menu principal', self)
        self.botao_voltar.clicked.connect(self.voltar_menu_principal)
        layout.addWidget(self.botao_voltar)

        self.setLayout(layout)

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
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def abrir_janela_ping(self):
        self.janela_ping = JanelaPing(self.usuario_logado, self.modo)
        self.janela_ping.show()

    def abrir_janela_opcoes_scanner(self):
        self.janela_opcoes_scanner = JanelaOpcoesScanner(self.usuario_logado, self.modo)
        self.janela_opcoes_scanner.show()

    def abrir_janela_ver_informacoes(self):
        self.janela_ver_informacoes = JanelaVerInformacoes(self.usuario_logado, self.modo)
        self.janela_ver_informacoes.show()

    def voltar_menu_principal(self):
        self.janela_principal = JanelaPrincipal(self.usuario_logado, self.modo)
        self.janela_principal.show()
        self.close()

    def closeEvent(self, event):
        self.voltar_menu_principal()
        event.accept()

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaScannerRede    

#Inicio da classe JanelaPing
class JanelaPing(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.carregar_preferencias_usuario()
        self.inicializarUI()
        self.aplicar_modo()

    def carregar_preferencias_usuario(self):
        carregar_preferencias = CarregarPreferenciasUsuario()
        preferencias = carregar_preferencias.carregar_preferencias_usuario(self.usuario_logado['id'])
        if preferencias:
            self.fonte_padrao = preferencias['fonte_perso'] if preferencias['fonte_alterada'] else ModosPrincipais().fonte_padrao
            self.tamanho_fonte_padrao = preferencias['tamanho_fonte_perso'] if preferencias['tamanho_fonte_alterado'] else ModosPrincipais().tamanho_fonte_padrao
        else:
            modos = ModosPrincipais()
            modos.carregar_preferencias_usuario()
            self.fonte_padrao = modos.fonte_padrao
            self.tamanho_fonte_padrao = modos.tamanho_fonte_padrao

    def inicializarUI(self):
        self.setWindowTitle('Ping')
        self.setGeometry(100, 100, 400, 300)
        self.center()

        layout = QVBoxLayout()

        self.label_rede_atual = QLabel('Rede Atual: Obtendo...', self)
        layout.addWidget(self.label_rede_atual)

        self.input_ip = QLineEdit(self)
        self.input_ip.setPlaceholderText('Digite o IP para fazer o PING')
        layout.addWidget(self.input_ip)

        self.botao_ping = QPushButton('PING', self)
        self.botao_ping.clicked.connect(self.fazer_ping)
        layout.addWidget(self.botao_ping)

        self.label_resultado = QLabel('', self)
        layout.addWidget(self.label_resultado)

        self.botao_voltar = QPushButton('Voltar', self)
        self.botao_voltar.clicked.connect(self.close)
        layout.addWidget(self.botao_voltar)
        
        self.setLayout(layout)
        self.atualizar_rede_atual()

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
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def atualizar_rede_atual(self):
        try:
            rede_atual = RedeAtual()
            rede = rede_atual.obter_rede_atual()

            if rede:
                self.label_rede_atual.setText(f"Rede Atual: {rede}")
            else:
                self.label_rede_atual.setText("Erro ao obter rede")
        except Exception as e:
            self.mostrar_erro(f"Erro ao atualizar rede atual: {e}")

    def fazer_ping(self):
        ip = self.input_ip.text()
        if not ip:
            self.mostrar_erro("Por favor, insira um IP.")
            return

        try:
            # Validando o endereço IP
            ipaddress.ip_address(ip)
        except ValueError:
            self.label_resultado.setText(f"Endereço IP inválido: {ip}")
            return

        self.label_resultado.setText("Executando PING...")

        def ping_thread():
            try:
                ping = PingIP(ip)
                resultado = ping.ping()
                if resultado == 1:
                    self.label_resultado.setText(f"PING para {ip} foi bem-sucedido.")
                elif resultado == 0:
                    self.label_resultado.setText(f"PING para {ip} falhou.")
            except Exception as e:
                self.label_resultado.setText(f"Erro ao executar o PING: {e}")

        class PingRunnable(QRunnable):
            def run(self):
                ping_thread()

        QThreadPool.globalInstance().start(PingRunnable())

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaPing
   
# Inicio da classe JanelaOpcoesScanner
class JanelaOpcoesScanner(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.carregar_preferencias_usuario()
        self.inicializarUI()
        self.aplicar_modo()

    def carregar_preferencias_usuario(self):
        modos = ModosPrincipais()
        modos.carregar_preferencias_usuario()
        self.fonte_padrao = modos.fonte_padrao
        self.tamanho_fonte_padrao = modos.tamanho_fonte_padrao

    def inicializarUI(self):
        self.setWindowTitle('Opções de Scanner de Rede')
        self.setGeometry(100, 100, 400, 300)
        self.center()

        layout = QVBoxLayout()

        self.checkbox_escaneamento_rapido = QCheckBox('Escaneamento Rápido', self)
        self.checkbox_escaneamento_rapido.setChecked(True)
        self.checkbox_escaneamento_rapido.stateChanged.connect(self.atualizar_checkboxes)
        layout.addWidget(self.checkbox_escaneamento_rapido)

        self.checkbox_escaneamento_completo = QCheckBox('Escaneamento Completo', self)
        self.checkbox_escaneamento_completo.stateChanged.connect(self.atualizar_checkboxes)
        layout.addWidget(self.checkbox_escaneamento_completo)

        self.checkbox_porta_22 = QCheckBox('Porta 22', self)
        layout.addWidget(self.checkbox_porta_22)

        self.checkbox_porta_80 = QCheckBox('Porta 80', self)
        layout.addWidget(self.checkbox_porta_80)

        self.checkbox_porta_443 = QCheckBox('Porta 443', self)
        layout.addWidget(self.checkbox_porta_443)

        self.botao_iniciar_scanner = QPushButton('Iniciar Scanner', self)
        self.botao_iniciar_scanner.clicked.connect(self.iniciar_scanner)
        layout.addWidget(self.botao_iniciar_scanner)

        self.setLayout(layout)

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
        QCheckBox {{
            color: {estilo["label"]["color"]};
        }}
        """)
        if self.fonte_padrao and self.tamanho_fonte_padrao:
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def atualizar_checkboxes(self):
        if self.checkbox_escaneamento_rapido.isChecked():
            self.checkbox_escaneamento_completo.setChecked(False)
        elif self.checkbox_escaneamento_completo.isChecked():
            self.checkbox_escaneamento_rapido.setChecked(False)

    def iniciar_scanner(self):
        escaneamento_rapido = self.checkbox_escaneamento_rapido.isChecked()
        portas_selecionadas = []
        if self.checkbox_porta_22.isChecked():
            portas_selecionadas.append('22')
        if self.checkbox_porta_80.isChecked():
            portas_selecionadas.append('80')
        if self.checkbox_porta_443.isChecked():
            portas_selecionadas.append('443')

        scanner = ScannerRedeExterno(host, user, password, database, port)
        scanner.escaneamento_rapido = escaneamento_rapido
        scanner.portas_selecionadas = portas_selecionadas
        resultados = scanner.escanear()

        try:
            scanner = ScannerRedeExterno(host, user, password, database, port)
            scanner.salvar_resultados(resultados)
            
            data_atual = datetime.now().strftime('%d/%m/%Y')
            carregar_resultados_calendario = CarregarResultadosCalendario(host, user, password, database, port, data_atual)
            resultados_salvos = carregar_resultados_calendario.carregar_resultados()
            
            if isinstance(resultados_salvos, str):
                self.mostrar_erro(resultados_salvos)
                return
            
            self.janela_resultados = JanelaResultadosScanner(self.usuario_logado, self.modo, resultados_salvos)
            self.janela_resultados.show()
            self.close()
        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar resultados do scanner: {e}")

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaOpcoesScanner

#Inicio da classe JanelaResultadosScanner
class JanelaResultadosScanner(QWidget):
    def __init__(self, usuario_logado, modo, resultados):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.resultados = resultados
        self.carregar_preferencias_usuario()
        self.inicializarUI()
        self.aplicar_modo()

    def carregar_preferencias_usuario(self):
        modos = ModosPrincipais()
        modos.carregar_preferencias_usuario()
        self.fonte_padrao = modos.fonte_padrao
        self.tamanho_fonte_padrao = modos.tamanho_fonte_padrao

    def inicializarUI(self):
        self.setWindowTitle('Resultados do Scanner de Rede')
        self.setGeometry(100, 100, 800, 600)
        self.center()

        layout = QVBoxLayout()

        self.tabela_resultados = QTableWidget(self)
        self.tabela_resultados.setColumnCount(6)
        self.tabela_resultados.setHorizontalHeaderLabels(['Usuário ID', 'Data', 'Hostname', 'MAC Address', 'IP', 'Portas'])
        self.tabela_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.tabela_resultados)

        self.carregar_resultados()

        botao_fechar = QPushButton('Fechar', self)
        botao_fechar.clicked.connect(self.close)
        layout.addWidget(botao_fechar)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def carregar_resultados(self):
        try:
            self.tabela_resultados.setRowCount(0)
            for resultado in self.resultados:
                row_position = self.tabela_resultados.rowCount()
                self.tabela_resultados.insertRow(row_position)
                valores = [
                    resultado.get('usuario_id', ''),
                    resultado.get('data', ''),
                    resultado.get('hostname', ''),
                    resultado.get('mac_address', ''),
                    resultado.get('ip', ''),
                    resultado.get('portas', '')
                ]
                for column, data in enumerate(valores):
                    self.tabela_resultados.setItem(row_position, column, QTableWidgetItem(str(data)))
            self.tabela_resultados.resizeColumnsToContents()
        except Exception as e:
            self.mostrar_erro(f"Erro ao carregar resultados: {e}")
            try:
                data_atual = datetime.now().strftime('%d/%m/%Y')
                carregar_resultados_calendario = CarregarResultadosCalendario(host, user, password, database, port, data_atual)
                resultados_salvos = carregar_resultados_calendario.carregar_resultados()

                if isinstance(resultados_salvos, str):
                    self.mostrar_erro(resultados_salvos)
                    return

                self.tabela_resultados.setRowCount(0)
                for resultado in resultados_salvos:
                    row_position = self.tabela_resultados.rowCount()
                    self.tabela_resultados.insertRow(row_position)
                    valores = [
                        resultado.get('usuario_id', ''),
                        resultado.get('data', ''),
                        resultado.get('hostname', ''),
                        resultado.get('mac_address', ''),
                        resultado.get('ip', ''),
                        resultado.get('portas', '')
                    ]
                    for column, data in enumerate(valores):
                        self.tabela_resultados.setItem(row_position, column, QTableWidgetItem(str(data)))
                self.tabela_resultados.resizeColumnsToContents()
            except Exception as e:
                self.mostrar_erro(f"Erro ao carregar resultados: {e}")
            
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
        QTableWidget {{
            background-color: {estilo["widget"]["background-color"]};
            color: {estilo["widget"]["color"]};
        }}
        QHeaderView::section {{
            background-color: {estilo["botao"]["background-color"]};
            color: {estilo["botao"]["color"]};
        }}
        """)
        if self.fonte_padrao and self.tamanho_fonte_padrao:
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaResultadosScanner

#Inicio da classe JanelaVerInformacoes
class JanelaVerInformacoes(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.carregar_preferencias_usuario()
        self.inicializarUI()
        self.aplicar_modo()

    def carregar_preferencias_usuario(self):
        modos = ModosPrincipais()
        modos.carregar_preferencias_usuario()
        self.fonte_padrao = modos.fonte_padrao
        self.tamanho_fonte_padrao = modos.tamanho_fonte_padrao

    def inicializarUI(self):
        self.setWindowTitle('Informações Armazenadas')
        self.setGeometry(100, 100, 600, 400)
        self.center()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Selecione a data no calendário:', self)
        layout.addWidget(self.label_instrucoes)

        self.calendario = QCalendarWidget(self)
        self.calendario.setSelectedDate(datetime.now())
        self.calendario.clicked.connect(self.atualizar_data_selecionada)
        layout.addWidget(self.calendario)

        self.input_data = QLineEdit(self)
        self.input_data.setText(self.calendario.selectedDate().toString('dd/MM/yyyy'))
        self.input_data.setReadOnly(True)
        layout.addWidget(self.input_data)

        self.botao_ver_informacoes = QPushButton('Ver Informações Armazenadas', self)
        self.botao_ver_informacoes.clicked.connect(self.ver_informacoes_armazenadas)
        layout.addWidget(self.botao_ver_informacoes)

        self.setLayout(layout)

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
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def atualizar_data_selecionada(self):
        data_selecionada = self.calendario.selectedDate().toString('dd/MM/yyyy')
        self.input_data.setText(data_selecionada)

    def ver_informacoes_armazenadas(self):
        data_selecionada = self.input_data.text()
        self.janela_resultados_data = JanelaResultadosData(self.usuario_logado, self.modo, data_selecionada)
        self.janela_resultados_data.show()

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaVerInformacoes

#Inicio da classe JanelaResultadosData
class JanelaResultadosData(QWidget):
    def __init__(self, usuario_logado, modo, data_selecionada):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.data_selecionada = data_selecionada
        self.carregar_preferencias_usuario()
        self.inicializarUI()
        self.aplicar_modo()

    def carregar_preferencias_usuario(self):
        modos = ModosPrincipais()
        modos.carregar_preferencias_usuario()
        self.fonte_padrao = modos.fonte_padrao
        self.tamanho_fonte_padrao = modos.tamanho_fonte_padrao

    def inicializarUI(self):
        self.setWindowTitle(f'Resultados para {self.data_selecionada}')
        self.setGeometry(100, 100, 800, 600)
        self.center()

        layout = QVBoxLayout()

        self.tabela_resultados = QTableWidget(self)
        self.tabela_resultados.setColumnCount(5)
        self.tabela_resultados.setHorizontalHeaderLabels(['Usuário ID', 'Data', 'Hostname', 'MAC Address', 'IP', 'Portas'])
        self.tabela_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabela_resultados.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        layout.addWidget(self.tabela_resultados)

        self.carregar_resultados()

        botao_fechar = QPushButton('Fechar', self)
        botao_fechar.clicked.connect(self.close)
        layout.addWidget(botao_fechar, alignment=Qt.AlignCenter)

        self.setLayout(layout)

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
            border: {estilo["botao"]["border"]};
            border-radius: {estilo["botao"]["border-radius"]};
            padding: {estilo["botao"]["padding"]};
            text-align: {estilo["botao"]["text-align"]};
            padding-right: {estilo["botao"].get("padding-right", "0px")};
            padding-left: {estilo["botao"].get("padding-left", "0px")};
        }}
        QPushButton:checked {{
            background-color: {estilo["botao_checked"]["background-color"]};
            color: {estilo["botao_checked"]["color"]};
            text-align: {estilo["botao_checked"]["text-align"]};
            padding-right: {estilo["botao_checked"].get("padding-right", "0px")};
            padding-left: {estilo["botao_checked"].get("padding-left", "0px")};
        }}
        QTableWidget {{
            background-color: {estilo["widget"]["background-color"]};
            color: {estilo["widget"]["color"]};
        }}
        QHeaderView::section {{
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
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def carregar_resultados(self):
        try:
            carregar_resultados_calendario = CarregarResultadosCalendario(host, user, password, database, port, self.data_selecionada)
            resultados = carregar_resultados_calendario.carregar_resultados()

            if isinstance(resultados, str):
                self.mostrar_erro(resultados)
                return

            self.tabela_resultados.setRowCount(0)
            for resultado in resultados:
                row_position = self.tabela_resultados.rowCount()
                self.tabela_resultados.insertRow(row_position)
                for column, data in enumerate(resultado.values()):
                    self.tabela_resultados.setItem(row_position, column, QTableWidgetItem(str(data)))
            self.tabela_resultados.resizeColumnsToContents()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao buscar informações: {e}")

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaResultadosData

#Inicio da classe JanelaConfigUsuarios
class JanelaConfigUsuarios(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.config_usuarios = ConfigUsuarios(usuario_logado, host, user, password, database, port)
        self.carregar_preferencias_usuario()
        self.inicializarUI()
        self.aplicar_modo()

    def carregar_preferencias_usuario(self):
        carregar_preferencias = CarregarPreferenciasUsuario()
        preferencias = carregar_preferencias.carregar_preferencias_usuario(self.usuario_logado['id'])
        if preferencias:
            self.fonte_padrao = preferencias['fonte_perso'] if preferencias['fonte_alterada'] else ModosPrincipais().fonte_padrao
            self.tamanho_fonte_padrao = preferencias['tamanho_fonte_perso'] if preferencias['tamanho_fonte_alterado'] else ModosPrincipais().tamanho_fonte_padrao
        else:
            modos = ModosPrincipais()
            modos.carregar_preferencias_usuario()
            self.fonte_padrao = modos.fonte_padrao
            self.tamanho_fonte_padrao = modos.tamanho_fonte_padrao

    def inicializarUI(self):
        self.setWindowTitle('Configurações de Usuários')
        self.setGeometry(100, 100, 600, 400)
        self.center()
        self.aplicar_modo()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Gerencie os usuários do sistema:', self)
        self.label_instrucoes.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_instrucoes)

        self.botao_adicionar_usuario = QPushButton('Adicionar Usuário', self)
        self.botao_adicionar_usuario.clicked.connect(self.adicionar_usuario)
        layout.addWidget(self.botao_adicionar_usuario)

        self.botao_alterar_senha = QPushButton('Alterar Senhas', self)
        self.botao_alterar_senha.clicked.connect(self.alterar_senha)
        layout.addWidget(self.botao_alterar_senha)

        self.botao_remover_usuario = QPushButton('Remover Usuário', self)
        self.botao_remover_usuario.clicked.connect(self.remover_usuario)
        layout.addWidget(self.botao_remover_usuario)

        self.botao_ver_informacoes_usuarios = QPushButton('Ver Informações e Editar', self)
        self.botao_ver_informacoes_usuarios.clicked.connect(self.ver_informacoes_usuarios)
        layout.addWidget(self.botao_ver_informacoes_usuarios)

        self.botao_voltar = QPushButton('Voltar ao Menu Principal', self)
        self.botao_voltar.clicked.connect(self.voltar_menu_principal)
        layout.addWidget(self.botao_voltar)

        self.setLayout(layout)

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
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        self.voltar_menu_principal()
        super().closeEvent(event)

    def voltar_menu_principal(self):
        self.janela_principal = JanelaPrincipal(self.usuario_logado, self.modo)
        self.janela_principal.show()
        self.close()

    def adicionar_usuario(self):
        if not self.usuario_logado['is_admin']:
            self.mostrar_erro("Somente administradores podem adicionar usuários.")
            return

        self.janela_adicionar = QWidget()
        self.janela_adicionar.setWindowTitle('Adicionar Usuário')
        self.janela_adicionar.setGeometry(100, 100, 400, 300)
        self.janela_adicionar.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout()

        self.input_usuario = QLineEdit(self.janela_adicionar)
        layout.addWidget(QLabel('Usuário:'))
        layout.addWidget(self.input_usuario)

        self.input_nome_completo = QLineEdit(self.janela_adicionar)
        layout.addWidget(QLabel('Nome Completo:'))
        layout.addWidget(self.input_nome_completo)

        self.input_email = QLineEdit(self.janela_adicionar)
        layout.addWidget(QLabel('Email:'))
        layout.addWidget(self.input_email)

        self.input_senha = QLineEdit(self.janela_adicionar)
        self.input_senha.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Senha:'))
        layout.addWidget(self.input_senha)

        self.checkbox_is_admin = QCheckBox('Administrador', self.janela_adicionar)
        layout.addWidget(self.checkbox_is_admin, alignment=Qt.AlignCenter)

        self.checkbox_adicionar_varios = QCheckBox('Adicionar vários', self.janela_adicionar)
        layout.addWidget(self.checkbox_adicionar_varios, alignment=Qt.AlignCenter)

        botao_salvar = QPushButton('Salvar', self.janela_adicionar)
        botao_salvar.clicked.connect(self.salvar_novo_usuario)
        layout.addWidget(botao_salvar, alignment=Qt.AlignCenter)

        botao_cancelar = QPushButton('Cancelar', self.janela_adicionar)
        botao_cancelar.clicked.connect(self.janela_adicionar.close)
        layout.addWidget(botao_cancelar, alignment=Qt.AlignCenter)

        self.janela_adicionar.setLayout(layout)
        self.janela_adicionar.show()

    def salvar_novo_usuario(self):
        usuario = self.input_usuario.text()
        nome_completo = self.input_nome_completo.text()
        email = self.input_email.text()
        senha = self.input_senha.text()
        is_admin = 1 if self.checkbox_is_admin.isChecked() else 0

        if not usuario or not nome_completo or not email or not senha:
            self.mostrar_erro("Todos os campos são obrigatórios.")
            return

        try:
            self.config_usuarios.adicionar_usuario(usuario, nome_completo, email, senha, is_admin)
            QMessageBox.information(self, 'Sucesso', 'Usuário adicionado com sucesso.')
            if self.checkbox_adicionar_varios.isChecked():
                self.input_usuario.clear()
                self.input_nome_completo.clear()
                self.input_email.clear()
                self.input_senha.clear()
                self.checkbox_is_admin.setChecked(False)
                self.input_usuario.setFocus()
            else:
                self.janela_adicionar.close()
        except PermissionError as e:
            self.mostrar_erro(str(e))
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao adicionar usuário: {e}")
        except Exception as e:
            self.mostrar_erro(f"Erro inesperado: {e}")

    def remover_usuario(self):
        if not self.usuario_logado['is_admin']:
            self.mostrar_erro("Somente administradores podem remover usuários.")
            return

        self.janela_remover = QWidget()
        self.janela_remover.setWindowTitle('Remover Usuário')
        self.janela_remover.setGeometry(100, 100, 600, 400)
        self.janela_remover.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Selecione o usuário a remover:', self.janela_remover)
        self.label_instrucoes.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_instrucoes)

        self.lista_usuarios_remover = QListWidget(self.janela_remover)
        layout.addWidget(self.lista_usuarios_remover)

        try:
            usuarios = self.config_usuarios.listar_usuarios()
            for usuario in usuarios:
                id_usuario, nome_usuario, nome_completo, email, is_admin = usuario
                item = QListWidgetItem(f"ID: {id_usuario} | Usuário: {nome_usuario} | Nome: {nome_completo} | Email: {email} | Admin: {'Sim' if is_admin else 'Não'}")
                item.setData(Qt.UserRole, usuario)
                self.lista_usuarios_remover.addItem(item)
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar usuários: {e}")
            return

        botao_remover = QPushButton('Remover', self.janela_remover)
        botao_remover.clicked.connect(self.confirmar_remocao_usuario)
        layout.addWidget(botao_remover, alignment=Qt.AlignCenter)

        botao_cancelar = QPushButton('Cancelar', self.janela_remover)
        botao_cancelar.clicked.connect(self.janela_remover.close)
        layout.addWidget(botao_cancelar, alignment=Qt.AlignCenter)

        self.janela_remover.setLayout(layout)
        self.janela_remover.show()

    def confirmar_remocao_usuario(self):
        item_selecionado = self.lista_usuarios_remover.currentItem()
        if not item_selecionado:
            self.mostrar_erro("Por favor, selecione um usuário para remover.")
            return

        usuario = item_selecionado.data(Qt.UserRole)
        usuario_id = usuario[0]

        reply = QMessageBox.question(
            self,
            'Confirmar Remoção',
            f'Tem certeza que deseja remover o usuário "{usuario[1]}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.config_usuarios.remover_usuario(usuario_id)
                QMessageBox.information(self, 'Sucesso', 'Usuário removido com sucesso.')
                self.janela_remover.close()
            except Exception as e:
                self.mostrar_erro(f"Erro ao remover usuário: {e}")
        else:
            # Usuário clicou 'Não', não faz nada
            pass

    def ver_informacoes_usuarios(self):
        try:
            usuarios = self.config_usuarios.listar_usuarios()

            self.janela_ver_usuarios = QWidget()
            self.janela_ver_usuarios.setWindowTitle('Informações dos Usuários')
            width = 800
            height = 100 + (len(usuarios) * 30) if usuarios else 200
            self.janela_ver_usuarios.setGeometry(100, 100, width, height)
            self.janela_ver_usuarios.setStyleSheet(self.styleSheet())
            layout = QVBoxLayout()

            if not usuarios:
                label_usuario = QLabel("Nenhum usuário encontrado.")
                label_usuario.setAlignment(Qt.AlignCenter)
                layout.addWidget(label_usuario)
            else:
                self.lista_usuarios = QListWidget(self.janela_ver_usuarios)
                for usuario in usuarios:
                    id_usuario, nome_usuario, nome_completo, email, is_admin = usuario
                    item = QListWidgetItem(f"ID: {id_usuario} | Usuário: {nome_usuario} | Nome: {nome_completo} | Email: {email} | Admin: {'Sim' if is_admin else 'Não'}")
                    item.setData(Qt.UserRole, usuario)
                    self.lista_usuarios.addItem(item)
                layout.addWidget(self.lista_usuarios)

                if self.usuario_logado['is_admin']:
                    botao_editar = QPushButton('Editar', self.janela_ver_usuarios)
                    botao_editar.clicked.connect(self.editar_usuario_selecionado)
                    layout.addWidget(botao_editar, alignment=Qt.AlignCenter)

            botao_fechar = QPushButton('Fechar', self.janela_ver_usuarios)
            botao_fechar.clicked.connect(self.janela_ver_usuarios.close)
            layout.addWidget(botao_fechar, alignment=Qt.AlignCenter)

            self.janela_ver_usuarios.setLayout(layout)
            self.janela_ver_usuarios.show()
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar usuários: {e}")

    def editar_usuario_selecionado(self):
        item_selecionado = self.lista_usuarios.currentItem()
        if item_selecionado:
            usuario = item_selecionado.data(Qt.UserRole)
            self.abrir_janela_edicao(usuario)
        else:
            self.mostrar_erro("Nenhum usuário selecionado.")

    def abrir_janela_edicao(self, usuario):
        self.janela_edicao = QWidget()
        self.janela_edicao.setWindowTitle('Editar Informações do Usuário')
        self.janela_edicao.setGeometry(100, 100, 400, 300)
        self.janela_edicao.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout()

        id_usuario, nome_usuario, nome_completo, email, is_admin = usuario

        self.input_usuario = QLineEdit(self.janela_edicao)
        self.input_usuario.setText(nome_usuario)
        layout.addWidget(QLabel('Usuário:'))
        layout.addWidget(self.input_usuario)

        self.input_nome_completo = QLineEdit(self.janela_edicao)
        self.input_nome_completo.setText(nome_completo)
        layout.addWidget(QLabel('Nome Completo:'))
        layout.addWidget(self.input_nome_completo)

        self.input_email = QLineEdit(self.janela_edicao)
        self.input_email.setText(email)
        layout.addWidget(QLabel('Email:'))
        layout.addWidget(self.input_email)

        self.checkbox_is_admin = QCheckBox('Administrador', self.janela_edicao)
        self.checkbox_is_admin.setChecked(is_admin)
        layout.addWidget(self.checkbox_is_admin, alignment=Qt.AlignCenter)

        botao_salvar = QPushButton('Salvar', self.janela_edicao)
        botao_salvar.clicked.connect(lambda: self.salvar_edicao_usuario(id_usuario))
        layout.addWidget(botao_salvar, alignment=Qt.AlignCenter)

        botao_cancelar = QPushButton('Cancelar', self.janela_edicao)
        botao_cancelar.clicked.connect(self.janela_edicao.close)
        layout.addWidget(botao_cancelar, alignment=Qt.AlignCenter)

        self.janela_edicao.setLayout(layout)
        self.janela_edicao.show()

    def salvar_edicao_usuario(self, usuario_id):
        usuario = self.input_usuario.text()
        nome_completo = self.input_nome_completo.text()
        email = self.input_email.text()
        is_admin = 1 if self.checkbox_is_admin.isChecked() else 0

        try:
            self.config_usuarios.editar_usuario(usuario_id, usuario, nome_completo, email, is_admin)
            QMessageBox.information(self, 'Sucesso', 'Informações do usuário atualizadas com sucesso.')
            self.janela_edicao.close()
            self.janela_ver_usuarios.close()
        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar informações do usuário: {e}")

    def alterar_senha(self):
        if not self.usuario_logado['is_admin']:
            self.alterar_senha_usuario(self.usuario_logado['id'])
        else:
            self.janela_selecionar_usuario = QWidget()
            self.janela_selecionar_usuario.setWindowTitle('Selecionar Usuário para Alterar Senha')
            self.janela_selecionar_usuario.setGeometry(100, 100, 600, 400)
            self.janela_selecionar_usuario.setStyleSheet(self.styleSheet())
            layout = QVBoxLayout()

            self.label_instrucoes = QLabel('Selecione o usuário para alterar a senha:', self.janela_selecionar_usuario)
            self.label_instrucoes.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.label_instrucoes)

            self.lista_usuarios = QListWidget(self.janela_selecionar_usuario)
            layout.addWidget(self.lista_usuarios)

            try:
                usuarios = self.config_usuarios.listar_usuarios()
                for usuario in usuarios:
                    id_usuario, nome_usuario, nome_completo, email, is_admin = usuario
                    item = QListWidgetItem(f"ID: {id_usuario} | Usuário: {nome_usuario} | Nome: {nome_completo} | Email: {email} | Admin: {'Sim' if is_admin else 'Não'}")
                    item.setData(Qt.UserRole, usuario)
                    self.lista_usuarios.addItem(item)
            except Exception as e:
                self.mostrar_erro(f"Erro ao buscar usuários: {e}")
                return

            botao_selecionar = QPushButton('Selecionar', self.janela_selecionar_usuario)
            botao_selecionar.clicked.connect(self.selecionar_usuario_para_alterar_senha)
            layout.addWidget(botao_selecionar, alignment=Qt.AlignCenter)

            botao_cancelar = QPushButton('Cancelar', self.janela_selecionar_usuario)
            botao_cancelar.clicked.connect(self.janela_selecionar_usuario.close)
            layout.addWidget(botao_cancelar, alignment=Qt.AlignCenter)

            self.janela_selecionar_usuario.setLayout(layout)
            self.janela_selecionar_usuario.show()

    def selecionar_usuario_para_alterar_senha(self):
        item_selecionado = self.lista_usuarios.currentItem()
        if not item_selecionado:
            self.mostrar_erro("Por favor, selecione um usuário.")
            return

        usuario = item_selecionado.data(Qt.UserRole)
        self.alterar_senha_usuario(usuario[0])

    def alterar_senha_usuario(self, usuario_id):
        self.janela_alterar_senha = QWidget()
        self.janela_alterar_senha.setWindowTitle('Alterar Senha')
        self.janela_alterar_senha.setGeometry(100, 100, 400, 300)
        self.janela_alterar_senha.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout()

        self.input_nova_senha = QLineEdit(self.janela_alterar_senha)
        self.input_nova_senha.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Nova Senha:'))
        layout.addWidget(self.input_nova_senha)

        self.input_confirmar_senha = QLineEdit(self.janela_alterar_senha)
        self.input_confirmar_senha.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Confirmar Nova Senha:'))
        layout.addWidget(self.input_confirmar_senha)

        botao_salvar = QPushButton('Salvar', self.janela_alterar_senha)
        botao_salvar.clicked.connect(lambda: self.salvar_nova_senha(usuario_id))
        layout.addWidget(botao_salvar, alignment=Qt.AlignCenter)

        botao_cancelar = QPushButton('Cancelar', self.janela_alterar_senha)
        botao_cancelar.clicked.connect(self.janela_alterar_senha.close)
        layout.addWidget(botao_cancelar, alignment=Qt.AlignCenter)

        self.janela_alterar_senha.setLayout(layout)
        self.janela_alterar_senha.show()

    def salvar_nova_senha(self, usuario_id):
        nova_senha = self.input_nova_senha.text()
        confirmar_senha = self.input_confirmar_senha.text()

        if not nova_senha or not confirmar_senha:
            self.mostrar_erro("Todos os campos são obrigatórios.")
            return

        if nova_senha != confirmar_senha:
            self.mostrar_erro("As senhas não coincidem.")
            return

        try:
            self.config_usuarios.alterar_senha(usuario_id, nova_senha)
            QMessageBox.information(self, 'Sucesso', 'Senha alterada com sucesso.')
            self.janela_alterar_senha.close()
            if hasattr(self, 'janela_selecionar_usuario'):
                self.janela_selecionar_usuario.close()
        except Exception as e:
            self.mostrar_erro(f"Erro ao alterar senha: {e}")

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
#Fim da classe JanelaConfigUsuarios

#Inicio da classe JanelaConfigPrograma
class JanelaConfigPrograma(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.carregar_preferencias_usuario()
        self.inicializarUI()
        self.aplicar_modo()

    def carregar_preferencias_usuario(self):
        modos = ModosPrincipais()
        modos.carregar_preferencias_usuario()
        self.fonte_padrao = modos.fonte_padrao
        self.tamanho_fonte_padrao = modos.tamanho_fonte_padrao

    def inicializarUI(self):
        self.setWindowTitle('Configurações do Programa')
        self.setGeometry(100, 100, 600, 400)
        self.center()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Configure as opções do programa:', self)
        layout.addWidget(self.label_instrucoes, alignment=Qt.AlignTop)

        if self.usuario_logado['is_admin']:
            self.input_logo_principal = QLineEdit(self)
            layout.addWidget(QLabel('Logo Principal:'))
            layout.addWidget(self.input_logo_principal)

            self.input_logo_principal.setReadOnly(True)
            self.input_logo_principal.setStyleSheet("background-color: lightgray;")
            self.botao_logo_principal = QPushButton('Selecionar Logo Principal', self)
            self.botao_logo_principal.clicked.connect(self.selecionar_logo_principal)
            layout.addWidget(self.botao_logo_principal)

            self.input_logo_rodape = QLineEdit(self)
            layout.addWidget(QLabel('Logo Rodapé:'))
            layout.addWidget(self.input_logo_rodape)

            self.input_logo_rodape.setReadOnly(True)
            self.input_logo_rodape.setStyleSheet("background-color: lightgray;")
            self.botao_logo_rodape = QPushButton('Selecionar Logo Rodapé', self)
            self.botao_logo_rodape.clicked.connect(self.selecionar_logo_rodape)
            layout.addWidget(self.botao_logo_rodape)

            self.combo_fonte_padrao = QComboBox(self)
            self.combo_fonte_padrao.setEditable(True)
            self.combo_fonte_padrao.lineEdit().setReadOnly(True)
            self.combo_fonte_padrao.lineEdit().setAlignment(Qt.AlignCenter)
            layout.addWidget(QLabel('Fonte Global:'))
            layout.addWidget(self.combo_fonte_padrao)

            for font in QFontDatabase().families():
                self.combo_fonte_padrao.addItem(font)

            self.combo_tamanho_fonte_padrao = QComboBox(self)
            self.combo_tamanho_fonte_padrao.setEditable(True)
            self.combo_tamanho_fonte_padrao.lineEdit().setReadOnly(True)
            self.combo_tamanho_fonte_padrao.lineEdit().setAlignment(Qt.AlignCenter)
            layout.addWidget(QLabel('Tamanho da Fonte Global:'))
            layout.addWidget(self.combo_tamanho_fonte_padrao)

            for size in range(8, 30):
                self.combo_tamanho_fonte_padrao.addItem(str(size))

            self.combo_modo_padrao = QComboBox(self)
            self.combo_modo_padrao.addItems(['Claro', 'Escuro'])
            layout.addWidget(QLabel('Modo Padrão:'))
            layout.addWidget(self.combo_modo_padrao)

        self.combo_fonte_usuario = QComboBox(self)
        self.combo_fonte_usuario.setEditable(True)
        self.combo_fonte_usuario.lineEdit().setReadOnly(True)
        self.combo_fonte_usuario.lineEdit().setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel('Fonte do Usuário:'))
        layout.addWidget(self.combo_fonte_usuario)

        for font in QFontDatabase().families():
            self.combo_fonte_usuario.addItem(font)

        self.combo_tamanho_fonte_usuario = QComboBox(self)
        self.combo_tamanho_fonte_usuario.setEditable(True)
        self.combo_tamanho_fonte_usuario.lineEdit().setReadOnly(True)
        self.combo_tamanho_fonte_usuario.lineEdit().setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel('Tamanho da Fonte do Usuário:'))
        layout.addWidget(self.combo_tamanho_fonte_usuario)

        for size in range(8, 30):
            self.combo_tamanho_fonte_usuario.addItem(str(size))

        self.checkbox_resetar_fonte = QCheckBox('Resetar Fonte para Padrão', self)
        self.checkbox_resetar_fonte.stateChanged.connect(self.resetar_fonte_padrao)
        layout.addWidget(self.checkbox_resetar_fonte)

        botao_salvar = QPushButton('Salvar', self)
        botao_salvar.clicked.connect(self.salvar_configuracoes)
        layout.addWidget(botao_salvar)

        botao_cancelar = QPushButton('Cancelar', self)
        botao_cancelar.clicked.connect(self.voltar_janela_anterior)
        layout.addWidget(botao_cancelar)

        self.setLayout(layout)
        self.carregar_fontes()
        self.carregar_tamanhos_fonte()
        self.carregar_fontes_usuario()
        self.carregar_tamanhos_fonte_usuario()
        self.carregar_configuracoes_perso_usuario()

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
        QComboBox {{
            background-color: {estilo["line_edit"]["background-color"]};
            color: {estilo["line_edit"]["color"]};
        }}
        QCheckBox {{
            color: {estilo["label"]["color"]};
        }}
        """)
        if self.fonte_padrao and self.tamanho_fonte_padrao:
            self.setFont(QFont(self.fonte_padrao, int(self.tamanho_fonte_padrao)))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def selecionar_logo_principal(self):
        url, ok = QInputDialog.getText(self, 'Trocar imagem', 'Insira a URL da imagem:')
        if ok and url:
            self.mostrar_preview_imagem(url, 'logo_principal')

    def selecionar_logo_rodape(self):
        url, ok = QInputDialog.getText(self, 'Selecionar Logo Rodapé', 'Insira a URL da imagem:')
        if ok and url:
            self.mostrar_preview_imagem(url, 'logo_rodape')

    def mostrar_preview_imagem(self, url, tipo_logo):
        self.janela_preview = QWidget()
        self.janela_preview.setWindowTitle('Preview da Imagem')
        self.janela_preview.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        label_imagem = QLabel(self.janela_preview)
        label_imagem.setAlignment(Qt.AlignCenter)
        try:
            response = requests.get(url)
            response.raise_for_status()
            image_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            label_imagem.setPixmap(pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Erro ao carregar imagem: {e}")
            return

        layout.addWidget(label_imagem)

        botao_aprovar = QPushButton('Aprovar', self.janela_preview)
        botao_aprovar.clicked.connect(lambda: self.aprovar_imagem(url, tipo_logo))
        layout.addWidget(botao_aprovar, alignment=Qt.AlignCenter)

        botao_reprovar = QPushButton('Reprovar', self.janela_preview)
        botao_reprovar.clicked.connect(self.janela_preview.close)
        layout.addWidget(botao_reprovar, alignment=Qt.AlignCenter)

        self.janela_preview.setLayout(layout)
        self.janela_preview.show()

    def aprovar_imagem(self, url, tipo_logo):
        if tipo_logo == 'logo_principal':
            self.input_logo_principal.setText(url)
        elif tipo_logo == 'logo_rodape':
            self.input_logo_rodape.setText(url)
        self.janela_preview.close()

    def carregar_fontes(self):
        if self.usuario_logado['is_admin']:
            fontes = QFontDatabase().families()
            for fonte in fontes:
                self.combo_fonte_padrao.addItem(fonte)
                index = self.combo_fonte_padrao.findText(fonte)
                self.combo_fonte_padrao.setItemData(index, QFont(fonte), Qt.FontRole)
            self.combo_fonte_padrao.currentIndexChanged.connect(self.atualizar_preview_fonte)
            self.combo_fonte_padrao.view().setMouseTracking(True)
            self.combo_fonte_padrao.view().entered.connect(self.expandir_lista_fontes)
            self.combo_fonte_padrao.lineEdit().installEventFilter(self)

    def carregar_tamanhos_fonte(self):
        if self.usuario_logado['is_admin']:
            for tamanho in range(1, 101):
                self.combo_tamanho_fonte_padrao.addItem(str(tamanho))
            self.combo_tamanho_fonte_padrao.currentIndexChanged.connect(self.atualizar_preview_tamanho_fonte_padrao)
            self.combo_tamanho_fonte_padrao.view().setMouseTracking(True)
            self.combo_tamanho_fonte_padrao.view().entered.connect(self.expandir_lista_tamanhos)
            self.combo_tamanho_fonte_padrao.lineEdit().installEventFilter(self)

    def carregar_fontes_usuario(self):
        fontes = QFontDatabase().families()
        for fonte in fontes:
            self.combo_fonte_usuario.addItem(fonte)
            index = self.combo_fonte_usuario.findText(fonte)
            self.combo_fonte_usuario.setItemData(index, QFont(fonte), Qt.FontRole)
        self.combo_fonte_usuario.currentIndexChanged.connect(self.atualizar_preview_fonte_usuario)
        self.combo_fonte_usuario.view().setMouseTracking(True)
        self.combo_fonte_usuario.view().entered.connect(self.expandir_lista_fontes_usuario)
        self.combo_fonte_usuario.lineEdit().installEventFilter(self)

    def carregar_tamanhos_fonte_usuario(self):
        for tamanho in range(1, 101):
            self.combo_tamanho_fonte_usuario.addItem(str(tamanho))
        self.combo_tamanho_fonte_usuario.currentIndexChanged.connect(self.atualizar_preview_tamanho_fonte_usuario)
        self.combo_tamanho_fonte_usuario.view().setMouseTracking(True)
        self.combo_tamanho_fonte_usuario.view().entered.connect(self.expandir_lista_tamanhos_usuario)
        self.combo_tamanho_fonte_usuario.lineEdit().installEventFilter(self)

    def carregar_configuracoes_perso_usuario(self):
        try:
            carregar_preferencias = CarregarPreferenciasUsuario()
            preferencias = carregar_preferencias.carregar_preferencias_usuario(self.usuario_logado['id'])
            if preferencias:
                if self.usuario_logado['is_admin']:
                    carregar_config = CarregarConfiguracoes()
                    carregar_config.carregar_configuracoes()
                    self.input_logo_principal.setText(carregar_config.logo_principal)
                    self.input_logo_rodape.setText(carregar_config.logo_rodape)
                    self.combo_fonte_padrao.setCurrentText(carregar_config.fonte_padrao)
                    self.combo_tamanho_fonte_padrao.setCurrentText(str(carregar_config.tamanho_fonte_padrao))
                    self.combo_modo_padrao.setCurrentIndex(1 if carregar_config.modo_atual == 'escuro' else 0)

                fonte_perso = preferencias['fonte_perso']
                tamanho_fonte_perso = preferencias['tamanho_fonte_perso']
                fonte_alterada = preferencias['fonte_alterada']
                tamanho_fonte_alterado = preferencias['tamanho_fonte_alterado']
                if fonte_alterada:
                    self.combo_fonte_usuario.setCurrentText(fonte_perso)
                else:
                    carregar_config = CarregarConfiguracoes()
                    carregar_config.carregar_configuracoes()
                    self.combo_fonte_usuario.setCurrentText(carregar_config.fonte_padrao if self.usuario_logado['is_admin'] else "")
                if tamanho_fonte_alterado:
                    self.combo_tamanho_fonte_usuario.setCurrentText(str(tamanho_fonte_perso))
                else:
                    carregar_config = CarregarConfiguracoes()
                    carregar_config.carregar_configuracoes()
                    self.combo_tamanho_fonte_usuario.setCurrentText(str(carregar_config.tamanho_fonte_padrao if self.usuario_logado['is_admin'] else ""))
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao carregar configurações: {e}")

    def carregar_configuracoes_perso_usuario(self):
        try:
            carregar_preferencias = CarregarPreferenciasUsuario()
            preferencias = carregar_preferencias.carregar_preferencias_usuario(self.usuario_logado['id'])
            if preferencias:
                if self.usuario_logado['is_admin']:
                    carregar_config = CarregarConfiguracoes()
                    carregar_config.carregar_configuracoes()
                    self.input_logo_principal.setText(carregar_config.logo_principal)
                    self.input_logo_rodape.setText(carregar_config.logo_rodape)
                    self.combo_fonte_padrao.setCurrentText(carregar_config.fonte_padrao)
                    self.combo_tamanho_fonte_padrao.setCurrentText(str(carregar_config.tamanho_fonte_padrao))
                    self.combo_modo_padrao.setCurrentIndex(1 if carregar_config.modo_atual == 'escuro' else 0)

                fonte_perso = preferencias['fonte_perso']
                tamanho_fonte_perso = preferencias['tamanho_fonte_perso']
                fonte_alterada = preferencias['fonte_alterada']
                tamanho_fonte_alterado = preferencias['tamanho_fonte_alterado']
                if fonte_alterada:
                    self.combo_fonte_usuario.setCurrentText(fonte_perso)
                else:
                    carregar_config = CarregarConfiguracoes()
                    carregar_config.carregar_configuracoes()
                    self.combo_fonte_usuario.setCurrentText(carregar_config.fonte_padrao if self.usuario_logado['is_admin'] else "")
                if tamanho_fonte_alterado:
                    self.combo_tamanho_fonte_usuario.setCurrentText(str(tamanho_fonte_perso))
                else:
                    self.combo_tamanho_fonte_usuario.setCurrentText(str(carregar_config.tamanho_fonte_padrao if self.usuario_logado['is_admin'] else ""))
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao carregar configurações: {e}")

    def atualizar_preview_fonte(self):
        fonte = self.combo_fonte_padrao.currentText()
        self.combo_fonte_padrao.lineEdit().setFont(QFont(fonte))

    def atualizar_preview_tamanho_fonte_padrao(self):
        tamanho = self.combo_tamanho_fonte_padrao.currentText()
        self.combo_tamanho_fonte_padrao.lineEdit().setFont(QFont(self.combo_fonte_padrao.currentText(), int(tamanho)))

    def expandir_lista_fontes(self, _):
        self.combo_fonte_padrao.showPopup()

    def expandir_lista_tamanhos(self, _):
        self.combo_tamanho_fonte_padrao.showPopup()

    def atualizar_preview_fonte_usuario(self):
        fonte = self.combo_fonte_usuario.currentText()
        self.combo_fonte_usuario.lineEdit().setFont(QFont(fonte))

    def atualizar_preview_tamanho_fonte_usuario(self):
        tamanho = self.combo_tamanho_fonte_usuario.currentText()
        self.combo_tamanho_fonte_usuario.lineEdit().setFont(QFont(self.combo_fonte_usuario.currentText(), int(tamanho)))

    def expandir_lista_fontes_usuario(self, _):
        self.combo_fonte_usuario.showPopup()

    def expandir_lista_tamanhos_usuario(self, _):
        self.combo_tamanho_fonte_usuario.showPopup()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            if source == self.combo_fonte_usuario.lineEdit():
                self.combo_fonte_usuario.showPopup()
            elif source == self.combo_tamanho_fonte_usuario.lineEdit():
                self.combo_tamanho_fonte_usuario.showPopup()
        return super().eventFilter(source, event)

    def resetar_fonte_padrao(self, state):
        if state == Qt.Checked:
            self.combo_fonte_usuario.setCurrentText("")
            self.combo_tamanho_fonte_usuario.setCurrentText("")

    def salvar_configuracoes(self):
        caminho_logo_principal = self.input_logo_principal.text() if self.usuario_logado['is_admin'] else None
        caminho_logo_rodape = self.input_logo_rodape.text() if self.usuario_logado['is_admin'] else None
        fonte_padrao = self.combo_fonte_padrao.currentText() if self.usuario_logado['is_admin'] else None
        tamanho_fonte_padrao = self.combo_tamanho_fonte_padrao.currentText() if self.usuario_logado['is_admin'] else None
        modo_padrao = self.combo_modo_padrao.currentIndex() if self.usuario_logado['is_admin'] else None
        fonte_usuario = self.combo_fonte_usuario.currentText()
        tamanho_fonte_usuario = self.combo_tamanho_fonte_usuario.currentText()
        resetar_fonte = self.checkbox_resetar_fonte.isChecked()

        try:
            salvar_config = SalvarConfiguracoes()
            if self.usuario_logado['is_admin']:
                salvar_config.salvar_configuracoes(
                    caminho_logo_principal=caminho_logo_principal,
                    caminho_logo_rodape=caminho_logo_rodape,
                    fonte_padrao=fonte_padrao,
                    tamanho_fonte_padrao=tamanho_fonte_padrao,
                    modo_padrao=modo_padrao,
                    resetar_fonte=resetar_fonte,
                    fonte_usuario=fonte_usuario,
                    tamanho_fonte_usuario=tamanho_fonte_usuario,
                    usuario_logado=self.usuario_logado
                )
            else:
                salvar_config.editar_preferencias_usuario(
                    usuario_id=self.usuario_logado['id'],
                    nova_fonte_perso=fonte_usuario,
                    novo_tamanho_fonte_perso=tamanho_fonte_usuario
                )
            QMessageBox.information(self, 'Sucesso', 'Configurações salvas com sucesso.')
            self.voltar_janela_anterior()
        except AttributeError as e:
            if 'input_logo_principal' in str(e) or 'input_logo_rodape' in str(e):
                self.mostrar_erro("Erro ao salvar configurações: Atributo não encontrado. Verifique se você tem permissão de administrador.")
            else:
                self.mostrar_erro(f"Erro ao salvar configurações: {e}")
        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar configurações: {e}")

    def voltar_janela_anterior(self):
        self.janela_anterior = JanelaPrincipal(self.usuario_logado, self.modo)
        self.janela_anterior.show()
        self.close()

    def closeEvent(self, event):
        self.voltar_janela_anterior()
        event.accept()

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()

class PingThread(QThread):
    resultado_ping = pyqtSignal(str, str, str, dict, str)

    def __init__(self, usuario, ip, porta, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.ip = ip
        self.porta = porta
        self._is_running = True
        self._last_ping_time = None

    def run(self):
        current_time = datetime.now()
        if self._last_ping_time and (current_time - self._last_ping_time).seconds < 60:
            return

        ping = PingIP(self.ip)
        status = "Online" if ping.ping() else "Offline"
        if status == "Offline" or not self._is_running:
            self.resultado_ping.emit(self.usuario, self.ip, self.porta, {}, status)
            return

        monitor = MonitorDeHardware(self.ip, self.porta)
        dados = monitor.obter_info_hardware()
        if not dados or not self._is_running:
            self.resultado_ping.emit(self.usuario, self.ip, self.porta, {}, status)
            return

        extractor = ExtratorDeInfoHardware()
        info_extraida = extractor.obter_info(dados)
        specific_sensors = extractor.encontrar_sensores_especificos(info_extraida)
        self.resultado_ping.emit(self.usuario, self.ip, self.porta, specific_sensors, status)
        self._last_ping_time = current_time

    def stop(self):
        self._is_running = False
#Fim da classe JanelaConfigPrograma

#Inicio da classe JanelaDashboard
class SensorThread(QThread):
    resultado_sensor = pyqtSignal(str, str, str, dict)

    def __init__(self, usuario, ip, porta, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.ip = ip
        self.porta = porta
        self._is_running = True

    def run(self):
        while self._is_running:
            monitor = MonitorDeHardware(self.ip, self.porta)
            dados = monitor.obter_info_hardware()
            if not dados or not self._is_running:
                self.resultado_sensor.emit(self.usuario, self.ip, self.porta, {})
                return

            extractor = ExtratorDeInfoHardware()
            info_extraida = extractor.obter_info(dados)
            specific_sensors = extractor.encontrar_sensores_especificos(info_extraida)
            self.resultado_sensor.emit(self.usuario, self.ip, self.porta, specific_sensors)
            QThread.sleep(10)

    def stop(self):
        self._is_running = False
#Fim da classe JanelaDashboard

#Inicio da classe JanelaDashboard
class PingThread(QThread):
    resultado_ping = pyqtSignal(str, str, str, dict, str)

    def __init__(self, usuario, ip, porta, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.ip = ip
        self.porta = porta
        self._is_running = True
        self._last_ping_time = None

    def run(self):
        current_time = datetime.now()
        if self._last_ping_time and (current_time - self._last_ping_time).seconds < 60:
            return

        ping = PingIP(self.ip)
        status = "Online" if ping.ping() else "Offline"
        if status == "Offline" or not self._is_running:
            self.resultado_ping.emit(self.usuario, self.ip, self.porta, {}, status)
            return

        monitor = MonitorDeHardware(self.ip, self.porta)
        dados = monitor.obter_info_hardware()
        if not dados or not self._is_running:
            self.resultado_ping.emit(self.usuario, self.ip, self.porta, {}, status)
            return

        extractor = ExtratorDeInfoHardware()
        info_extraida = extractor.obter_info(dados)
        specific_sensors = extractor.encontrar_sensores_especificos(info_extraida)
        self.resultado_ping.emit(self.usuario, self.ip, self.porta, specific_sensors, status)
        self._last_ping_time = current_time

    def stop(self):
        self._is_running = False
#Fim da classe JanelaDashboard

#Inicio da classe JanelaDashboard
class SensorThread(QThread):
    resultado_sensor = pyqtSignal(str, str, str, dict)

    def __init__(self, usuario, ip, porta, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.ip = ip
        self.porta = porta
        self._is_running = True

    def run(self):
        while self._is_running:
            monitor = MonitorDeHardware(self.ip, self.porta)
            dados = monitor.obter_info_hardware()
            if not dados or not self._is_running:
                self.resultado_sensor.emit(self.usuario, self.ip, self.porta, {})
                return

            extractor = ExtratorDeInfoHardware()
            info_extraida = extractor.obter_info(dados)
            specific_sensors = extractor.encontrar_sensores_especificos(info_extraida)
            self.resultado_sensor.emit(self.usuario, self.ip, self.porta, specific_sensors)
            QThread.sleep(10) 

    def stop(self):
        self._is_running = False
#Final da classe JanelaDashboard

#Inicio da Classe JanelaDashboard
class JanelaDashboard(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.ping_threads = []
        self.sensor_threads = []
        self.dados_agrupados = {}
        self.tempo_restante = 10  # Inicializa o tempo restante para 10 segundos
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Dashboard')
        self.setGeometry(100, 100, 800, 600)
        self.center()

        layout = QVBoxLayout()

        self.tabela_dados = QTableWidget(self)
        self.tabela_dados.setColumnCount(4)
        self.tabela_dados.setHorizontalHeaderLabels(['PC', 'Sensor', 'Valor', 'Status'])
        layout.addWidget(self.tabela_dados)

        self.botao_atualizar = QPushButton('Atualizar', self)
        self.botao_atualizar.clicked.connect(self.atualizar_dados)
        layout.addWidget(self.botao_atualizar)

        if self.usuario_logado['is_admin']:
            self.botao_configurar = QPushButton('Configurar', self)
            self.botao_configurar.clicked.connect(self.abrir_janela_configuracao)
            layout.addWidget(self.botao_configurar)

        self.botao_voltar = QPushButton('Voltar', self)
        self.botao_voltar.clicked.connect(self.voltar_menu_principal)
        layout.addWidget(self.botao_voltar)

        # Adiciona um label para mostrar o tempo restante para atualização
        self.label_tempo_restante = QLabel(f'Tempo para atualização: {self.tempo_restante}s', self)
        self.label_tempo_restante.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label_tempo_restante, alignment=Qt.AlignRight)

        self.setLayout(layout)
        self.atualizar_dados()

        # Configurar o temporizador para atualizar os dados a cada 10 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.decrementar_tempo)
        self.timer.start(1000)  # 1000 milissegundos = 1 segundo

        self.carregar_preferencia_modo()
        self.aplicar_modo()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def decrementar_tempo(self):
        self.tempo_restante -= 1
        if self.tempo_restante <= 0:
            self.tempo_restante = 10  # Reinicia o tempo restante
        self.label_tempo_restante.setText(f'Tempo para atualização: {self.tempo_restante}s')

    def atualizar_dados(self):
        try:
            conexao = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            cursor = conexao.cursor()
            cursor.execute('''
                SELECT pc_salvo.id, usuarios.usuario, pc_salvo.ip, pc_salvo.porta
                FROM pc_salvo
                JOIN usuarios ON pc_salvo.usuario_id = usuarios.id
            ''')
            pcs_salvos = cursor.fetchall()

            self.dados_agrupados.clear()
            for pc in pcs_salvos:
                _, usuario, ip, porta = pc
                ping_thread = PingThread(usuario, ip, porta)
                ping_thread.resultado_ping.connect(self.processar_resultado_ping)
                ping_thread.start()
                self.ping_threads.append(ping_thread)

                sensor_thread = SensorThread(usuario, ip, porta)
                sensor_thread.resultado_sensor.connect(self.processar_resultado_sensor)
                sensor_thread.start()
                self.sensor_threads.append(sensor_thread)
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao atualizar dados: {e}")
        finally:
            if conexao.is_connected():
                cursor.close()
                conexao.close()

    def processar_resultado_ping(self, usuario, ip, porta, specific_sensors, status):
        chave = f"{usuario} ({ip}:{porta})"
        if chave not in self.dados_agrupados:
            self.dados_agrupados[chave] = {"status": status, "sensores": {}}

        if status == "Offline":
            self.dados_agrupados[chave]["status"] = status
        else:
            self.dados_agrupados[chave]["sensores"].update(specific_sensors)

        self.atualizar_tabela()

    def processar_resultado_sensor(self, usuario, ip, porta, specific_sensors):
        chave = f"{usuario} ({ip}:{porta})"
        if chave not in self.dados_agrupados:
            self.dados_agrupados[chave] = {"status": "Online", "sensores": {}}

        self.dados_agrupados[chave]["sensores"].update(specific_sensors)
        self.atualizar_tabela()

    def atualizar_tabela(self):
        self.tabela_dados.setRowCount(0)  # Clear the table before updating
        for pc, dados in self.dados_agrupados.items():
            status = dados["status"]
            sensores = dados["sensores"]
            if not sensores:
                row_position = self.tabela_dados.rowCount()
                self.tabela_dados.insertRow(row_position)
                self.tabela_dados.setItem(row_position, 0, QTableWidgetItem(pc))
                self.tabela_dados.setItem(row_position, 1, QTableWidgetItem("N/A"))
                self.tabela_dados.setItem(row_position, 2, QTableWidgetItem("N/A"))
                self.tabela_dados.setItem(row_position, 3, QTableWidgetItem(status))
            else:
                for sensor, valor in sensores.items():
                    row_position = self.tabela_dados.rowCount()
                    self.tabela_dados.insertRow(row_position)
                    self.tabela_dados.setItem(row_position, 0, QTableWidgetItem(pc))
                    self.tabela_dados.setItem(row_position, 1, QTableWidgetItem(sensor))
                    self.tabela_dados.setItem(row_position, 2, QTableWidgetItem(str(valor) if valor else 'N/A'))
                    self.tabela_dados.setItem(row_position, 3, QTableWidgetItem(status))

    def abrir_janela_configuracao(self):
        self.janela_configuracao = JanelaConfigurarPCs(self.usuario_logado, self.modo, self)
        self.janela_configuracao.show()

    def voltar_menu_principal(self):
        self.timer.stop()
        for thread in self.ping_threads + self.sensor_threads:
            thread.stop()
            thread.wait()
        self.janela_principal = JanelaPrincipal(self.usuario_logado, self.modo)
        self.janela_principal.show()
        self.close()

    def closeEvent(self, event):
        self.timer.stop()
        for thread in self.ping_threads + self.sensor_threads:
            thread.stop()
            thread.wait()
        self.voltar_menu_principal()
        event.accept()

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()

    def carregar_preferencia_modo(self):
        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT modo_tela, fonte_perso, tamanho_fonte_perso FROM preferenciais_usuarios WHERE usuario_id = %s', (self.usuario_logado['id'],))
                preferencia = cursor.fetchone()
                if preferencia:
                    self.modo.modo_atual = 'escuro' if preferencia[0] == 1 else 'claro'
                    self.fonte_padrao = preferencia[1] if preferencia[1] else self.fonte_padrao
                    self.tamanho_fonte_padrao = preferencia[2] if preferencia[2] else self.tamanho_fonte_padrao
                    self.aplicar_modo()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao carregar preferência de modo: {e}")

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
#Fim da classe JanelaDashboard

#Inicio da classe JanelaConfigurarPCs
class JanelaConfigurarPCs(QWidget):
    def __init__(self, usuario_logado, modo, parent_dashboard):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.parent_dashboard = parent_dashboard
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Configurar PCs Salvos')
        self.setGeometry(100, 100, 600, 400)
        self.center()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Configure os PCs salvos:', self)
        layout.addWidget(self.label_instrucoes, alignment=Qt.AlignTop)

        self.lista_usuarios = QListWidget(self)
        layout.addWidget(QLabel('Selecione o usuário:'))
        layout.addWidget(self.lista_usuarios)

        self.input_ip = QLineEdit(self)
        layout.addWidget(QLabel('IP:'))
        layout.addWidget(self.input_ip)

        self.input_porta = QLineEdit(self)
        layout.addWidget(QLabel('Porta:'))
        layout.addWidget(self.input_porta)

        self.botao_salvar = QPushButton('Salvar', self)
        self.botao_salvar.clicked.connect(self.salvar_pc)
        layout.addWidget(self.botao_salvar)

        self.botao_voltar = QPushButton('Voltar', self)
        self.botao_voltar.clicked.connect(self.voltar_dashboard)
        layout.addWidget(self.botao_voltar)

        self.setLayout(layout)
        self.carregar_usuarios()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def carregar_usuarios(self):
        try:
            conexao = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            cursor = conexao.cursor()
            cursor.execute('SELECT id, usuario FROM usuarios')
            usuarios = cursor.fetchall()
            for usuario in usuarios:
                item = QListWidgetItem(f"ID: {usuario[0]} | Usuário: {usuario[1]}")
                item.setData(Qt.UserRole, usuario[0])
                self.lista_usuarios.addItem(item)
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao carregar usuários: {e}")
        finally:
            if conexao.is_connected():
                cursor.close()
                conexao.close()

    def salvar_pc(self):
        item_selecionado = self.lista_usuarios.currentItem()
        if not item_selecionado:
            self.mostrar_erro("Por favor, selecione um usuário.")
            return

        usuario_id = item_selecionado.data(Qt.UserRole)
        ip = self.input_ip.text()
        porta = self.input_porta.text()

        if not ip or not porta:
            self.mostrar_erro("Todos os campos são obrigatórios.")
            return

        try:
            conexao = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            cursor = conexao.cursor()
            cursor.execute('''
                INSERT INTO pc_salvo (usuario_id, ip, porta) VALUES (%s, %s, %s)
            ''', (usuario_id, ip, porta))
            conexao.commit()
            QMessageBox.information(self, 'Sucesso', 'PC salvo com sucesso.')
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao salvar PC: {e}")
        finally:
            if conexao.is_connected():
                cursor.close()
                conexao.close()

    def voltar_dashboard(self):
        self.parent_dashboard.show()
        self.close()

    def closeEvent(self, event):
        self.voltar_dashboard()
        event.accept()

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaConfigurarPCs


if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        janela = JanelaLogin()
        janela.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, 'Erro Fatal', f"Ocorreu um erro fatal: {e}")
        sys.exit(1)
