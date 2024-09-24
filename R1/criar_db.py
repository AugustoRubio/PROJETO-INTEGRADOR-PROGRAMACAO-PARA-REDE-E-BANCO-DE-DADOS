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
                columns = cursor.fetchall()
                expected_columns = [
                    (0, 'id', 'INTEGER', 0, None, 1),
                    (1, 'usuario', 'TEXT', 1, None, 0),
                    (2, 'senha', 'TEXT', 1, None, 0)
                ]
                if columns == expected_columns:
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
    db_path = os.path.join(os.path.dirname(__file__), 'usuarios.db')
    db_manager = DatabaseManager(db_path)
    db_manager.create_database()
    db_manager.check_structure()