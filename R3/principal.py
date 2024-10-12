from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QCalendarWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDate
from datetime import datetime
from tqdm import tqdm
from PIL import Image, ImageTk, ImageQt
import hashlib
import os
import sqlite3
import scanner_rede
import scanner_rede as scanner_file
import tkinter as tk
from tkinter import messagebox
from PyQt5.QtWidgets import QCalendarWidget

# Define global variables for entry fields
entry_usuario = None
entry_senha = None

def verificar_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()

    try:
        caminho_banco_dados = os.path.join(os.path.dirname(__file__), 'banco.db')
        conn = sqlite3.connect(caminho_banco_dados)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha_criptografada))
        resultado = cursor.fetchone()

        if resultado:
            data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE usuarios SET ultimo_login = ? WHERE usuario = ?", (data_hora_atual, usuario))
            conn.commit()
            is_admin = resultado[6]

            global usuario_logado, is_admin_logado, usuario_admin, usuario_comum
            usuario_logado = usuario
            is_admin_logado = is_admin

            if is_admin:
                usuario_admin = usuario
                usuario_comum = None
            else:
                usuario_comum = usuario
                usuario_admin = None

            globals().update({
                'usuario_logado': usuario_logado,
                'is_admin_logado': is_admin_logado,
                'usuario_admin': usuario_admin,
                'usuario_comum': usuario_comum
            })
            print("Login correto")
            janela_principal()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
#Fim da função verificar_login

