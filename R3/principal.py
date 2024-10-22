#Arquivo principal é o responsável por iniciar a aplicação e construir as janelas gráficas.
#Usando as bibliotecas sys (para acessar variáveis do sistema), sqlite3 (para acessar o banco de dados), hashlib (para criptografar a senha)
#Usando as bibliotecas gráficas do PyQt5.QtWidgets (para criar janelas, botões, caixas de texto, etc), PyQt5.QtGui (para gerenciar recursos gráficos), PyQt5.QtCore (para gerenciar recursos não gráficos)
#Usando as classes ScannerRede e ScannerRedeExterno do arquivo scanner_rede.py, a Classe ConfigUsuarios do arquivo usuarios.py, a Classe ConfigProgramaDB do arquivo config_programa.py, a Classe modo do arquivo modos.py, a Classe GerenciadorBancoDados do arquivo criar_db.py
#Usando as classes MonitorDeHardware e ExtratorDeInfoHardware do arquivo dashboard.py
#Importação de bibliotecas
import sys
import sqlite3
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QDesktopWidget, QCheckBox, QListWidget, QListWidgetItem, QCalendarWidget, QComboBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QFont, QMovie, QIcon, QFontDatabase
from PyQt5.QtCore import Qt, QEvent, QTimer
import os
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
#Importa as classes do arquivo dashboard.py, que cuida das funções de monitorar o hardware e extrair informações do hardware
from dashboard import MonitorDeHardware
#Importa as classes do arquivo dashboard.py, que cuida das funções de monitorar o hardware e extrair informações do hardware
from dashboard import ExtratorDeInfoHardware

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
    #Inicializamos a classe com o caminho do banco de dados
    #Representamos o caminho do banco de dados como uma variável de classe
    def __init__(self, caminho_bd):
        self.caminho_bd = caminho_bd
    #Faremos a verificação do banco de dados, verificando se ele já existe
    #Usamos o parametro self para acessar a variável de classe e poder ser acessada em outras funções
    def verificar_ou_criar_bd(self):
        #Verificamos o caminho do banco de dados, se ele não existir, criamos o banco de dados
        if not os.path.exists(self.caminho_bd):
            #Passamos o caminho do banco de dados para a classe GerenciadorBancoDados que passa instruções para o arquivo criar_db.py que contém a função de criar o banco de dados
            gerenciador_bd = GerenciadorBancoDados(self.caminho_bd)
            #Após receber o parametro do arquivo criar_db.py, a função criar_conexao é para criar uma conexão com o banco de dados
            gerenciador_bd.criar_conexao()
            #Verficamos se o arquivo está vazio ou não usando a definição None, se estiver vazio, criamos as tabelas.
            if gerenciador_bd.conn is not None:
                #Aqui criamos as tabelas no banco de dados e salvamos já que usamos a função com with
                gerenciador_bd.criar_tabelas()
                #Fechamos a conexão com o banco de dados
                gerenciador_bd.fechar_conexao()
                #Imprimimos uma mensagem de sucesso
                print(f"Banco de dados criado em: {self.caminho_bd}")
            #Se não for possível criar a conexão com o banco de dados, imprimimos uma mensagem de erro
            else:
                print("Erro! Não foi possível criar a conexão com o banco de dados.")
        #Se o banco de dados já existir, imprimimos uma mensagem informando que o banco de dados já existe
        else:
            print(f"Banco de dados já existe em: {self.caminho_bd}")
#Fim da classe VerificadorBancoDados

