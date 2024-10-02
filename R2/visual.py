#Bibliotecas de imagem e interface gráfica
#TKinter é uma biblioteca padrão do Python para criar interfaces gráficas
import tkinter as tk
from tkinter import ttk
#Bibliotecas de calendário do tkinter
from tkcalendar import Calendar
#Bibliotecas de imagem e interface gráfica
#Bibliotecas de mensagem do tkinter
from tkinter import messagebox
#Bibliotecas de fonte do tkinter
from tkinter import font
#Bibliotecas de tempo e progresso
#A biblioteca datetime fornece classes para manipular datas e horas
from datetime import datetime
#A biblioteca tqdm fornece uma barra de progresso para loops
from tqdm import tqdm
#Bibliotecas de imagem
#A biblioteca PIL (Python Imaging Library) fornece suporte para abrir, manipular e salvar muitos tipos diferentes de arquivos de imagem
from PIL import Image, ImageTk
#Bibliotecas de rede
#A biblioteca hashlib fornece funções de hash seguras para senhas
import hashlib
#A biblioteca os fornece funções para interagir com o sistema operacional
import os
#A biblioteca sqlite3 fornece uma interface para o banco de dados SQLite
import sqlite3
#Bibliotecas de scanner de rede
#Importar o arquivo scanner_rede.py
import scanner_rede
import scanner_rede as scanner_file
#Importar o arquivo dashboard.py
import dashboard

#Função para verificar se o login está correto
def verificar_login():
    # Obter o usuário e a senha dos campos de entrada da janela de login
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    
    # Verifica a senha de forma criptografada usando o algoritmo SHA-256
    senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()
    
    # Tenta conectar ao banco de dados e verificar se o usuário e a senha estão corretos
    try:
        # Obtem o caminho do banco de dados nesse caso dentro da mesma pasta do arquivo e dentro do arquivo banco.db
        caminho_banco_dados = os.path.join(os.path.dirname(__file__), 'banco.db')
        # Cria uma variavel para armazenar a função de conexão com o banco de dados
        conn = sqlite3.connect(caminho_banco_dados)
        # Cria uma variavel para armazenar o cursor do SQLite
        cursor = conn.cursor()
        
        # Verifica se o usuário e a senha estão corretos
        # Usa a variavel cursor para executar a query SQL buscando dentro da tabela usuarios o usuario e a senha criptografada
        # Faz a busca com o comando SELECT * FROM usuarios WHERE usuario = ? AND senha = ?
        # O argumento ? é inserido na query para evitar injeção de SQL e também indicar que os valores serão passados como parâmetros
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha_criptografada))
        # A variavel resultado recebe o resultado da busca
        resultado = cursor.fetchone()
        
        # Se o resultado for verdadeiro, chama a função janela_principal 
        if resultado:
            # Atualiza a coluna ultimo_login com a data e hora atual
            data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE usuarios SET ultimo_login = ? WHERE usuario = ?", (data_hora_atual, usuario))
            conn.commit()
            
            # Verifica se o usuário é administrador
            is_admin = resultado[6]  # Supondo que a coluna is_admin é a sétima coluna na tabela usuarios
            
            # Define variáveis globais para armazenar o estado do usuário logado
            global usuario_logado, is_admin_logado, usuario_admin, usuario_comum
            usuario_logado = usuario
            is_admin_logado = is_admin
            
            # Sub verificação para definir variáveis específicas para administrador e usuário comum
            if is_admin:
                usuario_admin = usuario
                usuario_comum = None
            else:
                usuario_comum = usuario
                usuario_admin = None
            
            # Permite que as variáveis sejam usadas pelo programa todo
            globals().update({
                'usuario_logado': usuario_logado,
                'is_admin_logado': is_admin_logado,
                'usuario_admin': usuario_admin,
                'usuario_comum': usuario_comum
            })
            print("Login correto")
            janela_principal()
        # Se não, exibe uma mensagem de erro
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")
        # Fecha o cursor e a conexão com o banco de dados
        # Somente o close() é necessário
        conn.close()
    # Se ocorrer um erro ao conectar ao banco de dados, exibe uma mensagem de erro    
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")