def janela_principal():
    global janela_login
    janela_login.close()
    
    app = QtWidgets.QApplication([])
    janela_principal = QtWidgets.QMainWindow()
    janela_principal.setWindowTitle("Menu Principal")
    janela_principal.setGeometry(100, 100, 400, 400)

    central_widget = QtWidgets.QWidget()
    janela_principal.setCentralWidget(central_widget)
    layout = QtWidgets.QVBoxLayout(central_widget)

    label_usuario_logado = QtWidgets.QLabel(f"Usuário: {usuario_logado} ({'Admin' if is_admin_logado else 'Comum'})")
    layout.addWidget(label_usuario_logado)

    def abrir_janela_escanear():
        janela_escanear = QtWidgets.QWidget()
        janela_escanear.setWindowTitle("Scanner de Rede")
        janela_escanear.setGeometry(100, 100, 300, 200)
        layout_escanear = QtWidgets.QVBoxLayout(janela_escanear)

        btn_escanear_propria_rede = QtWidgets.QPushButton("Escanear sua rede")
        btn_escanear_propria_rede.clicked.connect(scanner_file.scanner)
        layout_escanear.addWidget(btn_escanear_propria_rede)

        btn_visualizar = QtWidgets.QPushButton("Visualizar Informações Armazenadas")
        btn_visualizar.clicked.connect(visualizar_informacoes)
        layout_escanear.addWidget(btn_visualizar)

        btn_voltar = QtWidgets.QPushButton("Voltar ao Menu Principal")
        btn_voltar.clicked.connect(janela_escanear.close)
        layout_escanear.addWidget(btn_voltar)

        janela_escanear.show()

    def visualizar_informacoes():
        def buscar_informacoes(data_selecionada):
            try:
                data_selecionada = datetime.strptime(data_selecionada, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                QtWidgets.QMessageBox.critical(None, "Erro", "Formato de data inválido. Use DIA/MÊS/ANO.")
                return

            janela_informacoes = QtWidgets.QWidget()
            janela_informacoes.setWindowTitle("Informações Armazenadas")
            janela_informacoes.setGeometry(100, 100, 1200, 600)
            layout_informacoes = QtWidgets.QVBoxLayout(janela_informacoes)

            text_informacoes = QtWidgets.QTextEdit()
            text_informacoes.setReadOnly(True)
            layout_informacoes.addWidget(text_informacoes)

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT data, hostname, mac_address, ip, portas FROM scanner WHERE data LIKE ?', (f"{data_selecionada}%",))
                registros = cursor.fetchall()

                informacoes_texto = "\n".join([
                    f"Data: {r[0]} | Hostname: {r[1]} | MAC: {r[2]} | IP: {r[3]} | Portas: {r[4]}"
                    for r in registros
                ]) if registros else "Nenhuma informação encontrada para a data selecionada."

                text_informacoes.setPlainText(informacoes_texto)

            janela_informacoes.show()

        janela_selecao_data = QtWidgets.QWidget()
        janela_selecao_data.setWindowTitle("Selecione a Data")
        janela_selecao_data.setGeometry(100, 100, 300, 400)
        layout_selecao_data = QtWidgets.QVBoxLayout(janela_selecao_data)

        label_data = QtWidgets.QLabel("Selecione a Data:")
        layout_selecao_data.addWidget(label_data)

        db_path = os.path.join(os.path.dirname(__file__), 'banco.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT data FROM scanner')
            datas = [row[0] for row in cursor.fetchall()]

        var_data = QtCore.QDate.currentDate().toString("dd/MM/yyyy")
        entry_data = QtWidgets.QLineEdit(var_data)
        layout_selecao_data.addWidget(entry_data)

        label_calendario = QtWidgets.QLabel("Calendário:")
        layout_selecao_data.addWidget(label_calendario)

        cal = QCalendarWidget()
        cal.setGridVisible(True)
        cal.clicked.connect(lambda date: entry_data.setText(date.toString("dd/MM/yyyy")))
        layout_selecao_data.addWidget(cal)

        btn_buscar = QtWidgets.QPushButton("Buscar")
        btn_buscar.clicked.connect(lambda: buscar_informacoes(entry_data.text()))
        layout_selecao_data.addWidget(btn_buscar)
        # Placeholder for dashboard function
        print("Dashboard function called")
        janela_selecao_data.show()

    #def abrir_dashboard():
        #dashboard.abrir_dashboard()

    #btn_dashboard = QtWidgets.QPushButton("DASHBOARD")
    #btn_dashboard.clicked.connect(abrir_dashboard)
    #layout.addWidget(btn_dashboard)

    btn_funcoes_scanner = QtWidgets.QPushButton("FUNÇÕES DE SCANNER DE REDE")
    btn_funcoes_scanner.clicked.connect(abrir_janela_escanear)
    layout.addWidget(btn_funcoes_scanner)

    def abrir_configuracoes_usuarios():
        janela_configuracoes_usuarios = QtWidgets.QWidget()
        janela_configuracoes_usuarios.setWindowTitle("Configurações de Usuários")
        janela_configuracoes_usuarios.setGeometry(100, 100, 400, 300)
        layout_configuracoes_usuarios = QtWidgets.QVBoxLayout(janela_configuracoes_usuarios)

        def adicionar_usuario():
            janela_adicionar_usuario = QtWidgets.QWidget()
            janela_adicionar_usuario.setWindowTitle("Adicionar Usuário")
            janela_adicionar_usuario.setGeometry(100, 100, 400, 400)
            layout_adicionar_usuario = QtWidgets.QVBoxLayout(janela_adicionar_usuario)

            layout_adicionar_usuario.addWidget(QtWidgets.QLabel("Usuário:"))
            entry_novo_usuario = QtWidgets.QLineEdit()
            layout_adicionar_usuario.addWidget(entry_novo_usuario)

            layout_adicionar_usuario.addWidget(QtWidgets.QLabel("Senha:"))
            entry_nova_senha = QtWidgets.QLineEdit()
            entry_nova_senha.setEchoMode(QtWidgets.QLineEdit.Password)
            layout_adicionar_usuario.addWidget(entry_nova_senha)

            layout_adicionar_usuario.addWidget(QtWidgets.QLabel("Nome Completo:"))
            entry_nome_completo = QtWidgets.QLineEdit()
            layout_adicionar_usuario.addWidget(entry_nome_completo)

            layout_adicionar_usuario.addWidget(QtWidgets.QLabel("Email:"))
            entry_email = QtWidgets.QLineEdit()
            layout_adicionar_usuario.addWidget(entry_email)

            label_pergunta_admin = QtWidgets.QLabel("Precisa ser administrador ?")
            layout_adicionar_usuario.addWidget(label_pergunta_admin)

            is_admin_var = QtWidgets.QCheckBox("Administrador")
            layout_adicionar_usuario.addWidget(is_admin_var)

            def salvar_usuario():
                usuario = entry_novo_usuario.text()
                senha = entry_nova_senha.text()
                nome_completo = entry_nome_completo.text()
                email = entry_email.text()
                is_admin = is_admin_var.isChecked()

                if not all([usuario, senha, nome_completo, email]):
                    QtWidgets.QMessageBox.critical(None, "Erro", "Todos os campos devem ser preenchidos.")
                    return

                senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()
                data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    with sqlite3.connect(caminho_banco_dados) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO usuarios (usuario, senha, data_criacao, nome_completo, email, is_admin)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (usuario, senha_criptografada, data_criacao, nome_completo, email, int(is_admin)))
                        conn.commit()
                        QtWidgets.QMessageBox.information(None, "Sucesso", "Usuário adicionado com sucesso.")
                        janela_adicionar_usuario.close()
                except sqlite3.Error as e:
                    QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao adicionar usuário: {e}")

            btn_salvar_usuario = QtWidgets.QPushButton("Salvar Usuário")
            btn_salvar_usuario.clicked.connect(salvar_usuario)
            layout_adicionar_usuario.addWidget(btn_salvar_usuario)

            janela_adicionar_usuario.show()

        btn_adicionar_usuarios = QtWidgets.QPushButton("Adicionar Usuários")
        btn_adicionar_usuarios.clicked.connect(adicionar_usuario)
        layout_configuracoes_usuarios.addWidget(btn_adicionar_usuarios)

        def editar_usuarios():
            janela_editar_usuarios = QtWidgets.QWidget()
            janela_editar_usuarios.setWindowTitle("Editar Usuários Existentes")
            janela_editar_usuarios.setGeometry(100, 100, 600, 400)
            layout_editar_usuarios = QtWidgets.QVBoxLayout(janela_editar_usuarios)

            listbox_usuarios = QtWidgets.QListWidget()
            layout_editar_usuarios.addWidget(listbox_usuarios)

            def carregar_usuarios():
                try:
                    with sqlite3.connect(caminho_banco_dados) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT id, usuario, nome_completo, email, is_admin, ultimo_login FROM usuarios")
                        usuarios = cursor.fetchall()
                        listbox_usuarios.clear()
                        for usuario in usuarios:
                            usuario_info = f"{usuario[0]} | {usuario[1]} | {usuario[2]} | {usuario[3]} | {'Admin' if usuario[4] else 'Comum'} | Último login: {usuario[5]}"
                            listbox_usuarios.addItem(usuario_info)
                except sqlite3.Error as e:
                    QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao carregar usuários: {e}")

            def buscar_informacoes_usuario():
                if not listbox_usuarios.currentItem():
                    QtWidgets.QMessageBox.critical(None, "Erro", "Nenhum usuário selecionado.")
                    return
                usuario_selecionado = listbox_usuarios.currentItem().text().split(" | ")[1]
                try:
                    with sqlite3.connect(caminho_banco_dados) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT usuario, nome_completo, email, is_admin FROM usuarios WHERE usuario = ?", (usuario_selecionado,))
                        usuario_info = cursor.fetchone()
                        if usuario_info:
                            entry_usuario_editar.setText(usuario_info[0])
                            entry_nome_completo_editar.setText(usuario_info[1])
                            entry_email_editar.setText(usuario_info[2])
                            is_admin_var_editar.setChecked(usuario_info[3])
                        else:
                            QtWidgets.QMessageBox.critical(None, "Erro", "Usuário não encontrado.")
                except sqlite3.Error as e:
                    QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao buscar informações do usuário: {e}")

            listbox_usuarios.itemSelectionChanged.connect(buscar_informacoes_usuario)

            layout_editar_usuarios.addWidget(QtWidgets.QLabel("Usuário:"))
            entry_usuario_editar = QtWidgets.QLineEdit()
            layout_editar_usuarios.addWidget(entry_usuario_editar)

            layout_editar_usuarios.addWidget(QtWidgets.QLabel("Nome Completo:"))
            entry_nome_completo_editar = QtWidgets.QLineEdit()
            layout_editar_usuarios.addWidget(entry_nome_completo_editar)

            layout_editar_usuarios.addWidget(QtWidgets.QLabel("Email:"))
            entry_email_editar = QtWidgets.QLineEdit()
            layout_editar_usuarios.addWidget(entry_email_editar)

            is_admin_var_editar = QtWidgets.QCheckBox("Administrador")
            layout_editar_usuarios.addWidget(is_admin_var_editar)

            def salvar_alteracoes():
                usuario = entry_usuario_editar.text()
                nome_completo = entry_nome_completo_editar.text()
                email = entry_email_editar.text()
                is_admin = is_admin_var_editar.isChecked()

                if not all([usuario, nome_completo, email]):
                    QtWidgets.QMessageBox.critical(None, "Erro", "Todos os campos devem ser preenchidos.")
                    return

                with sqlite3.connect(caminho_banco_dados) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome_completo, email, is_admin FROM usuarios WHERE usuario = ?", (usuario,))
                    usuario_atual = cursor.fetchone()
                    if usuario_atual:
                        nome_completo_atual, email_atual, is_admin_atual = usuario_atual
                            
                        if nome_completo != nome_completo_atual or email != email_atual or int(is_admin) != is_admin_atual:
                            try:
                                cursor.execute("""
                                    UPDATE usuarios
                                    SET nome_completo = ?, email = ?, is_admin = ?
                                    WHERE usuario = ?
                                """, (nome_completo, email, int(is_admin), usuario))
                                conn.commit()
                                QtWidgets.QMessageBox.information(None, "Sucesso", "Informações do usuário atualizadas com sucesso.")
                                carregar_usuarios()
                            except sqlite3.Error as e:
                                QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao atualizar informações do usuário: {e}")
                        else:
                            QtWidgets.QMessageBox.information(None, "Informação", "Nenhuma alteração detectada.")
                    else:
                        QtWidgets.QMessageBox.critical(None, "Erro", "Usuário não encontrado.")

            btn_salvar_alteracoes = QtWidgets.QPushButton("Salvar Alterações")
            btn_salvar_alteracoes.clicked.connect(salvar_alteracoes)
            layout_editar_usuarios.addWidget(btn_salvar_alteracoes)

            carregar_usuarios()

            if not is_admin_logado:
                entry_usuario_editar.setDisabled(True)
                entry_nome_completo_editar.setDisabled(True)
                entry_email_editar.setDisabled(True)
                is_admin_var_editar.setDisabled(True)
                btn_salvar_alteracoes.setDisabled(True)

            janela_editar_usuarios.show()

        btn_editar_usuarios = QtWidgets.QPushButton("Editar Usuários Existentes")
        btn_editar_usuarios.clicked.connect(editar_usuarios)
        layout_configuracoes_usuarios.addWidget(btn_editar_usuarios)

        btn_visualizar_alteracoes = QtWidgets.QPushButton("Visualizar Alterações")
        layout_configuracoes_usuarios.addWidget(btn_visualizar_alteracoes)

        btn_voltar_menu_principal = QtWidgets.QPushButton("Voltar ao Menu Principal")
        btn_voltar_menu_principal.clicked.connect(janela_configuracoes_usuarios.close)
        layout_configuracoes_usuarios.addWidget(btn_voltar_menu_principal)

        janela_configuracoes_usuarios.show()

    btn_configuracoes_usuarios = QtWidgets.QPushButton("CONFIGURAÇÕES DE USUÁRIOS")
    btn_configuracoes_usuarios.clicked.connect(abrir_configuracoes_usuarios)
    layout.addWidget(btn_configuracoes_usuarios)

    btn_configuracoes = QtWidgets.QPushButton("CONFIGURAÇÕES DO PROGRAMA")
    layout.addWidget(btn_configuracoes)

    btn_sair = QtWidgets.QPushButton("SAIR")
    btn_sair.clicked.connect(janela_principal.close)
    layout.addWidget(btn_sair)

    janela_principal.show()
    app.exec_()
    #Fim da função janela_principal