#Aqui verificamos se o script foi executado pelo arquivo gerado pelo PyInstaller ou se foi executado diretamente pelo arquivo principal.py
#Se o script foi executado pelo arquivo gerado pelo PyInstaller, usamos o caminho do executável, para que seja possivel acessar os arquivos necessários como a pasta de apoio
#Se o script foi executado diretamente pelo arquivo principal.py, usamos o caminho do arquivo principal.py que seria a raiz do projeto
#Usamos a função getattr para verificar se o script foi empacotado pelo PyInstaller, passamos o sys como parametro e o atributo 'frozen' que é um atributo que é definido quando o script é empacotado pelo PyInstaller
if getattr(sys, 'frozen', False):
    #Se o script foi empacotado pelo PyInstaller, usamos o caminho do executável
    script_dir = os.path.dirname(sys.executable)
    #Caso contrário, usamos o caminho do arquivo principal.py
else:
    # Se o script estiver sendo executado normalmente, use o caminho do script
    script_dir = os.path.dirname(os.path.abspath(__file__))

#Reforçamos o caminho do banco de dados, juntando o caminho do script com o nome do banco de dados
database = os.path.join(script_dir, "banco.db")
verificador_bd = VerificadorBancoDados(database)
verificador_bd.verificar_ou_criar_bd()

