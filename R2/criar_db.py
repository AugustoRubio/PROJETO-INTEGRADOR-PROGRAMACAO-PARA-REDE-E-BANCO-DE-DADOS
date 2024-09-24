import sqlite3
import os
import hashlib

# Função para criar a conexão com o banco de dados
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Conectado ao banco de dados SQLite: {db_file}")
    except sqlite3.Error as e:
        print(e)
    return conn

# Função para criar as tabelas
def create_tables(conn):
    try:
        cursor = conn.cursor()
        
        # Criação da tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL
            )
        ''')
        
        # Criação da tabela de scanner de rede
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
        
        # Inserção do usuário admin com senha criptografada
        admin_password = hashlib.sha256("teste".encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO usuarios (usuario, senha) VALUES (?, ?)
        ''', ("admin", admin_password))
        
        conn.commit()
        print("Tabelas criadas com sucesso e usuário admin inserido.")
    except sqlite3.Error as e:
        print(e)

# Função para visualizar a estrutura das tabelas
def show_table_structure(conn):
    try:
        cursor = conn.cursor()
        
        # Estrutura da tabela de usuários
        cursor.execute("PRAGMA table_info(usuarios)")
        usuarios_info = cursor.fetchall()
        print("Estrutura da tabela 'usuarios':")
        for column in usuarios_info:
            print(column)
        
        # Estrutura da tabela de scanner de rede
        cursor.execute("PRAGMA table_info(scanner)")
        scanner_info = cursor.fetchall()
        print("\nEstrutura da tabela 'scanner':")
        for column in scanner_info:
            print(column)
    except sqlite3.Error as e:
        print(e)

def main():
    # Obtém o diretório do script atual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    database = os.path.join(script_dir, "banco.db")
    
    # Verifica se o arquivo do banco de dados já existe
    if os.path.exists(database):
        os.remove(database)
        print(f"Arquivo {database} existente removido.")
    
    # Cria a conexão com o banco de dados
    conn = create_connection(database)
    
    if conn is not None:
        # Cria as tabelas
        create_tables(conn)
        
        # Mostra a estrutura das tabelas
        show_table_structure(conn)
        
        # Fecha a conexão
        conn.close()
    else:
        print("Erro! Não foi possível criar a conexão com o banco de dados.")

if __name__ == '__main__':
    main()