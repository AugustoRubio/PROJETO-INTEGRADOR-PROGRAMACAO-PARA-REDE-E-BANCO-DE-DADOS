# PROJETO INTEGRADOR - GRUPO 08 - ANALISADOR DE REDE
#SENAC - TURMA 2024
#ALUNOS:
# Augusto Rubio da Câmara
# Erik Freitas Silva
# Hugo Santos de Lima
# Paulo Sérgio Aparecido Monteiro Feliciano

#PARA COMEÇAR!:
#1 - Instale as bibliotecas necessárias para o funcionamento do programa: Nmap (pip install python-nmap), tqdm (pip install tqdm), psutil(pip install psutil)
#2 - Instale o Nmap no caminho padrão (C:\Program Files (x86)\Nmap\nmap.exe)
#3 - Execute o arquivo criar_db.py para criar o banco de dados de login e usuário. Usuário padrão: admin, senha padrão: teste.
#4 - Execute o arquivo visual.py para iniciar o programa.

# Importa as bibliotecas necessárias para o funcionamento do programa

#Biblioteca para interface gráfica
import tkinter as tk
from tkinter import messagebox
#Biblioteca para manipulação de banco de dados
import sqlite3
#Biblioteca para criptografia de senha
import hashlib
#Biblioteca para manipulação de arquivos
import os
#Biblioteca para manipulação de rede
import nmap
#Biblioteca para manipulação de data e hora
from datetime import datetime
import time
#Biblioteca para barra de progresso
from tqdm import tqdm
#Biblioteca para manipulação de rede
import socket
import ipaddress
import psutil
#Biblioteca para manipulação de imagens
import base64
from io import BytesIO

########################################################## FAZ AS VERIFICACOES INICIAIS DO BANCO DE DADOS DO ANALISADOR DE REDE ###########################
# Define a pasta da criação do arquivo a mesma do arquivo .py
pasta = os.path.dirname(__file__)
# Define qual o arquivo que vai usar e dentro da mesma pasta do .py
arquivo = os.path.join(pasta, "arq_rede.db")

# Define o caminho do executável do nmap
nmap_path = r"C:\Program Files (x86)\Nmap\nmap.exe"
if not os.path.exists(nmap_path):
    raise FileNotFoundError(f"Nmap executable not found at {nmap_path}")

# Configura o caminho do nmap para o nmap.PortScanner
nmap.PortScanner().nmap_executable = nmap_path

#Verifica se o arquivo do BANCO DE DADOS existe, se não existir cria o arquivo com os parametros padrão.
def verifica_arquivo(arquivo):
    if not os.path.exists(arquivo):
        cria_banco(arquivo)
    else:
        verifica_base_inicial(arquivo)