#Função para abrir a janela principal após o login correto
def janela_principal():
    #Fecha a janela de login
    janela_login.destroy()
    
    #Cria a janela principal usando o TKinter
    janela_principal = tk.Tk()
    #Define o título da janela principal
    janela_principal.title("Menu Principal")
    #Define a o tamanho da janela principal em pixels
    janela_principal.geometry("400x400")

    # Label para mostrar o usuário logado e se é administrador ou não
    label_usuario_logado = tk.Label(janela_principal, text=f"Usuário: {usuario_logado} ({'Admin' if is_admin_logado else 'Comum'})")
    label_usuario_logado.pack(anchor='nw', padx=10, pady=10)
    
    #Função para organizar os botões na janela principal usando o pack_configure e função pady (padding)
    def corrigir_posicao_botoes():
        #O padding é o espaço entre o widget e a borda da janela

        #Para cada widget na janela principal, ajusta o padding para 10 pixels
        for widget in janela_principal.winfo_children():
            #A função pack_configure é usada para configurar a posição e o tamanho do widget
            widget.pack_configure(pady=10)
    
    #Função para abrir a janela de funções de scanner de rede ao clicar no botão "Funções de Scanner de Rede"
    def abrir_janela_escanear():
        #Cria uma nova janela para as funções de scanner de rede usando o TKinter
        janela_escanear = tk.Toplevel(janela_principal)
        #Define o título da janela de scanner de rede
        janela_escanear.title("Scanner de Rede")
        #Define o tamanho da janela de scanner de rede em pixels
        janela_escanear.geometry("300x200")

        #Botão com função para escanear a própria rede usando o comando scanner_file.scanner
        #A variavel command é usada para chamar a função scanner_file.scanner ao clicar no botão
        #Foi definida a função scanner_file no inicio do código que referencia o arquivo scanner_rede.py e chama a função scanner dentro desse arquivo
        btn_escanear_propria_rede = tk.Button(janela_escanear, text="Escanear sua rede", command=scanner_file.scanner)
        btn_escanear_propria_rede.pack(pady=10)

        btn_visualizar = tk.Button(janela_escanear, text="Visualizar Informações Armazenadas", command=visualizar_informacoes)
        btn_visualizar.pack(pady=5)


        #Botão para voltar ao menu principal ao clicar no botão "Voltar ao Menu Principal" e fecha a janela de funções de scanner de rede
        btn_voltar = tk.Button(janela_escanear, text="Voltar ao Menu Principal", command=janela_escanear.destroy)
        btn_voltar.pack(pady=10)
        #Função da janela de scanner acaba aqui

    #Função para visualizar as informações armazenadas no banco de dados do scanner de rede
    def visualizar_informacoes():
        #Principal que irá receber a seleção da data e buscar as informações no banco de dados
        def buscar_informacoes(data_selecionada):
            #Testa se a data inserida é válida. Essa função precisa ser chamada antes de converter a data para o formato do banco de dados
            try:
                data_selecionada = datetime.strptime(data_selecionada, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use DIA/MÊS/ANO.")
                return

            #Cria uma nova janela para exibir as informações buscadas
            janela_informacoes = tk.Toplevel()
            janela_informacoes.title("Informações Armazenadas")
            janela_informacoes.geometry("1200x600")
            text_informacoes = tk.Text(janela_informacoes, wrap="word")
            text_informacoes.pack(expand=True, fill="both")

            #Conecta ao banco de dados e define a query SQL para buscar as informações
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT data, hostname, mac_address, ip, portas FROM scanner WHERE data LIKE ?', (f"{data_selecionada}%",))
                #Armazena os resultados da busca dentro da variavel registros
                registros = cursor.fetchall()

                #Cria um texto formatado com as informações encontradas
                informacoes_texto = "\n".join([
                    f"Data: {r[0]} | Hostname: {r[1]} | MAC: {r[2]} | IP: {r[3]} | Portas: {r[4]}"
                    for r in registros
                ]) if registros else "Nenhuma informação encontrada para a data selecionada."

                #Insere o texto formatado na caixa de texto da janela informacoes_texto e coloca o texto na posição 1.0 (linha 1, coluna 0)
                text_informacoes.insert("1.0", informacoes_texto)
                text_informacoes.update()
            #A função buscar_informacoes acaba aqui

        #Cria uma nova janela para selecionar a data juntamente com um calendario
        janela_selecao_data = tk.Toplevel()
        janela_selecao_data.title("Selecione a Data")
        janela_selecao_data.geometry("300x400")

        label_data = tk.Label(janela_selecao_data, text="Selecione a Data:")
        label_data.pack(pady=10)

        #Obtem o caminho do banco de dados
        db_path = os.path.join(os.path.dirname(__file__), 'banco.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            #Busca as datas únicas armazenadas no banco de dados
            cursor.execute('SELECT DISTINCT data FROM scanner')
            #Armazena as datas únicas encontradas dentro da variavel datas
            datas = [row[0] for row in cursor.fetchall()]

        #Cria uma variavel para armazenar a data atual
        var_data = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        #Cria um campo de entrada de texto para a data
        entry_data = tk.Entry(janela_selecao_data, textvariable=var_data)
        entry_data.pack(pady=10)

        #Cria uma divisa para separar o campo de entrada de texto do calendário
        label_calendario = tk.Label(janela_selecao_data, text="Calendário:")
        label_calendario.pack(pady=10)

        #Função que cria um evento ao selecionar uma data no calendário
        def selecionar_data(event):
            var_data.set(cal.selection_get().strftime("%d/%m/%Y"))

        #Cria um calendário para selecionar a data
        cal = Calendar(janela_selecao_data, selectmode='day', date_pattern='dd/mm/yyyy')
        cal.pack(pady=10)
        #Vincula o evento da seleção da data para colocar dentro do campo de entrada de texto
        cal.bind("<<CalendarSelected>>", selecionar_data)

        #Cria um botão e chama a função buscar_informacoes ao clicar no botão
        btn_buscar = tk.Button(janela_selecao_data, text="Buscar", command=lambda: buscar_informacoes(var_data.get()))
        btn_buscar.pack(pady=10)
        #A função visualizar_informacoes acaba aqui

    #Função para abrir a janela do dashboard ao clicar no botão "DASHBOARD"
    def abrir_dashboard():
        dashboard.abrir_dashboard()

    #Botão para abrir a janela do dashboard ao clicar no botão "DASHBOARD"
    btn_dashboard = tk.Button(janela_principal, text="DASHBOARD", command=abrir_dashboard)
    btn_dashboard.pack(pady=10)

    #Aqui volta para a função janela_principal
    #Botão para abrir a janela de funções de scanner de rede ao clicar no botão "Funções de Scanner de Rede"
    btn_funcoes_scanner = tk.Button(janela_principal, text="FUNÇÕES DE SCANNER DE REDE", command=abrir_janela_escanear)
    btn_funcoes_scanner.pack(pady=10)

    # Função para abrir a janela de configurações de usuários
    def abrir_configuracoes_usuarios():
        # Cria uma nova janela para as configurações de usuários
        janela_configuracoes_usuarios = tk.Toplevel(janela_principal)
        janela_configuracoes_usuarios.title("Configurações de Usuários")
        janela_configuracoes_usuarios.geometry("400x300")

        def adicionar_usuario():
            # Cria uma nova janela para adicionar usuários
            janela_adicionar_usuario = tk.Toplevel(janela_configuracoes_usuarios)
            janela_adicionar_usuario.title("Adicionar Usuário")
            janela_adicionar_usuario.geometry("400x400")

            # Labels e campos de entrada para os dados do usuário
            tk.Label(janela_adicionar_usuario, text="Usuário:").pack(pady=5)
            entry_novo_usuario = tk.Entry(janela_adicionar_usuario)
            entry_novo_usuario.pack(pady=5)

            tk.Label(janela_adicionar_usuario, text="Senha:").pack(pady=5)
            entry_nova_senha = tk.Entry(janela_adicionar_usuario, show="*")
            entry_nova_senha.pack(pady=5)

            tk.Label(janela_adicionar_usuario, text="Nome Completo:").pack(pady=5)
            entry_nome_completo = tk.Entry(janela_adicionar_usuario)
            entry_nome_completo.pack(pady=5)

            tk.Label(janela_adicionar_usuario, text="Email:").pack(pady=5)
            entry_email = tk.Entry(janela_adicionar_usuario)
            entry_email.pack(pady=5)

            # Label para a opção de administrador
            label_pergunta_admin = tk.Label(janela_adicionar_usuario, text="Precisa ser administrador ?")
            label_pergunta_admin.pack(pady=5)

            # Variável para armazenar o estado da caixa de seleção
            is_admin_var = tk.IntVar()

            # Função para atualizar o texto ao lado da caixa de seleção
            def atualizar_texto_admin():
                if is_admin_var.get() == 1:
                    label_admin_status.config(text="Será administrador")
                else:
                    label_admin_status.config(text="Não será administrador")

            # Label para mostrar o status da seleção
            label_admin_status = tk.Label(janela_adicionar_usuario, text="Não será administrador")
            label_admin_status.pack(pady=5)

            # Caixa de seleção para definir se o usuário é administrador
            check_is_admin = tk.Checkbutton(janela_adicionar_usuario, variable=is_admin_var, command=atualizar_texto_admin)
            check_is_admin.pack(pady=5)

            # Função para salvar o novo usuário no banco de dados
            def salvar_usuario():
                usuario = entry_novo_usuario.get()
                senha = entry_nova_senha.get()
                nome_completo = entry_nome_completo.get()
                email = entry_email.get()
                is_admin = is_admin_var.get()

                # Verifica se todos os campos foram preenchidos
                if not all([usuario, senha, nome_completo, email]):
                    messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
                    return

                # Criptografa a senha
                senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()
                data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Insere o novo usuário no banco de dados
                try:
                    with sqlite3.connect(caminho_banco_dados) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO usuarios (usuario, senha, data_criacao, nome_completo, email, is_admin)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (usuario, senha_criptografada, data_criacao, nome_completo, email, int(is_admin)))
                        conn.commit()
                        messagebox.showinfo("Sucesso", "Usuário adicionado com sucesso.")
                        janela_adicionar_usuario.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Erro", f"Erro ao adicionar usuário: {e}")

            # Botão para salvar o novo usuário
            btn_salvar_usuario = tk.Button(janela_adicionar_usuario, text="Salvar Usuário", command=salvar_usuario)
            btn_salvar_usuario.pack(pady=20)

        # Botão para adicionar usuários
        btn_adicionar_usuarios = tk.Button(janela_configuracoes_usuarios, text="Adicionar Usuários", command=adicionar_usuario)
        btn_adicionar_usuarios.pack(pady=10)

        def editar_usuarios():
            # Cria uma nova janela para editar usuários
            janela_editar_usuarios = tk.Toplevel(janela_configuracoes_usuarios)
            janela_editar_usuarios.title("Editar Usuários Existentes")
            janela_editar_usuarios.geometry("600x400")

            # Função para buscar as informações do usuário selecionado
            def buscar_informacoes_usuario(event=None):
                if not listbox_usuarios.curselection():
                    messagebox.showerror("Erro", "Nenhum usuário selecionado.")
                    return
                usuario_selecionado = listbox_usuarios.get(listbox_usuarios.curselection()).split(" | ")[1]
                try:
                    with sqlite3.connect(caminho_banco_dados) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT usuario, nome_completo, email, is_admin FROM usuarios WHERE usuario = ?", (usuario_selecionado,))
                        usuario_info = cursor.fetchone()
                        if usuario_info:
                            entry_usuario_editar.delete(0, tk.END)
                            entry_usuario_editar.insert(0, usuario_info[0])
                            entry_nome_completo_editar.delete(0, tk.END)
                            entry_nome_completo_editar.insert(0, usuario_info[1])
                            entry_email_editar.delete(0, tk.END)
                            entry_email_editar.insert(0, usuario_info[2])
                            is_admin_var_editar.set(usuario_info[3])
                        else:
                            messagebox.showerror("Erro", "Usuário não encontrado.")
                except sqlite3.Error as e:
                    messagebox.showerror("Erro", f"Erro ao buscar informações do usuário: {e}")

            # Frame para a lista de usuários com barra de rolagem
            frame_lista_usuarios = tk.Frame(janela_editar_usuarios)
            frame_lista_usuarios.pack(pady=10, fill=tk.BOTH, expand=True)

            # Barra de rolagem vertical
            scrollbar_vertical = tk.Scrollbar(frame_lista_usuarios, orient=tk.VERTICAL)
            scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)

            # Lista de usuários
            listbox_usuarios = tk.Listbox(frame_lista_usuarios, yscrollcommand=scrollbar_vertical.set, height=10)
            listbox_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Configura a barra de rolagem para a lista de usuários
            scrollbar_vertical.config(command=listbox_usuarios.yview)

            # Vincula o evento de seleção da lista de usuários
            listbox_usuarios.bind('<<ListboxSelect>>', buscar_informacoes_usuario)

            # Função para carregar os usuários na lista
            def carregar_usuarios():
                try:
                    with sqlite3.connect(caminho_banco_dados) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT id, usuario, nome_completo, email, is_admin, ultimo_login FROM usuarios")
                        usuarios = cursor.fetchall()
                        listbox_usuarios.delete(0, tk.END)
                        for usuario in usuarios:
                            usuario_info = f"{usuario[0]} | {usuario[1]} | {usuario[2]} | {usuario[3]} | {'Admin' if usuario[4] else 'Comum'} | Último login: {usuario[5]}"
                            listbox_usuarios.insert(tk.END, usuario_info)
                except sqlite3.Error as e:
                    messagebox.showerror("Erro", f"Erro ao carregar usuários: {e}")

            # Função para salvar as alterações do usuário
            def salvar_alteracoes():
                usuario = entry_usuario_editar.get()
                nome_completo = entry_nome_completo_editar.get()
                email = entry_email_editar.get()
                is_admin = is_admin_var_editar.get()

                # Verifica se todos os campos foram preenchidos
                if not all([usuario, nome_completo, email]):
                    messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
                    return

                 # Verifica se houve alterações nos campos do usuário
                with sqlite3.connect(caminho_banco_dados) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome_completo, email, is_admin FROM usuarios WHERE usuario = ?", (usuario,))
                    usuario_atual = cursor.fetchone()
                             
                    if usuario_atual:
                        nome_completo_atual, email_atual, is_admin_atual = usuario_atual
                            
                        if nome_completo != nome_completo_atual or email != email_atual or int(is_admin) != is_admin_atual:
                            # Atualiza as informações do usuário no banco de dados
                            try:
                                cursor.execute("""
                                    UPDATE usuarios
                                    SET nome_completo = ?, email = ?, is_admin = ?
                                    WHERE usuario = ?
                                """, (nome_completo, email, int(is_admin), usuario))
                                conn.commit()
                                messagebox.showinfo("Sucesso", "Informações do usuário atualizadas com sucesso.")
                                carregar_usuarios()  # Recarrega a lista de usuários para refletir as alterações
                            except sqlite3.Error as e:
                                messagebox.showerror("Erro", f"Erro ao atualizar informações do usuário: {e}")
                        else:
                            messagebox.showinfo("Informação", "Nenhuma alteração detectada.")
                    else:
                        messagebox.showerror("Erro", "Usuário não encontrado.")

            tk.Label(janela_editar_usuarios, text="Usuário:").pack(pady=5)
            entry_usuario_editar = tk.Entry(janela_editar_usuarios)
            entry_usuario_editar.pack(pady=5)

            tk.Label(janela_editar_usuarios, text="Nome Completo:").pack(pady=5)
            entry_nome_completo_editar = tk.Entry(janela_editar_usuarios)
            entry_nome_completo_editar.pack(pady=5)

            tk.Label(janela_editar_usuarios, text="Email:").pack(pady=5)
            entry_email_editar = tk.Entry(janela_editar_usuarios)
            entry_email_editar.pack(pady=5)

            # Variável para armazenar o estado da caixa de seleção
            is_admin_var_editar = tk.IntVar()

            # Label para a opção de administrador
            label_pergunta_admin_editar = tk.Label(janela_editar_usuarios, text="Administrador:")
            label_pergunta_admin_editar.pack(pady=5)

            # Caixa de seleção para definir se o usuário é administrador
            check_is_admin_editar = tk.Checkbutton(janela_editar_usuarios, variable=is_admin_var_editar)
            check_is_admin_editar.pack(pady=5)

            # Botão para salvar as alterações
            btn_salvar_alteracoes = tk.Button(janela_editar_usuarios, text="Salvar Alterações", command=salvar_alteracoes)
            btn_salvar_alteracoes.pack(pady=20)

            # Carrega os usuários na lista
            carregar_usuarios()

            # Desabilita a edição se o usuário logado não for administrador
            if not is_admin_logado:
                entry_usuario_editar.config(state='disabled')
                entry_nome_completo_editar.config(state='disabled')
                entry_email_editar.config(state='disabled')
                check_is_admin_editar.config(state='disabled')
                btn_salvar_alteracoes.config(state='disabled')

        # Botão para editar usuários existentes
        btn_editar_usuarios = tk.Button(janela_configuracoes_usuarios, text="Editar Usuários Existentes", command=editar_usuarios)
        btn_editar_usuarios.pack(pady=10)

        # Botão para visualizar alterações
        btn_visualizar_alteracoes = tk.Button(janela_configuracoes_usuarios, text="Visualizar Alterações")
        btn_visualizar_alteracoes.pack(pady=10)

        # Botão para voltar ao menu principal
        btn_voltar_menu_principal = tk.Button(janela_configuracoes_usuarios, text="Voltar ao Menu Principal", command=janela_configuracoes_usuarios.destroy)
        btn_voltar_menu_principal.pack(pady=10)
    # Botão para abrir a janela de configurações de usuários
    btn_configuracoes_usuarios = tk.Button(janela_principal, text="CONFIGURAÇÕES DE USUÁRIOS", command=abrir_configuracoes_usuarios)
    btn_configuracoes_usuarios.pack(pady=10)

    #Botão para abrir a janela de configurações do programa ao clicar no botão "Configurações do Programa"
    btn_configuracoes = tk.Button(janela_principal, text="CONFIGURAÇÕES DO PROGRAMA")
    btn_configuracoes.pack(pady=10)
    
    #Botão para sair do programa ao clicar no botão "Sair"
    btn_sair = tk.Button(janela_principal, text="SAIR", command=janela_principal.quit)
    btn_sair.pack(pady=10)
    
    #Chama a função corrigir_posicao_botoes para organizar os botões na janela principal
    corrigir_posicao_botoes()
    
    #Inicia o loop principal da janela principal
    janela_principal.mainloop()
    #A função janela_principal acaba aqui

