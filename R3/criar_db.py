#Esse código é responsável por criar o banco de dados SQLite e as tabelas necessárias para o funcionamento do sistema.
#O banco de dados é criado no mesmo diretório do script e o arquivo é chamado de banco.db.
#Bibliotecas necessárias para a execução do código:
#sqlite3: para a conexão com o banco de dados SQLite.
import sqlite3
#os: para manipulação de arquivos e diretórios.
import os
#hashlib: para criptografar a senha do usuário.
import hashlib

#Função para criar a conexão com o banco de dados
def criar_conexao(arquivo_db):
    #Tenta criar a conexão com o banco de dados SQLite
    try:
        #Coloca dentro da variável conn a conexão com o banco de dados SQLite
        conn = sqlite3.connect(arquivo_db)
        print(f"Conectado ao banco de dados SQLite: {arquivo_db}")
        return conn
    #Caso ocorra algum erro, ele será exibido na tela
    except sqlite3.Error as e:
        print(e)
        return None
#Fim da função criar_conexao

#Função para criar as tabelas no banco de dados
def criar_tabelas(conn):
    #Tenta criar as tabelas no banco de dados SQLite
    try:
        #Usamos o with para garantir que a conexão com o banco de dados seja fechada ao final do bloco
        #Usando a variável conn, criamos um cursor para executar comandos SQL
        with conn:
            cursor = conn.cursor()
            
            #Chamamos o método execute do cursor para criar a tabela de usuários
            #Caso a tabela usuarios já exista, ela não será criada novamente
            #Table de usuários: id (chave primária), usuario (texto não nulo e único), senha (texto não nulo), data_criacao (texto não nulo), nome_completo (texto não nulo), email (texto não nulo), is_admin (inteiro não nulo com valor padrão 0) e ultimo_login (texto)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,
                    data_criacao TEXT NOT NULL,
                    nome_completo TEXT NOT NULL,
                    email TEXT NOT NULL,
                    is_admin INTEGER NOT NULL DEFAULT 0,
                    ultimo_login TEXT
                )
            ''')
            #Fim da criação da tabela de usuários

            #Chamamos o método execute do cursor para criar a tabela de scanner
            #Caso a tabela scanner já exista, ela não será criada novamente
            #Tabela de scanner: id (chave primária), data (texto não nulo), hostname (texto), mac_address (texto), ip (texto) e portas (texto)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scanner (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    hostname TEXT,
                    mac_address TEXT,
                    ip TEXT,
                    portas TEXT
                )
            ''')
            #Fim da criação da tabela de scanner

            #Obtém o diretório do script e armazena na variável script_dir
            script_dir = os.path.dirname(os.path.abspath(__file__))

            #Chamamos o método execute do cursor para criar a tabela de config_programa
            #Caso a tabela config_programa já exista, ela não será criada novamente
            #Tabela de config_programa: id (chave primária), data (texto não nulo), logo_principal (texto), logo_rodape (texto), fonte_principal (texto), tamanho_fonte (inteiro)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config_programa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    logo_principal TEXT,
                    logo_rodape TEXT,
                    fonte_principal TEXT,
                    tamanho_fonte INTEGER
                )
            ''')
            #Fim da criação da tabela de config_programa

            # Verifica se o diretório "apoio" existe, caso contrário, cria o diretório
            apoio_dir = os.path.join(script_dir, "apoio")
            if not os.path.exists(apoio_dir):
                os.makedirs(apoio_dir)
            
            # Insere uma configuração padrão na tabela config_programa
            # Nessa configuração padrão, definimos o logo principal, logo do rodapé, fonte principal e tamanho da fonte
            cursor.execute('''
                INSERT INTO config_programa (data, logo_principal, logo_rodape, fonte_principal, tamanho_fonte) VALUES (datetime('now'), ?, ?, ?, ?)
            ''', (
                os.path.join(apoio_dir, "LOGO_R3.png"),
                os.path.join(apoio_dir, "LOGO_R6.png"),
                "Arial",  # Fonte compatível com PyQt
                18,  # Tamanho da fonte padrão
            ))
            print("Configuração padrão inserida com sucesso.")
            #Fim da inserção da configuração padrão

            #Deixamos um usuário admin padrão para facilitar o acesso inicial ao sistema
            #Antes de inserir o usuário admin, criptografamos a senha usando o algoritmo SHA-256
            admin_password = hashlib.sha256("teste".encode()).hexdigest()
            
            #Verifica se o usuário admin já existe
            cursor.execute('SELECT * FROM usuarios WHERE usuario = ?', ("admin",))
            admin_exists = cursor.fetchone()
            
            #Se o usuário admin não existir, insere o usuário admin
            if not admin_exists:
                #Precisamos selecionar os campos que serão inseridos na tabela de usuários
                #Inserimos o usuário admin com a senha criptografada, data de criação, nome completo, email e marcamos como administrador
                cursor.execute('''
                    INSERT INTO usuarios (usuario, senha, data_criacao, nome_completo, email, is_admin) VALUES (?, ?, datetime('now'), ?, ?, ?)
                ''', ("admin", admin_password, "Administrador do Sistema", "admin@example.com", 1))
                print("Usuário admin inserido com sucesso.")
            else:
                print("Usuário admin já existe.")
            
            print("Tabelas criadas com sucesso.")
    except sqlite3.Error as e:
        print(e)
#Fim da função criar_tabelas

#Função para mostrar a estrutura das tabelas no banco de dados após a criação
def mostrar_estrutura_tabelas(conn):
    try:
        with conn:
            cursor = conn.cursor()
            
            # Mostra a estrutura da tabela de usuários
            cursor.execute("PRAGMA table_info(usuarios)")
            usuarios_info = cursor.fetchall()
            print("Estrutura da tabela 'usuarios':")
            for column in usuarios_info:
                print(column)
            
            # Mostra a estrutura da tabela de scanner
            cursor.execute("PRAGMA table_info(scanner)")
            scanner_info = cursor.fetchall()
            print("\nEstrutura da tabela 'scanner':")
            for column in scanner_info:
                print(column)
            
            # Mostra a estrutura da tabela de config_programa
            cursor.execute("PRAGMA table_info(config_programa)")
            config_programa_info = cursor.fetchall()
            print("\nEstrutura da tabela 'config_programa':")
            for column in config_programa_info:
                print(column)
    except sqlite3.Error as e:
        print(e)
# Fim da função mostrar_estrutura_tabelas

#Função principal para chamar as funções de criação de banco de dados, tabelas e mostrar a estrutura das tabelas
def principal():
    #Obtém o diretório do script e armazena na variável script_dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #Cria o caminho completo do arquivo do banco de dados
    database = os.path.join(script_dir, "banco.db")
    
    #Verifica se o arquivo do banco de dados já existe e remove para criar um novo
    if os.path.exists(database):
        os.remove(database)
        print(f"Arquivo {database} existente removido.")
    
    #Cria a conexão com o banco de dados
    conn = criar_conexao(database)
    #Verifica se a conexão foi criada com sucesso
    if conn is not None:
        #Cria as tabelas no banco de dados
        criar_tabelas(conn)
        
        #Mostra a estrutura das tabelas no banco de dados
        mostrar_estrutura_tabelas(conn)
        
        #Fecha a conexão com o banco de dados
        conn.close()
    #Caso a conexão não seja criada com sucesso, exibe uma mensagem de erro    
    else:
        print("Erro! Não foi possível criar a conexão com o banco de dados.")
#Fim da função principal

#Chama a função principal
if __name__ == '__main__':
    principal()

#Fim do código