#Aqui criamos a aplicação gráfica.
#A aplicação é criada usando a classe QWidget que é a classe base para todos os widgets
class JanelaLogin(QWidget):
    # Inicializamos a classe com a função __init__ e permitimos que a classe herde as propriedades da classe QWidget
    def __init__(self):
        # Usamos a função super() para acessar a classe pai (QWidgets) e inicializamos a classe pai
        super().__init__()
        # Aqui precisamos já inicializar a instância da classe Modo para que possamos usar a função de trocar o modo de cores das janelas
        # Como a classe Modo é usada em todas as janelas, precisamos inicializar ela aqui para que possamos usar a função de trocar o modo de cores em todas as janelas
        self.modo = Modo()
        # Aqui precisamos buscar todas as configurações do programa no banco de dados
        self.carregar_configuracoes()
        # Usamos a função inicializarUI para inicializar todos os componentes da interface gráfica
        self.inicializarUI()

    def carregar_configuracoes(self):
        try:
            # Conectamos dentro do banco de dados com o alias dessa conexão sendo o nome conexao
            with sqlite3.connect('banco.db') as conexao:
                # Usamos o alias anterior da conexão para criar um cursor para executar comandos SQL
                cursor = conexao.cursor()
                # Aqui selecionamos os parâmetros que existem na tabela config_programa e também reforçamos a seleção do primeiro registro
                cursor.execute('SELECT logo_principal, logo_rodape, fonte_principal, tamanho_fonte, modo_global FROM config_programa WHERE id = 1')
                # Guardamos o resultado da seleção em uma variável chamada configuração
                configuracao = cursor.fetchone()
        # Se ocorrer algum erro ao buscar as configurações do banco de dados, imprimimos uma mensagem de erro
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar configuração do banco de dados: {e}")
            # Retornamos para que a função não continue a ser executada
            return
        # Aqui verificamos se a estrutura de configuração foi encontrada no banco de dados, nesse caso a estrutura é a logo principal, logo do rodapé, fonte principal e tamanho da fonte
        if configuracao:
            self.logo_principal, self.logo_rodape, self.fonte_principal, self.tamanho_fonte, self.modo_global = configuracao
            # Definir o modo inicial com base na configuração do banco de dados
            self.modo.modo_atual = 'escuro' if self.modo_global == 1 else 'claro'
        # Se a estrutura de configuração não for encontrada no banco de dados, imprimimos uma mensagem de erro
        else:
            self.mostrar_erro("Configuração não encontrada no banco de dados.")
            # Retornamos para que a função não continue a ser executada
            return

    # Vamos declarar a função inicializarUI que será responsável por inicializar todos os componentes da interface gráfica e definir o layout da janela
    def inicializarUI(self):
        # Definimos o título da janela
        self.setWindowTitle('Login')
        # Definimos a geometria da janela em pixels (x, y, largura, altura)
        self.setGeometry(100, 100, 800, 600)
        # Forçamos a janela a ser maximizada quando aberta
        self.setWindowState(Qt.WindowMaximized)

        # Aqui definimos o layout da janela como um QVBoxLayout que organiza os widgets verticalmente.
        # Isso permite organizar os widgets na janela de cima para baixo.
        self.layout = QVBoxLayout()

        # Adicionar logo principal
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

        # Definir fonte
        if self.fonte_principal and self.tamanho_fonte:
            self.setFont(QFont(self.fonte_principal, self.tamanho_fonte))

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
        self.botao_login.setStyleSheet("margin-left: auto; margin-right: auto;")  # Centraliza o botão
        self.botao_login.clicked.connect(self.verificar_login)
        self.layout.addWidget(self.botao_login, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)
        self.adicionar_botao_modo()

        self.input_senha.returnPressed.connect(self.verificar_login)

        # Adicionar logo do rodapé
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
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT senha FROM usuarios WHERE usuario = ?', (usuario,))
                resultado = cursor.fetchone()
        except Exception as e:
            self.mostrar_erro(f"Erro ao verificar login: {e}")
            return

        if resultado:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if senha_hash == resultado[0]:
                self.registrar_login(usuario)
                self.abrir_janela_principal()
            else:
                QMessageBox.warning(self, 'Erro', 'Senha incorreta.')
        else:
            QMessageBox.warning(self, 'Erro', 'Usuário não encontrado.')

    def registrar_login(self, usuario):
        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                data_hora_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                cursor.execute('UPDATE usuarios SET ultimo_login = ? WHERE usuario = ?', (data_hora_atual, usuario))
                conexao.commit()
        except Exception as e:
            self.mostrar_erro(f"Erro ao registrar login: {e}")

    def abrir_janela_principal(self):
        usuario_logado = self.obter_usuario_logado()
        if usuario_logado:
            self.janela_principal = JanelaPrincipal(usuario_logado, self.modo)
            self.janela_principal.show()
            self.hide()  # Hide the login window after successful login
        else:
            self.mostrar_erro('Erro ao obter informações do usuário logado.')

    def obter_usuario_logado(self):
        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT id, usuario, is_admin FROM usuarios WHERE usuario = ?', (self.input_usuario.text(),))
                resultado = cursor.fetchone()
                if resultado:
                    return {'id': resultado[0], 'usuario': resultado[1], 'is_admin': resultado[2]}
        except Exception as e:
            self.mostrar_erro(f"Erro ao obter usuário logado: {e}")
        return None

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()

    def adicionar_botao_modo(self):
        # Adicionar switch de modo claro/escuro com ícones
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
            font-family: {self.fonte_principal};
            font-size: {self.tamanho_fonte}px;
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
        # Manter a fonte e o tamanho da fonte
        if self.fonte_principal and self.tamanho_fonte:
            self.setFont(QFont(self.fonte_principal, self.tamanho_fonte))

    def salvar_modo_global(self):
        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                modo_global = 1 if self.modo.modo_atual == 'escuro' else 0
                cursor.execute('UPDATE config_programa SET modo_global = ? WHERE id = 1', (modo_global,))
                conexao.commit()
        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar modo global: {e}")
# Fim da classe JanelaLogin

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
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT * FROM scanner WHERE data LIKE ?', (f'%{data_selecionada}%',))
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
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar informações: {e}")

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

