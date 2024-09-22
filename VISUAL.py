# PROJETO INTEGRADOR - GRUPO 08 - ANALISADOR DE REDE
#SENAC - TURMA 2024
#ALUNOS:
# Augusto Rubio da Câmara
# Erik Freitas Silva
# Hugo Santos de Lima
# Paulo Sérgio Aparecido Monteiro Feliciano

#PARA COMEÇAR!:
#1 - Instale as bibliotecas necessárias para o funcionamento do programa: Nmap (pip install python-nmap), tqdm (pip install tqdm), psutil(pip install psutil), pillow(pip install pillow), tkinter (pip install tk), sqlite3 (pip install db-sqlite3).
#2 - Instale o Nmap no caminho padrão (C:\Program Files (x86)\Nmap\nmap.exe).
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
import PIL
from PIL import Image, ImageTk

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
    janela_principal.geometry("400x400")
    
    # Função para corrigir a posição dos botões
    def corrigir_posicao_botoes():
        for widget in janela_principal.winfo_children():
            if isinstance(widget, tk.Button):
                widget.pack_configure(pady=10)
    
    btn_escanear = tk.Button(janela_principal, text="Escanear a Rede", command=scanner)
    btn_escanear.pack(pady=10)
    
    btn_listar = tk.Button(janela_principal, text="Listar Informações", command=listar_informacoes)
    btn_listar.pack(pady=10)
    
    btn_sair = tk.Button(janela_principal, text="Sair", command=janela_principal.quit)
    btn_sair.pack(pady=10)
    
    corrigir_posicao_botoes()
    
    janela_principal.mainloop()

def scanner():
    def escanear_propria_rede():
        # Obtém o endereço IP e a máscara de sub-rede
        ip = socket.gethostbyname(socket.gethostname())
        mascara = ipaddress.IPv4Network(f"{ip}/24", strict=False).netmask
        rede = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)
        
        # Configura o scanner Nmap
        nm = nmap.PortScanner()
        nm.scan(hosts=str(rede), arguments='-p 22,80')
        
        # Processa os resultados
        resultados = []
        for host in nm.all_hosts():
            hostname = nm[host].hostname()
            mac_address = nm[host]['addresses'].get('mac', 'N/A')
            ip_address = nm[host]['addresses'].get('ipv4', 'N/A')
            porta_22 = 'open' if nm[host]['tcp'][22]['state'] == 'open' else 'closed'
            porta_80 = 'open' if nm[host]['tcp'][80]['state'] == 'open' else 'closed'
            resultados.append((hostname, mac_address, ip_address, porta_22, porta_80))
        
        # Guarda os resultados no banco de dados
        with sqlite3.connect(arquivo) as conn:
            cursor = conn.cursor()
            for resultado in resultados:
                cursor.execute('''
                    INSERT INTO escaneamentos (data, hostname, mac_address, ip, porta_22, porta_80)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resultado[0], resultado[1], resultado[2], resultado[3], resultado[4]))
            conn.commit()

    def escanear_outra_rede():
        def iniciar_escaneamento():
            rede = entry_rede.get()
            nm = nmap.PortScanner()
            nm.scan(hosts=rede, arguments='-p 22,80')
            
            resultados = []
            for host in nm.all_hosts():
                hostname = nm[host].hostname()
                mac_address = nm[host]['addresses'].get('mac', 'N/A')
                ip_address = nm[host]['addresses'].get('ipv4', 'N/A')
                porta_22 = 'open' if nm[host]['tcp'][22]['state'] == 'open' else 'closed'
                porta_80 = 'open' if nm[host]['tcp'][80]['state'] == 'open' else 'closed'
                resultados.append((hostname, mac_address, ip_address, porta_22, porta_80))
            
            # Guarda os resultados no banco de dados
            with sqlite3.connect(arquivo) as conn:
                cursor = conn.cursor()
                for resultado in resultados:
                    cursor.execute('''
                        INSERT INTO escaneamentos (data, hostname, mac_address, ip, porta_22, porta_80)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resultado[0], resultado[1], resultado[2], resultado[3], resultado[4]))
                conn.commit()
        
        janela_outra_rede = tk.Toplevel()
        janela_outra_rede.title("Escanear Outra Rede")
        janela_outra_rede.geometry("400x200")
        
        label_rede = tk.Label(janela_outra_rede, text="Digite a rede (ex: 192.168.1.0/24):")
        label_rede.pack(pady=5)
        entry_rede = tk.Entry(janela_outra_rede)
        entry_rede.pack(pady=5)
        
        btn_iniciar = tk.Button(janela_outra_rede, text="Iniciar Escaneamento", command=iniciar_escaneamento)
        btn_iniciar.pack(pady=20)
    
    janela_opcoes = tk.Toplevel()
    janela_opcoes.title("Opções de Escaneamento")
    janela_opcoes.geometry("400x200")

    # Obtém o endereço IP e a máscara de sub-rede
    ip = socket.gethostbyname(socket.gethostname())
    mascara = ipaddress.IPv4Network(f"{ip}/24", strict=False).netmask
    rede = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)

    # Exibe a rede do usuário
    label_rede_usuario = tk.Label(janela_opcoes, text=f"Sua rede: {rede}")
    label_rede_usuario.pack(pady=5)

    btn_propria_rede = tk.Button(janela_opcoes, text="Escanear Própria Rede", command=escanear_propria_rede)
    btn_propria_rede.pack(pady=5)
    
    btn_outra_rede = tk.Button(janela_opcoes, text="Escanear Outra Rede", command=escanear_outra_rede)
    btn_outra_rede.pack(pady=5)
    
    btn_voltar = tk.Button(janela_opcoes, text="Voltar ao Menu Principal", command=janela_opcoes.destroy)
    btn_voltar.pack(pady=5)

    janela_opcoes.mainloop()
    

