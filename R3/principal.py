import sys
import sqlite3
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt
import subprocess

class JanelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 800, 600)  # Set the window size
        self.setWindowState(Qt.WindowMaximized)  # Allow the window to be maximized

        # Buscar configuração do banco de dados
        with sqlite3.connect('banco.db') as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT logo_principal, logo_rodape, fonte_principal, tamanho_fonte FROM config_programa WHERE id = 1')
            configuracao = cursor.fetchone()

        logo_principal, logo_rodape, fonte_principal, tamanho_fonte = configuracao

        self.layout = QVBoxLayout()

        # Adicionar logo principal
        if logo_principal:
            self.label_logo_principal = QLabel(self)
            self.label_logo_principal.setAlignment(Qt.AlignCenter)
            if logo_principal.endswith('.gif'):
                self.movie_logo_principal = QMovie(logo_principal)
                self.label_logo_principal.setMovie(self.movie_logo_principal)
                self.movie_logo_principal.start()
            else:
                self.pixmap_logo_principal = QPixmap(logo_principal)
                self.label_logo_principal.setPixmap(self.pixmap_logo_principal.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.layout.addWidget(self.label_logo_principal)

        # Definir fonte
        if fonte_principal and tamanho_fonte:
            self.setFont(QFont(fonte_principal, tamanho_fonte))

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
        self.botao_login.setStyleSheet("margin-left: auto; margin-right: auto;")  # Center the button
        self.botao_login.clicked.connect(self.verificar_login)
        self.layout.addWidget(self.botao_login, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        self.input_senha.returnPressed.connect(self.verificar_login)

        # Adicionar logo do rodapé
        if logo_rodape:
            self.label_logo_rodape = QLabel(self)
            self.label_logo_rodape.setAlignment(Qt.AlignCenter)
            self.pixmap_logo_rodape = QPixmap(logo_rodape)
            self.label_logo_rodape.setPixmap(self.pixmap_logo_rodape.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.layout.addWidget(self.label_logo_rodape)

    def verificar_login(self):
        usuario = self.input_usuario.text()
        senha = self.input_senha.text()

        if not usuario or not senha:
            QMessageBox.warning(self, 'Erro', 'Por favor, preencha todos os campos.')
            return

        with sqlite3.connect('banco.db') as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT senha FROM usuarios WHERE usuario = ?', (usuario,))
            resultado = cursor.fetchone()

        if resultado:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if senha_hash == resultado[0]:
                QMessageBox.information(self, 'Sucesso', 'Login realizado com sucesso!')
                self.abrir_janela_principal()
            else:
                QMessageBox.warning(self, 'Erro', 'Senha incorreta.')
        else:
            QMessageBox.warning(self, 'Erro', 'Usuário não encontrado.')

    def abrir_janela_principal(self):
        self.janela_principal = JanelaPrincipal()
        self.janela_principal.show()
        self.close()

class JanelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Janela Principal')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.botao_dashboard = QPushButton('DASHBOARD', self)
        layout.addWidget(self.botao_dashboard)

        self.botao_scanner_rede = QPushButton('Scanner de rede', self)
        self.botao_scanner_rede.clicked.connect(self.executar_scanner_rede)
        layout.addWidget(self.botao_scanner_rede)

        self.botao_config_usuarios = QPushButton('Configurações de usuários', self)
        layout.addWidget(self.botao_config_usuarios)

        self.botao_config_programa = QPushButton('Configuração do programa', self)
        layout.addWidget(self.botao_config_programa)

        self.botao_sair = QPushButton('SAIR', self)
        self.botao_sair.clicked.connect(self.close)
        layout.addWidget(self.botao_sair)

        self.setLayout(layout)

    def executar_scanner_rede(self):
        subprocess.run(['python', 'scanner_rede.py'])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = JanelaLogin()
    janela.show()
    sys.exit(app.exec_())
