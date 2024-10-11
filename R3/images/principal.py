from PyQt5 import QtCore, QtWidgets, QtGui
import hashlib
import os
import sqlite3
from datetime import datetime
from PIL import Image

# Função para verificar se o login está correto
def verificar_login():
    usuario = entry_usuario.text()
    senha = entry_senha.text()
    
    senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()
    
    try:
        caminho_banco_dados = os.path.join(os.path.dirname(__file__), 'banco.db')
        conn = sqlite3.connect(caminho_banco_dados)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha_criptografada))
        resultado = cursor.fetchone()
        
        if resultado:
            janela_principal()
        else:
            QtWidgets.QMessageBox.warning(None, "Erro", "Usuário ou senha incorretos")
        
        conn.close()
    except sqlite3.Error as e:
        QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao conectar ao banco de dados: {e}")

# Função para abrir a janela principal após o login correto
def janela_principal():
    janela_login.close()
    
    janela_principal = QtWidgets.QMainWindow()
    janela_principal.setWindowTitle("Menu Principal")
    janela_principal.setGeometry(100, 100, 400, 400)
    
    central_widget = QtWidgets.QWidget()
    janela_principal.setCentralWidget(central_widget)
    
    layout = QtWidgets.QVBoxLayout(central_widget)
    
    label_usuario_logado = QtWidgets.QLabel(f"Usuário: {usuario_logado} ({'Admin' if is_admin_logado else 'Comum'})")
    layout.addWidget(label_usuario_logado)
    
    btn_dashboard = QtWidgets.QPushButton("DASHBOARD")
    btn_dashboard.clicked.connect(abrir_dashboard)
    layout.addWidget(btn_dashboard)
    
    btn_funcoes_scanner = QtWidgets.QPushButton("FUNÇÕES DE SCANNER DE REDE")
    btn_funcoes_scanner.clicked.connect(abrir_janela_escanear)
    layout.addWidget(btn_funcoes_scanner)
    
    btn_configuracoes_usuarios = QtWidgets.QPushButton("CONFIGURAÇÕES DE USUÁRIOS")
    btn_configuracoes_usuarios.clicked.connect(abrir_configuracoes_usuarios)
    layout.addWidget(btn_configuracoes_usuarios)
    
    btn_configuracoes = QtWidgets.QPushButton("CONFIGURAÇÕES DO PROGRAMA")
    layout.addWidget(btn_configuracoes)
    
    btn_sair = QtWidgets.QPushButton("SAIR")
    btn_sair.clicked.connect(janela_principal.close)
    layout.addWidget(btn_sair)
    
    janela_principal.show()

# Função para carregar GIF
def carregar_gif(caminho):
    try:
        return Image.open(caminho)
    except FileNotFoundError:
        QtWidgets.QMessageBox.critical(None, "Erro", "Arquivo de imagem não encontrado")
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao carregar a imagem: {e}")
    return None

# Função para redimensionar a imagem
def redimensionar_imagem(imagem, largura, altura):
    return imagem.resize((largura, altura), Image.LANCZOS)

# Função para animar o GIF
def animar_gif(label, imagem, ind):
    try:
        label.setPixmap(QtGui.QPixmap(imagem))
    except EOFError:
        pass

# Configuração da janela de login
app = QtWidgets.QApplication([])

janela_login = QtWidgets.QWidget()
janela_login.setWindowTitle("Login")
janela_login.setGeometry(100, 100, 800, 800)

layout = QtWidgets.QVBoxLayout(janela_login)

caminho_banco_dados = os.path.join(os.path.dirname(__file__), 'banco.db')
try:
    with sqlite3.connect(caminho_banco_dados) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_logo FROM configuracoes")
        caminho_logo = cursor.fetchone()[0]
except sqlite3.Error as e:
    QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao conectar ao banco de dados: {e}")

imagem_logo = carregar_gif(caminho_logo)
label_logo = QtWidgets.QLabel()
label_logo.setPixmap(QtGui.QPixmap(imagem_logo))
layout.addWidget(label_logo)

fonte_padrao = QtGui.QFont("Terminal", 18)

label_usuario = QtWidgets.QLabel("Usuário:")
label_usuario.setFont(fonte_padrao)
layout.addWidget(label_usuario)

entry_usuario = QtWidgets.QLineEdit()
entry_usuario.setFont(fonte_padrao)
layout.addWidget(entry_usuario)

label_senha = QtWidgets.QLabel("Senha:")
label_senha.setFont(fonte_padrao)
layout.addWidget(label_senha)

entry_senha = QtWidgets.QLineEdit()
entry_senha.setFont(fonte_padrao)
entry_senha.setEchoMode(QtWidgets.QLineEdit.Password)
layout.addWidget(entry_senha)

entry_senha.returnPressed.connect(verificar_login)

btn_login = QtWidgets.QPushButton("Login")
btn_login.setFont(fonte_padrao)
btn_login.clicked.connect(verificar_login)
layout.addWidget(btn_login)

try:
    with sqlite3.connect(caminho_banco_dados) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_logo_rodape FROM configuracoes")
        caminho_logo_rodape = cursor.fetchone()[0]
except sqlite3.Error as e:
    QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao conectar ao banco de dados: {e}")

imagem_logo_rodape = carregar_gif(caminho_logo_rodape)
label_logo_rodape = QtWidgets.QLabel()
label_logo_rodape.setPixmap(QtGui.QPixmap(imagem_logo_rodape))
layout.addWidget(label_logo_rodape)

janela_login.show()
app.exec_()