def listar_informacoes():
    def buscar_informacoes():
        data = entry_data.get()
        try:
            data_formatada = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d')
            with sqlite3.connect(arquivo) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM escaneamentos WHERE date(data) = ?", (data_formatada,))
                resultados = cursor.fetchall()
                
                if resultados:
                    resultado_texto = "\n".join([f"ID: {r[0]}, Data: {r[1]}, Hostname: {r[2]}, MAC: {r[3]}, IP: {r[4]}, Porta 22: {r[5]}, Porta 80: {r[6]}" for r in resultados])
                    messagebox.showinfo("Resultados", resultado_texto)
                else:
                    messagebox.showinfo("Resultados", "Nenhum resultado encontrado para a data fornecida.")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use o formato DIA/MÊS/ANO.")
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao conectar com o banco de dados: {e}")

    janela_busca = tk.Toplevel()
    janela_busca.title("Buscar Informações")
    janela_busca.geometry("400x200")

    label_data = tk.Label(janela_busca, text="Digite a data (DIA/MÊS/ANO):")
    label_data.pack(pady=5)
    entry_data = tk.Entry(janela_busca)
    entry_data.pack(pady=5)

    btn_buscar = tk.Button(janela_busca, text="Buscar", command=buscar_informacoes)
    btn_buscar.pack(pady=20)

# Configuração da janela de login
janela_login = tk.Tk()
janela_login.title("Login")
janela_login.geometry("800x800")

########################################################## IMPLEMENTA LOGO NO TOPO DO PROGRAMA ##########################################################################
# Função para carregar a imagem GIF
def carregar_gif(caminho):
    return Image.open(caminho)

# Caminho da imagem GIF
caminho_logo = "apoio\\teste.gif"

# Carregar a imagem GIF
imagem_logo = carregar_gif(caminho_logo)

# Adicionar a imagem na janela de login
label_logo = tk.Label(janela_login, image=ImageTk.PhotoImage(imagem_logo))
label_logo.pack(pady=20)

# Função para redimensionar a imagem
def redimensionar_imagem(imagem, largura, altura):
    return imagem.resize((largura, altura), Image.LANCZOS)

# Função para animar o GIF
def animar_gif(ind):
    try:
        frame = Image.open(caminho_logo)
        frame.seek(ind)
        frame = redimensionar_imagem(frame, 200, 100)
        frame_image = ImageTk.PhotoImage(frame)
        label_logo.configure(image=frame_image)
        label_logo.image = frame_image
        ind += 1
        janela_login.after(100, animar_gif, ind)
    except EOFError:
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
label_logo_rodape = tk.Label(janela_login, image=ImageTk.PhotoImage(imagem_logo_rodape))
label_logo_rodape.pack(side="bottom", pady=10)

# Função para redimensionar a imagem
def redimensionar_imagem(imagem, largura, altura):
    return imagem.resize((largura, altura), Image.LANCZOS)

# Função para animar o GIF do rodapé
def animar_gif_rodape(ind):
    try:
        frame = Image.open(caminho_logo_rodape)
        frame.seek(ind)
        frame = redimensionar_imagem(frame, 200, 100)
        frame_image = ImageTk.PhotoImage(frame)
        label_logo_rodape.configure(image=frame_image)
        label_logo_rodape.image = frame_image
        ind += 1
        janela_login.after(100, animar_gif_rodape, ind)
    except EOFError:
        ind = 0
        janela_login.after(100, animar_gif_rodape, ind)

# Iniciar a animação do GIF do rodapé
janela_login.after(0, animar_gif_rodape, 0)

########################################################## FIM DO RODAPÉ DO PROGRAMA ##########################################################################

janela_login.mainloop()