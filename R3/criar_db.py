import sqlite3
import os
import hashlib

class GerenciadorBancoDados:
    def __init__(self, caminho_bd):
        self.caminho_bd = caminho_bd
        self.conn = None

    def criar_conexao(self):
        try:
            self.conn = sqlite3.connect(self.caminho_bd)
            print(f"Conectado ao banco de dados SQLite: {self.caminho_bd}")
        except sqlite3.Error as e:
            print(e)
            self.conn = None

    def criar_tabelas(self):
        if self.conn is None:
            print("Erro! Não há conexão com o banco de dados.")
            return

        try:
            with self.conn:
                cursor = self.conn.cursor()

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

                script_dir = os.path.dirname(os.path.abspath(__file__))

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

                apoio_dir = os.path.join(script_dir, "apoio")
                if not os.path.exists(apoio_dir):
                    os.makedirs(apoio_dir)

                cursor.execute('''
                    INSERT INTO config_programa (data, logo_principal, logo_rodape, fonte_principal, tamanho_fonte) VALUES (datetime('now'), ?, ?, ?, ?)
                ''', (
                    os.path.join(apoio_dir, "LOGO_R3.png"),
                    os.path.join(apoio_dir, "LOGO_R6.png"),
                    "Arial",
                    18,
                ))
                print("Configuração padrão inserida com sucesso.")

                admin_password = hashlib.sha256("teste".encode()).hexdigest()

                cursor.execute('SELECT * FROM usuarios WHERE usuario = ?', ("admin",))
                admin_exists = cursor.fetchone()

                if not admin_exists:
                    cursor.execute('''
                        INSERT INTO usuarios (usuario, senha, data_criacao, nome_completo, email, is_admin) VALUES (?, ?, datetime('now'), ?, ?, ?)
                    ''', ("admin", admin_password, "Administrador do Sistema", "admin@example.com", 1))
                    print("Usuário admin inserido com sucesso.")
                else:
                    print("Usuário admin já existe.")

                print("Tabelas criadas com sucesso.")
        except sqlite3.Error as e:
            print(e)

    def mostrar_estrutura_tabelas(self):
        if self.conn is None:
            print("Erro! Não há conexão com o banco de dados.")
            return

        try:
            with self.conn:
                cursor = self.conn.cursor()

                cursor.execute("PRAGMA table_info(usuarios)")
                usuarios_info = cursor.fetchall()
                print("Estrutura da tabela 'usuarios':")
                for column in usuarios_info:
                    print(column)

                cursor.execute("PRAGMA table_info(scanner)")
                scanner_info = cursor.fetchall()
                print("\nEstrutura da tabela 'scanner':")
                for column in scanner_info:
                    print(column)

                cursor.execute("PRAGMA table_info(config_programa)")
                config_programa_info = cursor.fetchall()
                print("\nEstrutura da tabela 'config_programa':")
                for column in config_programa_info:
                    print(column)
        except sqlite3.Error as e:
            print(e)

    def fechar_conexao(self):
        if self.conn:
            self.conn.close()
            print("Conexão com o banco de dados fechada.")

def principal():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    database = os.path.join(script_dir, "banco.db")

    if os.path.exists(database):
        os.remove(database)
        print(f"Arquivo {database} existente removido.")

    gerenciador_bd = GerenciadorBancoDados(database)
    gerenciador_bd.criar_conexao()
    if gerenciador_bd.conn is not None:
        gerenciador_bd.criar_tabelas()
        gerenciador_bd.mostrar_estrutura_tabelas()
        gerenciador_bd.fechar_conexao()
    else:
        print("Erro! Não foi possível criar a conexão com o banco de dados.")

if __name__ == '__main__':
    principal()