#Configuração da janela de login
janela_login = tk.Tk()
janela_login.title("Login")
janela_login.geometry("800x800")

#Função que verifica se o arquivo de imagem foi carregado corretamente, caso não exibe uma mensagem de erro
def carregar_gif(caminho):
    try:
        # Retorna a imagem GIF carregada
        return Image.open(caminho)
    except FileNotFoundError:
        messagebox.showerror("Erro", f"Arquivo não encontrado: {caminho}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar a imagem: {e}")
    return None

#Parte do Header da janela de login
#Conecta ao banco de dados para obter o caminho da imagem do logo principal
caminho_banco_dados = os.path.join(os.path.dirname(__file__), 'banco.db')
try:
    with sqlite3.connect(caminho_banco_dados) as conn:
        cursor = conn.cursor()
        #Busca o caminho da imagem do logo principal na tabela config_programa dentro de logo_principal
        cursor.execute("SELECT logo_principal FROM config_programa")
        caminho_logo = cursor.fetchone()[0]
except sqlite3.Error as e:
    messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")

#Guarda a imagem GIF carregada na variavel imagem_logo
imagem_logo = carregar_gif(caminho_logo)

#Adiciona a imagem na janela de login (logo)
label_logo = tk.Label(janela_login, image=ImageTk.PhotoImage(imagem_logo))
label_logo.pack(pady=20)