# Define the JanelaConfigPrograma class
class JanelaConfigPrograma(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.config_db = ConfiguracaoProgramaDB('banco.db', QApplication.instance())
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

        self.combo_fonte_principal = QComboBox(self)
        self.combo_fonte_principal.setEditable(True)
        self.combo_fonte_principal.lineEdit().setReadOnly(True)
        self.combo_fonte_principal.lineEdit().setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel('Fonte Principal:'))
        layout.addWidget(self.combo_fonte_principal)

        self.combo_tamanho_fonte = QComboBox(self)
        self.combo_tamanho_fonte.setEditable(True)
        self.combo_tamanho_fonte.lineEdit().setReadOnly(True)
        self.combo_tamanho_fonte.lineEdit().setAlignment(Qt.AlignCenter)
        layout.addWidget(QLabel('Tamanho da Fonte:'))
        layout.addWidget(self.combo_tamanho_fonte)

        botao_salvar = QPushButton('Salvar', self)
        botao_salvar.clicked.connect(self.salvar_configuracoes)
        layout.addWidget(botao_salvar)

        botao_cancelar = QPushButton('Cancelar', self)
        botao_cancelar.clicked.connect(self.voltar_janela_anterior)
        layout.addWidget(botao_cancelar)

        self.setLayout(layout)
        self.carregar_fontes()
        self.carregar_tamanhos_fonte()
        self.carregar_configuracoes()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def selecionar_logo_principal(self):
        caminho_logo = self.config_db.selecionar_imagem()
        if caminho_logo:
            self.input_logo_principal.setText(caminho_logo)

    def selecionar_logo_rodape(self):
        caminho_logo = self.config_db.selecionar_imagem()
        if caminho_logo:
            self.input_logo_rodape.setText(caminho_logo)

    def carregar_fontes(self):
        fontes = QFontDatabase().families()
        for fonte in fontes:
            self.combo_fonte_principal.addItem(fonte)
            index = self.combo_fonte_principal.findText(fonte)
            self.combo_fonte_principal.setItemData(index, QFont(fonte), Qt.FontRole)
        self.combo_fonte_principal.currentIndexChanged.connect(self.atualizar_preview_fonte)
        self.combo_fonte_principal.view().setMouseTracking(True)
        self.combo_fonte_principal.view().entered.connect(self.expandir_lista_fontes)
        self.combo_fonte_principal.lineEdit().installEventFilter(self)

    def carregar_tamanhos_fonte(self):
        for tamanho in range(1, 101):
            self.combo_tamanho_fonte.addItem(str(tamanho))
        self.combo_tamanho_fonte.currentIndexChanged.connect(self.atualizar_preview_tamanho_fonte)
        self.combo_tamanho_fonte.view().setMouseTracking(True)
        self.combo_tamanho_fonte.view().entered.connect(self.expandir_lista_tamanhos)
        self.combo_tamanho_fonte.lineEdit().installEventFilter(self)

    def carregar_configuracoes(self):
        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT logo_principal, logo_rodape, fonte_principal, tamanho_fonte FROM config_programa WHERE id = 1')
                configuracao = cursor.fetchone()
                if configuracao:
                    self.input_logo_principal.setText(configuracao[0])
                    self.input_logo_rodape.setText(configuracao[1])
                    self.combo_fonte_principal.setCurrentText(configuracao[2])
                    self.combo_tamanho_fonte.setCurrentText(str(configuracao[3]))
        except Exception as e:
            self.mostrar_erro(f"Erro ao carregar configurações: {e}")

    def atualizar_preview_fonte(self):
        fonte = self.combo_fonte_principal.currentText()
        self.combo_fonte_principal.lineEdit().setFont(QFont(fonte))

    def atualizar_preview_tamanho_fonte(self):
        tamanho = self.combo_tamanho_fonte.currentText()
        self.combo_tamanho_fonte.lineEdit().setFont(QFont(self.combo_fonte_principal.currentText(), int(tamanho)))

    def expandir_lista_fontes(self, index):
        self.combo_fonte_principal.showPopup()

    def expandir_lista_tamanhos(self, index):
        self.combo_tamanho_fonte.showPopup()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            if source == self.combo_fonte_principal.lineEdit():
                self.combo_fonte_principal.showPopup()
            elif source == self.combo_tamanho_fonte.lineEdit():
                self.combo_tamanho_fonte.showPopup()
        return super().eventFilter(source, event)

    def salvar_configuracoes(self):
        logo_principal = self.input_logo_principal.text()
        logo_rodape = self.input_logo_rodape.text()
        fonte_principal = self.combo_fonte_principal.currentText()
        tamanho_fonte = self.combo_tamanho_fonte.currentText()

        try:
            self.config_db.atualizar_configuracao(
                id_config=1,
                logo_principal=logo_principal,
                logo_rodape=logo_rodape,
                fonte_principal=fonte_principal,
                tamanho_fonte=tamanho_fonte
            )
            QMessageBox.information(self, 'Sucesso', 'Configurações atualizadas com sucesso.')
            self.voltar_janela_anterior()
        except Exception as e:
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
#Final da classe JanelaConfigPrograma