#Inicio da função para carregar a janela de login
# Configuração da janela de login
app = QtWidgets.QApplication([])
janela_login = QtWidgets.QWidget()
janela_login.setWindowTitle("Login")
janela_login.setGeometry(100, 100, 800, 800)

# Função que verifica se o arquivo de imagem foi carregado corretamente, caso não exibe uma mensagem de erro
def carregar_gif(caminho):
    try:
        return Image.open(caminho)
    except FileNotFoundError:
        QtWidgets.QMessageBox.critical(None, "Erro", f"Arquivo não encontrado: {caminho}")
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao carregar a imagem: {e}")
    return None

# Parte do Header da janela de login
caminho_banco_dados = os.path.join(os.path.dirname(__file__), 'banco.db')
try:
    with sqlite3.connect(caminho_banco_dados) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT logo_principal FROM config_programa")
        caminho_logo = cursor.fetchone()[0]
except sqlite3.Error as e:
    QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao conectar ao banco de dados: {e}")

imagem_logo = carregar_gif(caminho_logo)
label_logo = QtWidgets.QLabel()
label_logo.setPixmap(QtGui.QPixmap.fromImage(ImageQt(imagem_logo)))
label_logo.setAlignment(QtCore.Qt.AlignCenter)

layout = QtWidgets.QVBoxLayout(janela_login)
layout.addWidget(label_logo)