def cria_banco(arquivo):
    with sqlite3.connect(arquivo) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS escaneamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                hostname TEXT,
                mac_address TEXT,
                ip TEXT,
                porta_22 TEXT,
                porta_80 TEXT
            )
        ''')
        conn.commit()

#Verifica se o BANCO DE DADOS possui a estrutura inicial correta, se não tiver cria a estrutura.
def verifica_base_inicial(arquivo):
    with sqlite3.connect(arquivo) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='escaneamentos';")
        if not cursor.fetchone():
            cria_banco(arquivo)

########################################################## FIM DAS VERIFICACOES INICIAIS DO BANCO DE DADOS DO ANALISADOR DE REDE ###########################

########################################################## COMEÇA O PROGRAMA VISUAL ##########################################################################

# Função para abrir a janela de sucesso
def abrir_janela_sucesso():
    messagebox.showinfo("Sucesso", "Conexão com o banco de dados efetuada com sucesso!")

# Função para verificar a conexão com o banco de dados
def verificar_conexao():
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios';")
        resultado = cursor.fetchone()
        
        if resultado:
            abrir_janela_sucesso()
        else:
            messagebox.showerror("Erro", "Tabela 'usuarios' não encontrada no banco de dados!")
        
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar com o banco de dados: {e}")
    
# Verificar a conexão com o banco de dados ao iniciar o programa
verificar_conexao()

# Função para verificar o login
def verificar_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    
    # Criptografar a senha usando hashlib.sha256
    senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()
    
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha_criptografada))
        resultado = cursor.fetchone()
        
        if resultado:
            abrir_segunda_janela()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")
        
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar com o banco de dados: {e}")
    
    finally:
        if conn:
            conn.close()

# Função para abrir a segunda janela
def abrir_segunda_janela():
    janela_login.destroy()
    
    janela_principal = tk.Tk()
    janela_principal.title("Menu Principal")
    janela_principal.geometry("800x800")
    
    btn_escanear = tk.Button(janela_principal, text="Escanear a Rede", command=escanear_rede)
    btn_escanear.pack(pady=20)
    
    btn_listar = tk.Button(janela_principal, text="Listar Informações", command=listar_informacoes)
    btn_listar.pack(pady=20)
    
    btn_sair = tk.Button(janela_principal, text="Sair", command=janela_principal.quit)
    btn_sair.pack(pady=20)
    
    janela_principal.mainloop()

# Funções de exemplo para os botões da segunda janela
def escanear_rede():
    messagebox.showinfo("Escanear", "Função de escanear a rede ainda não implementada.")

def listar_informacoes():
    messagebox.showinfo("Listar", "Função de listar informações ainda não implementada.")

# Configuração da janela de login
janela_login = tk.Tk()
janela_login.title("Login")
janela_login.geometry("800x800")

########################################################## IMPLEMENTA LOGO NO TOPO DO PROGRAMA ##########################################################################
# Função para carregar a imagem GIF
def carregar_gif(caminho):
    with open(caminho, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return tk.PhotoImage(data=encoded_string)

# Caminho da imagem GIF
caminho_logo = "apoio\\LOGO_R3.png"

# Carregar a imagem GIF
imagem_logo = carregar_gif(caminho_logo)

# Adicionar a imagem na janela de login
label_logo = tk.Label(janela_login, image=imagem_logo)
label_logo.pack(pady=20)

# Função para animar o GIF
def animar_gif(ind):
    try:
        frame = tk.PhotoImage(file=caminho_logo, format=f"gif -index {ind}")
        label_logo.configure(image=frame)
        label_logo.image = frame
        ind += 1
        janela_login.after(100, animar_gif, ind)
    except tk.TclError:
        ind = 0
        janela_login.after(100, animar_gif, ind)

# Iniciar a animação do GIF
janela_login.after(0, animar_gif, 0)

########################################################## FIM DO TOPO DO PROGRAMA ##########################################################################

# Campos de entrada para usuário e senha
label_usuario = tk.Label(janela_login, text="Usuário:")
label_usuario.pack(pady=5)
entry_usuario = tk.Entry(janela_login)
entry_usuario.pack(pady=5)

label_senha = tk.Label(janela_login, text="Senha:")
label_senha.pack(pady=5)
entry_senha = tk.Entry(janela_login, show="*")
entry_senha.pack(pady=5)

# Botão de login
btn_login = tk.Button(janela_login, text="Login", command=verificar_login)
btn_login.pack(pady=20)

########################################################## IMPLEMENTA LOGO NO RODAPÉ DO PROGRAMA ##########################################################################
# Caminho da imagem GIF do rodapé
caminho_logo_rodape = "apoio\\teste1.gif"

# Carregar a imagem GIF do rodapé
imagem_logo_rodape = carregar_gif(caminho_logo_rodape)

# Adicionar a imagem na janela de login (rodapé)
label_logo_rodape = tk.Label(janela_login, image=imagem_logo_rodape)
label_logo_rodape.pack(side="bottom", pady=10)

# Variável para controlar a velocidade da animação do GIF
velocidade_animacao = 250  # Valor em milissegundos

# Função para redimensionar a imagem
def redimensionar_imagem(imagem, largura, altura):
    return imagem.subsample(imagem.width() // largura, imagem.height() // altura)

# Função para animar o GIF do rodapé
def animar_gif_rodape(ind):
    try:
        frame = tk.PhotoImage(file=caminho_logo_rodape, format=f"gif -index {ind}")
        frame = redimensionar_imagem(frame, 200, 100)
        label_logo_rodape.configure(image=frame)
        label_logo_rodape.image = frame
        ind += 1
        janela_login.after(velocidade_animacao, animar_gif_rodape, ind)
    except tk.TclError:
        ind = 0
        janela_login.after(velocidade_animacao, animar_gif_rodape, ind)

# Iniciar a animação do GIF do rodapé
janela_login.after(0, animar_gif_rodape, 0)

# Adicionar um controle deslizante para ajustar a velocidade da animação
def ajustar_velocidade(val):
    global velocidade_animacao
    velocidade_animacao = int(val)

########################################################## FIM DO RODAPÉ DO PROGRAMA ##########################################################################

janela_login.mainloop()