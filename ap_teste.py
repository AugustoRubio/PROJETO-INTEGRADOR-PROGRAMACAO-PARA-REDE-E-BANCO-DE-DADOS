import tkinter as tk
import sqlite3
import hashlib
from tkinter import messagebox
import nmap
import TESTE_REDE
import os

# Conexão com o banco de dados SQLite
try:
    with sqlite3.connect('usuarios.db') as conn:
        cursor = conn.cursor()

        # Criação da tabela de usuários, caso não exista
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()
        messagebox.showinfo("Conexão bem-sucedida", "Conectado ao banco de dados com sucesso.")
except sqlite3.Error as e:
    messagebox.showerror("Erro de conexão", f"Erro ao conectar ao banco de dados: {e}")

def verify_credentials(username, password):
    try:
        with sqlite3.connect('usuarios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM usuarios WHERE username = ?', (username,))
            result = cursor.fetchone()
            if result:
                stored_password = result[0]
                return stored_password == hashlib.sha256(password.encode()).hexdigest()
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return False
root = tk.Tk()
root.title("Tela de Login")
def open_menu():
    menu_window = tk.Toplevel(root)
    menu_window.title("Menu Principal")

    def escanear_rede():
        TESTE_REDE.escanear_rede()

    def listar_registros():
        TESTE_REDE.listar_registros()

    def sair():
        menu_window.destroy()
        import importlib.util

        def load_teste_rede():
            module_name = "TESTE_REDE"
            file_path = os.path.join(os.path.dirname(__file__), "TESTE_REDE.py")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        TESTE_REDE = load_teste_rede()
        
    btn_escanear = tk.Button(menu_window, text="Escanear Rede", command=escanear_rede)
    btn_escanear.pack()

    btn_listar = tk.Button(menu_window, text="Listar Registros", command=listar_registros)
    btn_listar.pack()

    btn_sair = tk.Button(menu_window, text="Sair", command=sair)
    btn_sair.pack()

def login():
    username = entry_username.get()
    password = entry_password.get()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    if username == "admin" and hashed_password == hashlib.sha256("teste".encode()).hexdigest():
        messagebox.showinfo("Login bem-sucedido", "Você fez login com sucesso como admin!")
        open_menu()
    elif verify_credentials(username, password):
        messagebox.showinfo("Login bem-sucedido", "Você fez login com sucesso!")
        open_menu()
    else:
        messagebox.showerror("Erro de login", "Nome de usuário ou senha incorretos.")
# Criação dos widgets
label_username = tk.Label(root, text="Nome de usuário")
label_username.pack()

entry_username = tk.Entry(root)
entry_username.pack()

label_password = tk.Label(root, text="Senha")
label_password.pack()

entry_password = tk.Entry(root, show="*")
entry_password.pack()

login_button = tk.Button(root, text="Login", command=login)
login_button.pack()

# Inicia o loop principal da interface gráfica
root.mainloop()