class JanelaDashboard(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Dashboard')
        self.setGeometry(100, 100, 800, 600)
        self.center()

        layout = QVBoxLayout()

        self.tabela_dados = QTableWidget(self)
        self.tabela_dados.setColumnCount(2)
        self.tabela_dados.setHorizontalHeaderLabels(['Sensor', 'Valor'])
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

        self.setLayout(layout)
        self.atualizar_dados()

        # Configurar o temporizador para atualizar os dados a cada 10 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_dados)
        self.timer.start(10000)  # 10000 milissegundos = 10 segundos

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def atualizar_dados(self):
        monitor = MonitorDeHardware()
        data = monitor.obter_info_hardware()

        extractor = ExtratorDeInfoHardware()
        extracted_info = extractor.obter_info(data)
        specific_sensors = extractor.encontrar_sensores_especificos(extracted_info)

        self.tabela_dados.setRowCount(len(specific_sensors))
        for row, (sensor, value) in enumerate(specific_sensors.items()):
            self.tabela_dados.setItem(row, 0, QTableWidgetItem(sensor))
            self.tabela_dados.setItem(row, 1, QTableWidgetItem(str(value) if value else 'N/A'))

    def abrir_janela_configuracao(self):
        self.janela_configuracao = JanelaConfiguracao(self.usuario_logado, self.modo)
        self.janela_configuracao.show()

    def voltar_menu_principal(self):
        self.janela_principal = JanelaPrincipal(self.usuario_logado, self.modo)
        self.janela_principal.show()
        self.close()

    def closeEvent(self, event):
        self.voltar_menu_principal()
        event.accept()

class JanelaConfiguracao(QWidget):
    def __init__(self, usuario_logado, modo):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.modo = modo
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Configuração de Dados Externos')
        self.setGeometry(100, 100, 600, 400)
        self.center()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Configurar dados vindos de outras máquinas:', self)
        layout.addWidget(self.label_instrucoes, alignment=Qt.AlignTop)

        self.input_ip_maquina = QLineEdit(self)
        layout.addWidget(QLabel('IP da Máquina:'))
        layout.addWidget(self.input_ip_maquina)

        self.input_porta = QLineEdit(self)
        layout.addWidget(QLabel('Porta:'))
        layout.addWidget(self.input_porta)

        self.botao_salvar = QPushButton('Salvar', self)
        self.botao_salvar.clicked.connect(self.salvar_configuracao)
        layout.addWidget(self.botao_salvar)

        self.botao_cancelar = QPushButton('Cancelar', self)
        self.botao_cancelar.clicked.connect(self.close)
        layout.addWidget(self.botao_cancelar)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def salvar_configuracao(self):
        ip_maquina = self.input_ip_maquina.text()
        porta = self.input_porta.text()

        if not ip_maquina or not porta:
            QMessageBox.warning(self, 'Erro', 'Por favor, preencha todos os campos.')
            return

        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('INSERT INTO configuracoes_externas (ip_maquina, porta) VALUES (?, ?)', (ip_maquina, porta))
                conexao.commit()
            QMessageBox.information(self, 'Sucesso', 'Configuração salva com sucesso.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Erro ao salvar configuração: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        janela = JanelaLogin()
        janela.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, 'Erro Fatal', f"Ocorreu um erro fatal: {e}")
        sys.exit(1)