def redimensionar_imagem(imagem, largura, altura):
    return imagem.resize((largura, altura), Image.ANTIALIAS)

def animar_gif():
    try:
        imagem_logo.seek(imagem_logo.tell() + 1)
        imagem_redimensionada = ImageQt(redimensionar_imagem(imagem_logo, 600, 300))
        label_logo.setPixmap(QtGui.QPixmap.fromImage(imagem_redimensionada))
        QtCore.QTimer.singleShot(100, animar_gif)
    except EOFError:
        pass

animar_gif()

# Fetch font settings from the database
try:
    with sqlite3.connect(caminho_banco_dados) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fonte_principal, tamanho_fonte FROM config_programa")
        fonte_principal, tamanho_fonte = cursor.fetchone()
except sqlite3.Error as e:
    QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao conectar ao banco de dados: {e}")

fonte_padrao = QtGui.QFont(fonte_principal, tamanho_fonte)
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

def pressionar_enter():
    verificar_login()

entry_senha.returnPressed.connect(pressionar_enter)

btn_login = QtWidgets.QPushButton("Login")
btn_login.setFont(fonte_padrao)
btn_login.clicked.connect(verificar_login)
layout.addWidget(btn_login)

try:
    with sqlite3.connect(caminho_banco_dados) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT logo_rodape FROM config_programa")
        caminho_logo_rodape = cursor.fetchone()[0]
except sqlite3.Error as e:
    QtWidgets.QMessageBox.critical(None, "Erro", f"Erro ao conectar ao banco de dados: {e}")

imagem_logo_rodape = carregar_gif(caminho_logo_rodape)
label_logo_rodape = QtWidgets.QLabel()
label_logo_rodape.setPixmap(QtGui.QPixmap.fromImage(ImageQt(imagem_logo_rodape)))
label_logo_rodape.setAlignment(QtCore.Qt.AlignCenter)
layout.addWidget(label_logo_rodape)

def animar_gif_rodape():
    try:
        imagem_logo_rodape.seek(imagem_logo_rodape.tell() + 1)
        frame = ImageQt(redimensionar_imagem(imagem_logo_rodape, 600, 300))
        label_logo_rodape.setPixmap(QtGui.QPixmap.fromImage(frame))
        QtCore.QTimer.singleShot(100, animar_gif_rodape)
    except EOFError:
        pass

animar_gif_rodape()

janela_login.show()
app.exec_()