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
    #Obter o usuário e a senha dos campos de entrada da janela de login
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    
    #Verifica a senha de forma criptografada usando o algoritmo SHA-256
    senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()
    
    #Tenta conectar ao banco de dados e verificar se o usuário e a senha estão corretos
    try:
        #Obtem o caminho do banco de dados nesse caso dentro da mesma pasta do arquivo e dentro do arquivo banco.db
        caminho_banco_dados = os.path.join(os.path.dirname(__file__), 'banco.db')
        #Cria uma variavel para armazenar a função de conexão com o banco de dados
        conn = sqlite3.connect(caminho_banco_dados)
        #Cria uma variavel para armazenar o cursor do SQLite
        cursor = conn.cursor()
        
        #Verifica se o usuário e a senha estão corretos
        #Usa a variavel cursor para executar a query SQL buscando dentro da tabela usuarios o usuario e a senha criptografada
        #Faz a busca com o comando SELECT * FROM usuarios WHERE usuario = ? AND senha = ?
        #O argumento ? é inserido na query para evitar injeção de SQL e também indicar que os valores serão passados como parâmetros
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha_criptografada))
        #A variavel resultado recebe o resultado da busca
        resultado = cursor.fetchone()
        
        #Se o resultado for verdadeiro, chama a função janela_principal 
        if resultado:
            janela_principal()
        #Se não, exibe uma mensagem de erro
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")
        
        #Fecha o cursor e a conexão com o banco de dados
        #Somente o close() é necessário
        conn.close()
    #Se ocorrer um erro ao conectar ao banco de dados, exibe uma mensagem de erro    
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
    finally:
        print("Login correto")

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
    #Se ocorrer um erro de final de arquivo (EOFError), reinicia a animação
    except EOFError:
        janela_login.after(100, animar_gif, 0)
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
        janela_login.after(100, animar_gif_rodape, 0)
#Fim da função animar_gif_rodape

#Iniciar a animação do GIF do rodapé
janela_login.after(0, animar_gif_rodape, 0)

#Inicia o loop principal da janela de login
janela_login.mainloop()
#Fim do código