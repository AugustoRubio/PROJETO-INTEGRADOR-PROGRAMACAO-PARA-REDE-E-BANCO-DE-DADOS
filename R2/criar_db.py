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
            #Tabela de usuários: id (chave primária), usuário (texto não nulo e único) e senha (texto não nulo)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL
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

            #Deixamos um usuário admin padrão para facilitar o acesso inicial ao sistema
            #Antes de inserir o usuário admin, criptografamos a senha usando o algoritmo SHA-256
            admin_password = hashlib.sha256("teste".encode()).hexdigest()
            #Aqui executamos o cursor para inserir dentro da tabela usuarios o usuário admin e a senha criptografada
            #Usamos o comando INSERT OR IGNORE para evitar que o usuário admin seja inserido mais de uma vez
            cursor.execute('''
                INSERT OR IGNORE INTO usuarios (usuario, senha) VALUES (?, ?)
            ''', ("admin", admin_password))
            
            print("Tabelas criadas com sucesso e usuário admin inserido.")
    except sqlite3.Error as e:
        print(e)
#Fim da função criar_tabelas

#Função para mostrar a estrutura das tabelas no banco de dados após a criação
def mostrar_estrutura_tabelas(conn):
    try:
        with conn:
            cursor = conn.cursor()
            
            #Aqui mostramos a estrutura da tabela de usuários usando o comando PRAGMA para retornar informações sobre a tabela
            cursor.execute("PRAGMA table_info(usuarios)")
            #Aqui guardamos as informações da tabela de usuários na variável usuarios_info usando o método fetchall do cursor
            #O método fetchall retorna uma lista com todas as linhas do resultado da consulta
            usuarios_info = cursor.fetchall()
            print("Estrutura da tabela 'usuarios':")
            #Aqui percorremos a lista de informações da tabela de usuários e exibimos na tela
            for column in usuarios_info:
                print(column)
            
            #Aqui mostramos a estrutura da tabela de scanner usando o comando PRAGMA para retornar informações sobre a tabela
            #Usando o mesmo mecanismo anterior
            cursor.execute("PRAGMA table_info(scanner)")
            scanner_info = cursor.fetchall()
            print("\nEstrutura da tabela 'scanner':")
            for column in scanner_info:
                print(column)
    except sqlite3.Error as e:
        print(e)
#Fim da função mostrar_estrutura_tabelas

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