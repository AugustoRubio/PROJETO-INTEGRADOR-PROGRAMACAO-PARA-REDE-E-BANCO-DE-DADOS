# CRIA A BASE DOS USUÁRIOS QUE IRÃO ACESSAR O SISTEMA.
# CRIA A BASE DE DADOS PARA ARMAZENAR OS DADOS DOS ESCANEAMENTOS.
# VERIFICA TAMBÉM SE A BASE EXISTE, SE NÃO EXISTIR, CRIA A BASE DE DADOS.
import sqlite3
import hashlib
import os

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT NOT NULL,
                        senha TEXT NOT NULL
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS escaneamentos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data TEXT NOT NULL,
                        hostname TEXT,
                        mac_address TEXT,
                        ip TEXT,
                        portas TEXT
                    )
                ''')
                conn.commit()
                print("Banco de dados criado com sucesso.")
                self.add_user('admin', 'teste')
        except sqlite3.Error as e:
            print(f"Erro ao criar o banco de dados: {e}")

    def check_structure(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(usuarios)")
                columns_usuarios = cursor.fetchall()
                expected_columns_usuarios = [
                    (0, 'id', 'INTEGER', 0, None, 1),
                    (1, 'usuario', 'TEXT', 1, None, 0),
                    (2, 'senha', 'TEXT', 1, None, 0)
                ]
                
                cursor.execute("PRAGMA table_info(escaneamentos)")
                columns_escaneamentos = cursor.fetchall()
                expected_columns_escaneamentos = [
                    (0, 'id', 'INTEGER', 0, None, 1),
                    (1, 'data', 'TEXT', 1, None, 0),
                    (2, 'hostname', 'TEXT', 0, None, 0),
                    (3, 'mac_address', 'TEXT', 0, None, 0),
                    (4, 'ip', 'TEXT', 0, None, 0),
                    (5, 'portas', 'TEXT', 0, None, 0)
                ]

                if columns_usuarios == expected_columns_usuarios and columns_escaneamentos == expected_columns_escaneamentos:
                    print("A estrutura do banco de dados está correta.")
                else:
                    print("A estrutura do banco de dados está incorreta. Criando banco de dados...")
                    self.create_database()
                    self.add_user('admin', 'teste')
        except sqlite3.Error as e:
            print(f"Erro ao verificar a estrutura do banco de dados: {e}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, usuario, senha):
        hashed_senha = self.hash_password(senha)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO usuarios (usuario, senha)
                    VALUES (?, ?)
                ''', (usuario, hashed_senha))
                conn.commit()
                print("Usuário adicionado com sucesso.")
        except sqlite3.Error as e:
            print(f"Erro ao adicionar usuário: {e}")

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), 'banco.db')
    db_manager = DatabaseManager(db_path)
    db_manager.create_database()
    db_manager.check_structure()

    # Display the structure of the database
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            print("\nEstrutura da tabela 'usuarios':")
            cursor.execute("PRAGMA table_info(usuarios)")
            for column in cursor.fetchall():
                print(column)

            print("\nEstrutura da tabela 'escaneamentos':")
            cursor.execute("PRAGMA table_info(escaneamentos)")
            for column in cursor.fetchall():
                print(column)
    except sqlite3.Error as e:
        print(f"Erro ao exibir a estrutura do banco de dados: {e}")