#Função criada para redimensionar a imagem usando a biblioteca Image do PIL e o método resize com o algoritmo LANCZOS que é um algoritmo de interpolação de imagem
#Essa função somente carrega as estruturas de redimensionamento da imagem, não redimensiona a imagem em si
def redimensionar_imagem(imagem, largura, altura):
    return imagem.resize((largura, altura), Image.LANCZOS)

#Função para animar o GIF
def animar_gif(ind):
    #Por se tratar de um arquivo GIF, é necessário verificar se o arquivo chegou ao final para reiniciar a animação.
    #Isso permite que a animação seja contínua e que possamos controlar a velocidade da animação, loop e outros parâmetros.
    try:
        #A função seek() é usada para mover o cursor para um determinado quadro no arquivo GIF usando um índice
        imagem_logo.seek(ind)
        #Função para redimensionar a imagem do logo chamando a função redimensionar_imagem
        imagem_redimensionada = ImageTk.PhotoImage(redimensionar_imagem(imagem_logo, 600, 300))  #Redimensine a imagem ajustando os valores de largura e altura
        #Adiciona a imagem redimensionada na variavel label_logo que é a imagem do logo e chamada na janela de login
        label_logo.configure(image=imagem_redimensionada)
        #Mantém uma referência à imagem para evitar que seja perdida pelo garbage collector.
        #Garbage collector é um processo que gerencia a memória do computador e libera memória não utilizada, evitando vazamentos de memória.
        label_logo.image = imagem_redimensionada
        #Incrementa o índice para avançar para o próximo quadro
        ind += 1
        #Chama a função após 100 milissegundos para animar o próximo quadro controlando a velocidade da animação
        janela_login.after(100, animar_gif, ind)
    #Se ocorrer um erro de final de arquivo ele para.
    except EOFError:
        pass
