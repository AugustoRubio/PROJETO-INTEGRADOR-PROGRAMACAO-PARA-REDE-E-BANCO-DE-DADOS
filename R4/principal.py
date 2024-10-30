#Arquivo principal é o responsável por iniciar a aplicação e construir as janelas gráficas.
#Usando as bibliotecas sys (para acessar variáveis do sistema), sqlite3 (para acessar o banco de dados), hashlib (para criptografar a senha)
#Usando as bibliotecas QtWidgets (para criar a interface gráfica), QDesktopWidget (para centralizar a janela na tela), QCheckBox (para criar caixas de seleção), QListWidget (para criar listas), QListWidgetItem (para adicionar itens na lista), QCalendarWidget (para criar um calendário), QComboBox (para criar uma caixa de seleção);
#QTableWidget (para criar tabelas), QTableWidgetItem (para adicionar itens na tabela), QVBoxLayout (para organizar os widgets verticalmente), QHBoxLayout (para organizar os widgets horizontalmente), QWidget (classe base para todos os widgets), QLabel (para adicionar texto), QLineEdit (para adicionar campos de entrada de texto);
#QPushButton (para adicionar botões), QMessageBox (para exibir mensagens), QPixmap (para exibir imagens), QFont (para definir a fonte), QMovie (para exibir gifs), QIcon (para adicionar ícones), QFontDatabase (para acessar a base de dados de fontes), QEvent (para eventos), QTimer (para temporizadores)
#Usando as classes ScannerRede e ScannerRedeExterno do arquivo scanner_rede.py, a Classe ConfigUsuarios do arquivo usuarios.py, a Classe ConfigProgramaDB do arquivo config_programa.py, a Classe modo do arquivo modos.py, a Classe GerenciadorBancoDados do arquivo criar_db.py
#Usando as classes MonitorDeHardware e ExtratorDeInfoHardware do arquivo dashboard.py
#Importação de bibliotecas
import sys
import subprocess
import importlib.util
class DependencyChecker:
    @staticmethod
    def check_and_install_dependencies():
        dependencies = [
            "PyQt5",
            "requests",
            "python-nmap",
            "mysql-connector-python"
        ]

        missing_dependencies = []
        for dependency in dependencies:
            if not importlib.util.find_spec(dependency):
                missing_dependencies.append(dependency)

        if missing_dependencies:
            print(f"Instalando dependências ausentes: {', '.join(missing_dependencies)}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_dependencies])
        else:
            print("Todas as dependências estão instaladas.")

DependencyChecker.check_and_install_dependencies()

import sys
import mysql.connector
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QDesktopWidget, QCheckBox, QListWidget, QListWidgetItem, QCalendarWidget, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5.QtGui import QPixmap, QFont, QMovie, QIcon, QFontDatabase
from PyQt5.QtCore import Qt, QEvent, QTimer

import os
import configparser
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
#Importa as classes do arquivo config_programa.py, que cuida das funções de adicionar, editar e remover configurações do programa no banco de dados
from config_programa import ConfiguracaoProgramaDB
#Importa as classes do arquivo modos.py, que cuida das funções de trocar o modo de cores do programa
from modos import Modo
#Importa as classes do arquivo criar_db.py, que cuida das funções de criar o banco de dados e verificar se o banco de dados já existe
from criar_db import GerenciadorBancoDados
from modos import Modo
#Importa as classes do arquivo dashboard.py, que cuida das funções de monitorar o hardware e extrair informações do hardware
from dashboard import MonitorDeHardware, ExtratorDeInfoHardware
from scanner_rede import PingIP
from PyQt5.QtCore import QThread, pyqtSignal

#Começamos inicializando algumas variáveis do Scanner de Rede para que não ocorra erro de variável não definida
#Como a função de escanear a rede captura as informações nesse arquivo, é necessário inicializar as variáveis antes de chamar a função
#Essas variáveis são necessárias para a execução da função de escanear a rede
#Inicio da Classe JanelaVerInformacoes
class ScannerRede:
    #Inicializamos as variáveis que serão utilizadas na função de escanear a rede
    #Essas variáveis receberam os valores necesseários quando a função for chamada
    def __init__(self, portas_selecionadas, escaneamento_rapido):
        #Fazemos a inicialização das variáveis usando os valores passados como parâmetro e atribuimos o self para que possam ser acessadas em outras funções
        self.portas_selecionadas = portas_selecionadas
        self.escaneamento_rapido = escaneamento_rapido
    #Essa função é necessária para canaliar a recepção de dados para a função de escanear a rede e enviar os dados para o outro script
    def escanear(self):
        #Retornamos um valor padrão para que não ocorra erro de variável não definida.        
        return [("Host1", "00:11:22:33:44:55", "192.168.1.1", self.portas_selecionadas)]
#Fim da classe ScannerRede

#Essa classe executa uma checagem do banco de dados, removendo a necessidade de executar o script criar_db.py
#O script criar_db.py é executado automaticamente ao iniciar a aplicação, verificando se o banco de dados já existe e criando-o caso não exista
#Inicio da classe VerificarBancoDados
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

# Aqui verificamos se o script foi executado pelo arquivo gerado pelo PyInstaller ou se foi executado diretamente pelo arquivo principal.py
# Se o script foi executado pelo arquivo gerado pelo PyInstaller, usamos o caminho do executável, para que seja possível acessar os arquivos necessários como a pasta de apoio
# Se o script foi executado diretamente pelo arquivo principal.py, usamos o caminho do arquivo principal.py que seria a raiz do projeto
# Usamos a função getattr para verificar se o script foi empacotado pelo PyInstaller, passamos o sys como parâmetro e o atributo 'frozen' que é um atributo que é definido quando o script é empacotado pelo PyInstaller
if getattr(sys, 'frozen', False):
    # Se o script foi empacotado pelo PyInstaller, usamos o caminho do executável
    script_dir = os.path.dirname(sys.executable)
else:
    # Se o script estiver sendo executado normalmente, use o caminho do script
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Reforçamos o caminho do banco de dados, juntando o caminho do script com o nome do banco de dados
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'config.ini'))

