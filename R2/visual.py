import tkinter as tk
from tkinter import messagebox
from tkinter import font
from datetime import datetime
from tqdm import tqdm
from PIL import Image, ImageTk
import hashlib
import os
import sqlite3
#def conectar_banco_dados():
    # try:
    #     conn = sqlite3.connect('meu_banco_de_dados.db')
    #     messagebox.showinfo("Conexão", "Conectado ao banco de dados com sucesso!")
    #     return conn
    # except sqlite3.Error as e:
    #     messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
    #     return None
#    pass

# Conectar ao banco de dados antes de iniciar a interface gráfica
#conexao = conectar_banco_dados()

# Função para verificar o login
def verificar_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    
    # Criptografar a senha usando SHA256
    senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()
    
    try:
        # Obter o caminho absoluto do arquivo do banco de dados
        caminho_banco_dados = os.path.join(os.path.dirname(__file__), 'banco.db')
        conn = sqlite3.connect(caminho_banco_dados)
        cursor = conn.cursor()
        
        # Verificar se o usuário e a senha estão corretos
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha_criptografada))
        resultado = cursor.fetchone()
        
        if resultado:
            abrir_segunda_janela()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")
        
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")

# Função para abrir a segunda janela
def abrir_segunda_janela():
    janela_login.destroy()
    
    janela_principal = tk.Tk()
    janela_principal.title("Menu Principal")
    janela_principal.geometry("400x400")
    
    # Função para corrigir a posição dos botões
    def corrigir_posicao_botoes():
        for widget in janela_principal.winfo_children():
            widget.pack_configure(pady=10)
    
    btn_escanear = tk.Button(janela_principal, text="Escanear a Rede", command=scanner)
    btn_escanear.pack(pady=10)
    
    btn_listar = tk.Button(janela_principal, text="Listar Informações", command=listar_informacoes)
    btn_listar.pack(pady=10)
    
    btn_sair = tk.Button(janela_principal, text="Sair", command=janela_principal.quit)
    btn_sair.pack(pady=10)
    
    corrigir_posicao_botoes()
    
    janela_principal.mainloop()

# Configuração da janela de login
janela_login = tk.Tk()
janela_login.title("Login")
janela_login.geometry("800x800")

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
        imagem_logo.seek(ind)
        label_logo.configure(image=ImageTk.PhotoImage(imagem_logo))
        ind += 1
        janela_login.after(100, animar_gif, ind)
    except EOFError:
        janela_login.after(100, animar_gif, 0)

# Iniciar a animação do GIF
janela_login.after(0, animar_gif, 0)

# Define a fonte padrão
fonte_padrao = ("Terminal", 18)

# Campos de entrada para usuário e senha
label_usuario = tk.Label(janela_login, text="Usuário:", font=fonte_padrao)
label_usuario.pack(pady=5)
entry_usuario = tk.Entry(janela_login, font=fonte_padrao)
entry_usuario.pack(pady=5)
entry_usuario.focus_set()  # Configura o cursor do teclado para o campo de login

label_senha = tk.Label(janela_login, text="Senha:", font=fonte_padrao)
label_senha.pack(pady=5)
entry_senha = tk.Entry(janela_login, show="*", font=fonte_padrao)
entry_senha.pack(pady=5)

# Função para permitir login ao pressionar Enter
def pressionar_enter(event):
    verificar_login()

# Botão de login
btn_login = tk.Button(janela_login, text="Login", command=verificar_login, font=fonte_padrao)
btn_login.pack(pady=20)

# Bind da tecla Enter para o campo de senha
entry_senha.bind('<Return>', pressionar_enter)

# Caminho da imagem GIF do rodapé
caminho_logo_rodape = "apoio\\teste1.gif"

# Carregar a imagem GIF do rodapé
imagem_logo_rodape = carregar_gif(caminho_logo_rodape)

# Adicionar a imagem na janela de login (rodapé)
label_logo_rodape = tk.Label(janela_login, image=ImageTk.PhotoImage(imagem_logo_rodape))
label_logo_rodape.pack(side="bottom", pady=10)

# Função para animar o GIF do rodapé
def animar_gif_rodape(ind):
    try:
        imagem_logo_rodape.seek(ind)
        label_logo_rodape.configure(image=ImageTk.PhotoImage(imagem_logo_rodape))
        ind += 1
        janela_login.after(100, animar_gif_rodape, ind)
    except EOFError:
        janela_login.after(100, animar_gif_rodape, 0)

# Iniciar a animação do GIF do rodapé
janela_login.after(0, animar_gif_rodape, 0)

janela_login.mainloop()