#Fim da função animar_gif
#Apesar da função animar_gif terminar, aqui ela é chamada para iniciar a animação do GIF no ponto 0
janela_login.after(0, animar_gif, 0)

#Define a variavel fonte_padrao com a fonte do texto.
fonte_padrao = ("Terminal", 18)
#Cria a variavel label_usuario com a função Label do TKinter para criar um texto na janela de login
label_usuario = tk.Label(janela_login, text="Usuário:", font=fonte_padrao)
label_usuario.pack(pady=5)
#Cria a variavel entry_usuario com a função Entry do TKinter para criar um campo de entrada de texto na janela de login
entry_usuario = tk.Entry(janela_login, font=fonte_padrao)
entry_usuario.pack(pady=5)
#Essa variavel permite que o cursor do teclado fique no campo de entrada de texto ao iniciar a janela de login
entry_usuario.focus_set()
#Cria a variavel label_senha com a função Label do TKinter para criar um texto na janela de login
label_senha = tk.Label(janela_login, text="Senha:", font=fonte_padrao)
label_senha.pack(pady=5)
#Cria a variavel entry_senha com a função Entry do TKinter para criar um campo de entrada de texto na janela de login
entry_senha = tk.Entry(janela_login, show="*", font=fonte_padrao)
entry_senha.pack(pady=5)