host = config['mysql']['host']
user = config['mysql']['user']
password = config['mysql']['password']
database = config['mysql']['database']
port = config['mysql'].getint('port')

verificador_bd = VerificadorBancoDados(host, user, password, database, port)
verificador_bd.verificar_ou_criar_bd()

#Aqui criamos a aplicação gráfica.
#A aplicação é criada usando a classe QWidget que é a classe base para todos os widgets
class JanelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.modo = Modo()
        self.carregar_configuracoes()
        self.inicializarUI()
        self.timer = QTimer(self)

    def carregar_configuracoes(self):
        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT logo_principal, logo_rodape, fonte_padrao, tamanho_fonte_padrao, modo_global FROM config_programa WHERE id = 1')
                configuracao = cursor.fetchone()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao buscar configuração do banco de dados: {e}")
            return

        if configuracao:
            self.logo_principal, self.logo_rodape, self.fonte_padrao, self.tamanho_fonte_padrao, self.modo_global = configuracao
            self.modo.modo_atual = 'escuro' if self.modo_global == 1 else 'claro'
        else:
            self.mostrar_erro("Configuração não encontrada no banco de dados.")
            return

    def inicializarUI(self):
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.layout = QVBoxLayout()

        if self.logo_principal:
            self.label_logo_principal = QLabel(self)
            self.label_logo_principal.setAlignment(Qt.AlignCenter)
            if self.logo_principal.endswith('.gif'):
                self.movie_logo_principal = QMovie(self.logo_principal)
                self.label_logo_principal.setMovie(self.movie_logo_principal)
                self.movie_logo_principal.start()
            else:
                self.pixmap_logo_principal = QPixmap(self.logo_principal)
                self.label_logo_principal.setPixmap(self.pixmap_logo_principal.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.layout.addWidget(self.label_logo_principal)

        if self.fonte_padrao and self.tamanho_fonte_padrao:
            self.setFont(QFont(self.fonte_padrao, self.tamanho_fonte_padrao))

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
        self.adicionar_botao_modo()

        self.input_senha.returnPressed.connect(self.verificar_login)

        if self.logo_rodape:
            self.label_logo_rodape = QLabel(self)
            self.label_logo_rodape.setAlignment(Qt.AlignCenter)
            self.pixmap_logo_rodape = QPixmap(self.logo_rodape)
            self.label_logo_rodape.setPixmap(self.pixmap_logo_rodape.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.layout.addWidget(self.label_logo_rodape)

    def verificar_login(self):
        usuario = self.input_usuario.text()
        senha = self.input_senha.text()

        if not usuario or not senha:
            QMessageBox.warning(self, 'Erro', 'Por favor, preencha todos os campos.')
            return

        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT id, senha, ultimo_login FROM usuarios WHERE usuario = %s', (usuario,))
                resultado = cursor.fetchone()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao verificar login: {e}")
            return

        if resultado:
            usuario_id, senha_armazenada, ultimo_login = resultado
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()

            if senha_hash == senha_armazenada:
                if usuario_id == 1 and not ultimo_login:
                    self.mostrar_tela_alterar_senha(usuario)
                else:
                    self.registrar_login(usuario)
                    self.abrir_janela_principal()
            else:
                QMessageBox.warning(self, 'Erro', 'Senha incorreta.')
        else:
            QMessageBox.warning(self, 'Erro', 'Usuário não encontrado.')

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

        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT senha FROM usuarios WHERE usuario = %s', (usuario,))
                senha_atual_hash = cursor.fetchone()[0]
                nova_senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()

                if nova_senha_hash == senha_atual_hash:
                    self.mostrar_erro("A nova senha não pode ser igual à senha atual.")
                    return

                cursor.execute('UPDATE usuarios SET senha = %s, ultimo_login = %s WHERE usuario = %s', (nova_senha_hash, datetime.now(), usuario))
                conexao.commit()
                QMessageBox.information(self, 'Sucesso', 'Senha alterada com sucesso.')
                self.janela_alterar_senha.close()
                self.registrar_login(usuario)
                self.abrir_janela_principal()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao alterar senha: {e}")

    def registrar_login(self, usuario):
        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conexao:
                cursor = conexao.cursor()
                data_hora_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('UPDATE usuarios SET ultimo_login = %s WHERE usuario = %s', (data_hora_atual, usuario))
                conexao.commit()
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
        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT id, usuario, is_admin FROM usuarios WHERE usuario = %s', (self.input_usuario.text(),))
                resultado = cursor.fetchone()
                if resultado:
                    return {'id': resultado[0], 'usuario': resultado[1], 'is_admin': resultado[2]}
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao obter usuário logado: {e}")
        return None

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()

    def adicionar_botao_modo(self):
        self.switch_modo = QPushButton(self)
        self.switch_modo.setMaximumWidth(150)
        self.switch_modo.setCheckable(True)
        self.switch_modo.setChecked(self.modo.modo_atual == 'escuro')
        self.switch_modo.clicked.connect(self.trocar_modo)
        self.layout.addWidget(self.switch_modo, alignment=Qt.AlignRight)
        self.atualizar_switch()

    def trocar_modo(self):
        self.modo.trocar_modo()
        self.atualizar_switch()
        self.salvar_modo_global()

    def atualizar_switch(self):
        estilo = self.modo.atualizar_switch()
        self.switch_modo.setIcon(QIcon(estilo.get("icone", "")))
        self.switch_modo.setIcon(QIcon(estilo["icone"]))
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
        if self.fonte_padrao and self.tamanho_fonte_padrao:
            self.setFont(QFont(self.fonte_padrao, self.tamanho_fonte_padrao))

    def salvar_modo_global(self):
        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conexao:
                cursor = conexao.cursor()
                modo_global = 1 if self.modo.modo_atual == 'escuro' else 0
                cursor.execute('UPDATE config_programa SET modo_global = %s WHERE id = 1', (modo_global,))
                conexao.commit()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao salvar modo global: {e}")

#Começo da classe JanelaPrincipal
class JanelaPrincipal(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__() 
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Janela Principal')
        self.setGeometry(0, 0, 300, 200)
        self.center()

        layout = QVBoxLayout()

        # Adicionar informações do usuário logado no canto superior esquerdo da janela
        self.label_usuario_logado = QLabel(f"Usuário: {self.usuario_logado['usuario']} ({'Admin' if self.usuario_logado['is_admin'] else 'Comum'})", self)
        self.label_usuario_logado.setAlignment(Qt.AlignLeft)

        # Adicionar switch de modo claro/escuro no canto superior direito
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
            if event:
                event.accept()
            else:
                self.close()
        else:
            if event:
                event.ignore()

    def executar_scanner_rede(self):
        self.janela_scanner_rede = JanelaScannerRede(self.usuario_logado, self.modo)
        self.janela_scanner_rede.show()
        self.hide()  # Use hide() instead of close() to prevent triggering closeEvent

    def abrir_janela_config_usuarios(self):
        self.janela_config_usuarios = JanelaConfigUsuarios(self.usuario_logado, self.modo)
        self.janela_config_usuarios.show()
        self.hide()

    def abrir_janela_config_programa(self):
        if self.usuario_logado['is_admin']:
            self.janela_config_programa = JanelaConfigPrograma(self.usuario_logado, self.modo)
            self.janela_config_programa.show()
            self.hide()
        else:
            QMessageBox.warning(self, 'Acesso Negado', 'Somente administradores podem acessar as configurações do programa.')

    def abrir_dashboard(self):
        self.janela_dashboard = JanelaDashboard(self.usuario_logado, self.modo)
        self.janela_dashboard.show()
        self.hide()

    def trocar_modo(self):
        self.modo.trocar_modo()
        self.atualizar_switch()

    def atualizar_switch(self):
        estilo = self.modo.atualizar_switch()
        self.switch_modo.setIcon(QIcon(estilo["icone"]))
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
            font-family: {estilo["widget"]["font-family"]};
            font-size: {estilo["widget"]["font-size"]};
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
#Fim da classe JanelaPrincipal

#Começo da classe JanelaScannerRede
class JanelaScannerRede(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Scanner de Rede')
        self.setGeometry(100, 100, 400, 300)
        self.center()

        layout = QVBoxLayout()

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

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    def abrir_janela_opcoes_scanner(self):
        self.janela_opcoes_scanner = JanelaOpcoesScanner(self.usuario_logado, self.modo)
        self.janela_opcoes_scanner.show()

    def abrir_janela_ver_informacoes(self):
        self.janela_ver_informacoes = JanelaVerInformacoes()
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

#Inicio da classe JanelaOpcoesScanner
class JanelaOpcoesScanner(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Opções de Scanner de Rede')
        self.setGeometry(100, 100, 400, 300)
        self.center()

        layout = QVBoxLayout()

        # Adicionar label para mostrar a rede atual do usuário
        self.label_rede_atual = QLabel('Rede Atual: Obtendo...', self)
        layout.addWidget(self.label_rede_atual)

        # Adicionar checkboxes para seleção de portas
        self.checkbox_escanear_rapido = QCheckBox('Escaneamento Rápido', self)
        self.checkbox_escanear_rapido.setChecked(True)
        layout.addWidget(self.checkbox_escanear_rapido)

        self.checkbox_porta_22 = QCheckBox('Porta 22 (SSH)', self)
        self.checkbox_porta_22.setChecked(False)
        layout.addWidget(self.checkbox_porta_22)

        self.checkbox_porta_80 = QCheckBox('Porta 80 (HTTP)', self)
        self.checkbox_porta_80.setChecked(False)
        layout.addWidget(self.checkbox_porta_80)

        self.checkbox_porta_443 = QCheckBox('Porta 443 (HTTPS)', self)
        self.checkbox_porta_443.setChecked(False)
        layout.addWidget(self.checkbox_porta_443)

        self.botao_escanear_rede = QPushButton('Escanear', self)
        self.botao_escanear_rede.clicked.connect(self.escanear_rede)
        layout.addWidget(self.botao_escanear_rede)

        self.botao_voltar = QPushButton('Voltar', self)
        self.botao_voltar.clicked.connect(self.close)
        layout.addWidget(self.botao_voltar)

        self.setLayout(layout)

        # Atualizar a rede atual do usuário
        self.atualizar_rede_atual()

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

    def escanear_rede(self):
        try:
            portas_selecionadas = []
            if self.checkbox_porta_22.isChecked():
                portas_selecionadas.append('22')
            if self.checkbox_porta_80.isChecked():
                portas_selecionadas.append('80')
            if self.checkbox_porta_443.isChecked():
                portas_selecionadas.append('443')

            escaneamento_rapido = self.checkbox_escanear_rapido.isChecked()

            # Importar e usar a classe ScannerRede do arquivo scanner_rede.py
            scanner = ScannerRedeExterno(portas_selecionadas, escaneamento_rapido)
            resultados = scanner.escanear()

            # Exibir os resultados em uma nova janela
            self.mostrar_resultados(resultados)
        except Exception as e:
            self.mostrar_erro(f"Erro ao escanear rede: {e}")

    def mostrar_resultados(self, resultados):
        self.janela_resultados = QWidget()
        self.janela_resultados.setWindowTitle('Resultados do Escaneamento')
        self.janela_resultados.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        texto_resultados = "\n".join([
            f"Nome do Host: {r[0]} | MAC: {r[1]} | IP: {r[2]} | Portas: {r[3]}"
            for r in resultados
        ])
        label_resultados = QLabel(texto_resultados)
        label_resultados.setAlignment(Qt.AlignTop)
        layout.addWidget(label_resultados)

        botao_fechar = QPushButton('Fechar', self.janela_resultados)
        botao_fechar.clicked.connect(self.janela_resultados.close)
        layout.addWidget(botao_fechar)

        self.janela_resultados.setLayout(layout)
        self.janela_resultados.show()

        # Check if the scan is completed and show a message
        if hasattr(self, 'escaneamento_concluido') and self.escaneamento_concluido:
            QMessageBox.information(self.janela_resultados, 'Escaneamento Concluído', 'O escaneamento foi concluído com sucesso!')

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaOpcoesScanner

#Inicio da classe JanelaVerInformacoes
class JanelaVerInformacoes(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Informações Armazenadas')
        self.setGeometry(100, 100, 600, 400)
        self.center()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Selecione a data no calendário:', self)
        layout.addWidget(self.label_instrucoes)

        self.calendario = QCalendarWidget(self)
        self.calendario.setSelectedDate(datetime.now().date())
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

        try:
            conexao = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM scanner WHERE data LIKE %s', (f'%{data_selecionada}%',))
            resultados = cursor.fetchall()

            if not resultados:
                self.mostrar_erro("Nenhuma informação encontrada para a data selecionada.")
                return

            self.janela_resultados = QWidget()
            self.janela_resultados.setWindowTitle('Informações Armazenadas')
            self.janela_resultados.setGeometry(100, 100, 600, 400)
            layout = QVBoxLayout()

            texto_resultados = "\n".join([
                f"ID: {r[0]} | Data: {r[1]} | Hostname: {r[2]} | MAC: {r[3]} | IP: {r[4]} | Portas: {r[5]}"
                for r in resultados
            ])
            label_resultados = QLabel(texto_resultados)
            label_resultados.setAlignment(Qt.AlignTop)
            layout.addWidget(label_resultados)

            botao_fechar = QPushButton('Fechar', self.janela_resultados)
            botao_fechar.clicked.connect(self.janela_resultados.close)
            layout.addWidget(botao_fechar)

            self.janela_resultados.setLayout(layout)
            self.janela_resultados.show()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao buscar informações: {e}")
        finally:
            if conexao.is_connected():
                cursor.close()
                conexao.close()

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaVerInformacoes

class JanelaConfigUsuarios(QWidget):
    def __init__(self, usuario_logado, modo):
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.config_usuarios = ConfigUsuarios(usuario_logado)
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Configurações de Usuários')
        self.setGeometry(100, 100, 600, 400)
        self.center()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Gerencie os usuários do sistema:', self)
        layout.addWidget(self.label_instrucoes, alignment=Qt.AlignTop)

        self.botao_adicionar_usuario = QPushButton('Adicionar Usuário', self)
        self.botao_adicionar_usuario.clicked.connect(self.adicionar_usuario)
        layout.addWidget(self.botao_adicionar_usuario, alignment=Qt.AlignTop)

        self.botao_alterar_senha = QPushButton('Alterar senhas', self)
        self.botao_alterar_senha.clicked.connect(self.alterar_senha)
        layout.addWidget(self.botao_alterar_senha, alignment=Qt.AlignTop)

        self.botao_remover_usuario = QPushButton('Remover Usuário', self)
        self.botao_remover_usuario.clicked.connect(self.remover_usuario)
        layout.addWidget(self.botao_remover_usuario, alignment=Qt.AlignTop)

        self.botao_ver_informacoes_usuarios = QPushButton('Ver informações e editar', self)
        self.botao_ver_informacoes_usuarios.clicked.connect(self.ver_informacoes_usuarios)
        layout.addWidget(self.botao_ver_informacoes_usuarios, alignment=Qt.AlignTop)

        self.botao_voltar = QPushButton('Voltar ao menu principal', self)
        self.botao_voltar.clicked.connect(self.voltar_menu_principal)
        layout.addWidget(self.botao_voltar, alignment=Qt.AlignTop)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        self.voltar_menu_principal()

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

        botao_salvar = QPushButton('Salvar', self.janela_adicionar)
        botao_salvar.clicked.connect(self.salvar_novo_usuario)
        layout.addWidget(botao_salvar)

        botao_cancelar = QPushButton('Cancelar', self.janela_adicionar)
        botao_cancelar.clicked.connect(self.janela_adicionar.close)
        layout.addWidget(botao_cancelar)

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
            self.janela_adicionar.close()
        except Exception as e:
            self.mostrar_erro(f"Erro ao adicionar usuário: {e}")

    def remover_usuario(self):
        if not self.usuario_logado['is_admin']:
            self.mostrar_erro("Somente administradores podem remover usuários.")
            return

        self.janela_remover = QWidget()
        self.janela_remover.setWindowTitle('Remover Usuário')
        self.janela_remover.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Selecione o usuário a remover:', self.janela_remover)
        layout.addWidget(self.label_instrucoes)

        self.lista_usuarios_remover = QListWidget(self.janela_remover)
        layout.addWidget(self.lista_usuarios_remover)

        try:
            usuarios = self.config_usuarios.listar_usuarios()
            for usuario in usuarios:
                item = QListWidgetItem(f"ID: {usuario[0]} | Usuário: {usuario[1]} | Nome: {usuario[2]} | Email: {usuario[3]} | Admin: {'Sim' if usuario[4] else 'Não'}")
                item.setData(Qt.UserRole, usuario)
                self.lista_usuarios_remover.addItem(item)
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar usuários: {e}")
            return

        botao_remover = QPushButton('Remover', self.janela_remover)
        botao_remover.clicked.connect(self.confirmar_remocao_usuario)
        layout.addWidget(botao_remover)

        botao_cancelar = QPushButton('Cancelar', self.janela_remover)
        botao_cancelar.clicked.connect(self.janela_remover.close)
        layout.addWidget(botao_cancelar)

        self.janela_remover.setLayout(layout)
        self.janela_remover.show()

    def confirmar_remocao_usuario(self):
        item_selecionado = self.lista_usuarios_remover.currentItem()
        if not item_selecionado:
            self.mostrar_erro("Por favor, selecione um usuário para remover.")
            return

        usuario = item_selecionado.data(Qt.UserRole)
        usuario_id = usuario[0]

        try:
            self.config_usuarios.remover_usuario(usuario_id)
            QMessageBox.information(self, 'Sucesso', 'Usuário removido com sucesso.')
            self.janela_remover.close()
        except Exception as e:
            self.mostrar_erro(f"Erro ao remover usuário: {e}")

    def ver_informacoes_usuarios(self):
        try:
            usuarios = self.config_usuarios.listar_usuarios()

            self.janela_ver_usuarios = QWidget()
            self.janela_ver_usuarios.setWindowTitle('Informações dos Usuários')
            
            # Set the width to a fixed value and height based on the number of users
            width = 800
            height = 100 + (len(usuarios) * 30) if usuarios else 200
            self.janela_ver_usuarios.setGeometry(100, 100, width, height)
            
            layout = QVBoxLayout()

            if not usuarios:
                label_usuario = QLabel("Nenhum usuário encontrado.")
                layout.addWidget(label_usuario)
            else:
                self.lista_usuarios = QListWidget(self.janela_ver_usuarios)
                for usuario in usuarios:
                    item = QListWidgetItem(f"ID: {usuario[0]} | Usuário: {usuario[1]} | Nome: {usuario[2]} | Email: {usuario[3]} | Admin: {'Sim' if usuario[4] else 'Não'}")
                    item.setData(Qt.UserRole, usuario)
                    self.lista_usuarios.addItem(item)
                layout.addWidget(self.lista_usuarios)

                if self.usuario_logado['is_admin']:
                    botao_editar = QPushButton('Editar', self.janela_ver_usuarios)
                    botao_editar.clicked.connect(self.editar_usuario_selecionado)
                    layout.addWidget(botao_editar)

            botao_fechar = QPushButton('Fechar', self.janela_ver_usuarios)
            botao_fechar.clicked.connect(self.janela_ver_usuarios.close)
            layout.addWidget(botao_fechar)

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
        layout = QVBoxLayout()

        self.input_usuario = QLineEdit(self.janela_edicao)
        self.input_usuario.setText(usuario[1])
        layout.addWidget(QLabel('Usuário:'))
        layout.addWidget(self.input_usuario)

        self.input_nome_completo = QLineEdit(self.janela_edicao)
        self.input_nome_completo.setText(usuario[2])
        layout.addWidget(QLabel('Nome Completo:'))
        layout.addWidget(self.input_nome_completo)

        self.input_email = QLineEdit(self.janela_edicao)
        self.input_email.setText(usuario[3])
        layout.addWidget(QLabel('Email:'))
        layout.addWidget(self.input_email)

        self.checkbox_is_admin = QCheckBox('Administrador', self.janela_edicao)
        self.checkbox_is_admin.setChecked(usuario[4])
        layout.addWidget(self.checkbox_is_admin, alignment=Qt.AlignCenter)

        botao_salvar = QPushButton('Salvar', self.janela_edicao)
        botao_salvar.clicked.connect(lambda: self.salvar_edicao_usuario(usuario[0]))
        layout.addWidget(botao_salvar)

        botao_cancelar = QPushButton('Cancelar', self.janela_edicao)
        botao_cancelar.clicked.connect(self.janela_edicao.close)
        layout.addWidget(botao_cancelar)

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
            layout = QVBoxLayout()

            self.label_instrucoes = QLabel('Selecione o usuário para alterar a senha:', self.janela_selecionar_usuario)
            layout.addWidget(self.label_instrucoes)

            self.lista_usuarios = QListWidget(self.janela_selecionar_usuario)
            layout.addWidget(self.lista_usuarios)

            try:
                usuarios = self.config_usuarios.listar_usuarios()
                for usuario in usuarios:
                    item = QListWidgetItem(f"ID: {usuario[0]} | Usuário: {usuario[1]} | Nome: {usuario[2]} | Email: {usuario[3]} | Admin: {'Sim' if usuario[4] else 'Não'}")
                    item.setData(Qt.UserRole, usuario)
                    self.lista_usuarios.addItem(item)
            except Exception as e:
                self.mostrar_erro(f"Erro ao buscar usuários: {e}")
                return

            botao_selecionar = QPushButton('Selecionar', self.janela_selecionar_usuario)
            botao_selecionar.clicked.connect(self.selecionar_usuario_para_alterar_senha)
            layout.addWidget(botao_selecionar)

            botao_cancelar = QPushButton('Cancelar', self.janela_selecionar_usuario)
            botao_cancelar.clicked.connect(self.janela_selecionar_usuario.close)
            layout.addWidget(botao_cancelar)

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
        layout.addWidget(botao_salvar)

        botao_cancelar = QPushButton('Cancelar', self.janela_alterar_senha)
        botao_cancelar.clicked.connect(self.janela_alterar_senha.close)
        layout.addWidget(botao_cancelar)

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
        self.show()
# Fim da classe JanelaConfigUsuarios

#Inicio da classe JanelaConfigPrograma
class JanelaConfigPrograma(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Configurações do Programa')
        self.setGeometry(100, 100, 600, 400)
        self.center()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Configure as opções do programa:', self)
        layout.addWidget(self.label_instrucoes, alignment=Qt.AlignTop)

        self.input_logo_principal = QLineEdit(self)
        layout.addWidget(QLabel('Logo Principal:'))
        layout.addWidget(self.input_logo_principal)

        self.botao_logo_principal = QPushButton('Selecionar Logo Principal', self)
        self.botao_logo_principal.clicked.connect(self.selecionar_logo_principal)
        layout.addWidget(self.botao_logo_principal)

        self.input_logo_rodape = QLineEdit(self)
        layout.addWidget(QLabel('Logo Rodapé:'))
        layout.addWidget(self.input_logo_rodape)

        self.botao_logo_rodape = QPushButton('Selecionar Logo Rodapé', self)
        self.botao_logo_rodape.clicked.connect(self.selecionar_logo_rodape)
        layout.addWidget(self.botao_logo_rodape)

        self.combo_fonte_padrao = QComboBox(self)
        self.combo_fonte_padrao.setEditable(True)
        self.combo_fonte_padrao.lineEdit().setReadOnly(True)
        self.combo_fonte_padrao.lineEdit().setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel('Fonte Global:'))
        layout.addWidget(self.combo_fonte_padrao)

        self.combo_tamanho_fonte_padrao = QComboBox(self)
        self.combo_tamanho_fonte_padrao.setEditable(True)
        self.combo_tamanho_fonte_padrao.lineEdit().setReadOnly(True)
        self.combo_tamanho_fonte_padrao.lineEdit().setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel('Tamanho da Fonte Global:'))
        layout.addWidget(self.combo_tamanho_fonte_padrao)

        self.combo_fonte_usuario = QComboBox(self)
        self.combo_fonte_usuario.setEditable(True)
        self.combo_fonte_usuario.lineEdit().setReadOnly(True)
        self.combo_fonte_usuario.lineEdit().setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel('Fonte do Usuário:'))
        layout.addWidget(self.combo_fonte_usuario)

        self.combo_tamanho_fonte_usuario = QComboBox(self)
        self.combo_tamanho_fonte_usuario.setEditable(True)
        self.combo_tamanho_fonte_usuario.lineEdit().setReadOnly(True)
        self.combo_tamanho_fonte_usuario.lineEdit().setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel('Tamanho da Fonte do Usuário:'))
        layout.addWidget(self.combo_tamanho_fonte_usuario)

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
        self.carregar_configuracoes()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def selecionar_logo_principal(self):
        caminho_logo, _ = QFileDialog.getOpenFileName(self, 'Selecionar Logo Principal', '', 'Images (*.png *.jpg *.bmp)')
        if caminho_logo:
            self.input_logo_principal.setText(caminho_logo)

    def selecionar_logo_rodape(self):
        caminho_logo, _ = QFileDialog.getOpenFileName(self, 'Selecionar Logo Rodapé', '', 'Images (*.png *.jpg *.bmp)')
        if caminho_logo:
            self.input_logo_rodape.setText(caminho_logo)

    def carregar_fontes(self):
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
        for tamanho in range(1, 101):
            self.combo_tamanho_fonte_padrao.addItem(str(tamanho))
        self.combo_tamanho_fonte_padrao.currentIndexChanged.connect(self.atualizar_preview_tamanho_fonte_padrao)
        self.combo_tamanho_fonte_padrao.view().setMouseTracking(True)
        self.combo_tamanho_fonte_padrao.view().entered.connect(self.expandir_lista_tamanhos)
        self.combo_tamanho_fonte_padrao.lineEdit().installEventFilter(self)

    def carregar_configuracoes(self):
        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT logo_principal, logo_rodape, fonte_padrao, tamanho_fonte_padrao FROM config_programa WHERE id = 1')
                configuracao = cursor.fetchone()
                if configuracao:
                    self.input_logo_principal.setText(configuracao[0])
                    self.input_logo_rodape.setText(configuracao[1])
                    self.combo_fonte_padrao.setCurrentText(configuracao[2])
                    self.combo_tamanho_fonte_padrao.setCurrentText(str(configuracao[3]))

                cursor.execute('SELECT fonte_perso, tamanho_fonte_perso, fonte_alterada, tamanho_fonte_alterado FROM preferenciais_usuarios WHERE usuario_id = %s', (self.usuario_logado['id'],))
                preferencia_usuario = cursor.fetchone()
                if preferencia_usuario:
                    fonte_perso, tamanho_fonte_perso, fonte_alterada, tamanho_fonte_alterado = preferencia_usuario
                    if fonte_alterada:
                        self.combo_fonte_usuario.setCurrentText(fonte_perso)
                    else:
                        self.combo_fonte_usuario.setCurrentText(configuracao[2])
                    if tamanho_fonte_alterado:
                        self.combo_tamanho_fonte_usuario.setCurrentText(str(tamanho_fonte_perso))
                    else:
                        self.combo_tamanho_fonte_usuario.setCurrentText(str(configuracao[3]))
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

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            if source == self.combo_fonte_padrao.lineEdit():
                self.combo_fonte_padrao.showPopup()
            elif source == self.combo_tamanho_fonte_padrao.lineEdit():
                self.combo_tamanho_fonte_padrao.showPopup()
        return super().eventFilter(source, event)
    
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

    def salvar_configuracoes(self):
        logo_principal = self.input_logo_principal.text()
        logo_rodape = self.input_logo_rodape.text()
        fonte_padrao = self.combo_fonte_padrao.currentText()
        tamanho_fonte_padrao = self.combo_tamanho_fonte_padrao.currentText()
        fonte_usuario = self.combo_fonte_usuario.currentText()
        tamanho_fonte_usuario = self.combo_tamanho_fonte_usuario.currentText()

        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conexao:
                cursor = conexao.cursor()
                cursor.execute('''
                    UPDATE config_programa
                    SET logo_principal = %s, logo_rodape = %s, fonte_padrao = %s, tamanho_fonte_padrao = %s
                    WHERE id = 1
                ''', (logo_principal, logo_rodape, fonte_padrao, tamanho_fonte_padrao))

                cursor.execute('''
                    UPDATE preferenciais_usuarios
                    SET fonte_perso = %s, tamanho_fonte_perso = %s, fonte_alterada = %s, tamanho_fonte_alterado = %s
                    WHERE usuario_id = %s
                ''', (fonte_usuario, tamanho_fonte_usuario, 1, 1, self.usuario_logado['id']))

                conexao.commit()
                QMessageBox.information(self, 'Sucesso', 'Configurações atualizadas com sucesso.')
                self.voltar_janela_anterior()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Erro', f"Erro ao salvar configurações: {e}")

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
            QThread.sleep(10)  # Sleep for 10 seconds before the next update

    def stop(self):
        self._is_running = False

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        janela = JanelaLogin()
        janela.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, 'Erro Fatal', f"Ocorreu um erro fatal: {e}")
        sys.exit(1)