#Função para verificar um evento no teclado e chamar a função verificar_login
#Abaixo ele será chamado com o botão que quisermos que seja pressionado para chamar a função verificar_login
def pressionar_enter(event):
    verificar_login()
#Aqui ele chama a função pressionar_enter ao o botão que definimos
entry_senha.bind('<Return>', pressionar_enter)

#Cria a variavel btn_login com a função Button do TKinter para criar um botão na janela de login e chama a função verificar_login ao clicar no botão
#Disparando todo o processo de inicio do programa
btn_login = tk.Button(janela_login, text="Login", command=verificar_login, font=fonte_padrao)
btn_login.pack(pady=20)

#Parte do rodapé da janela de login que procura dentro do banco de dados o caminho da imagem GIF do rodapé
#Mesma lógica do logo principal
try:
    with sqlite3.connect(caminho_banco_dados) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT logo_rodape FROM config_programa")
        caminho_logo_rodape = cursor.fetchone()[0]
except sqlite3.Error as e:
    messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")

#Guardar a imagem GIF carregada na variável imagem_logo_rodape
imagem_logo_rodape = carregar_gif(caminho_logo_rodape)

#Adiciona a imagem na janela de login (rodapé) com a função Label do TKinter
label_logo_rodape = tk.Label(janela_login, image=ImageTk.PhotoImage(imagem_logo_rodape))
label_logo_rodape.pack(side="bottom", pady=10)

#Função para animar o GIF do rodapé executando a mesma lógica da função animar_gif
def animar_gif_rodape(ind):
    try:
        imagem_logo_rodape.seek(ind)
        frame = ImageTk.PhotoImage(redimensionar_imagem(imagem_logo_rodape, 600, 300))  # Redimensiona a imagem do rodapé
        label_logo_rodape.configure(image=frame)
        label_logo_rodape.image = frame  # Mantém uma referência à imagem para evitar que seja coletada pelo garbage collector
        ind += 1
        janela_login.after(100, animar_gif_rodape, ind)
    except EOFError:
        pass
#Fim da função animar_gif_rodape

#Iniciar a animação do GIF do rodapé
janela_login.after(0, animar_gif_rodape, 0)

#Inicia o loop principal da janela de login
janela_login.mainloop()
#Fim do código