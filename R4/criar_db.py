import mysql.connector
import os
import hashlib
import configparser

class GerenciadorBancoDados:
    def __init__(self, host, user, password, database, port):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None

    def criar_conexao(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            print(f"Conectado ao banco de dados MySQL: {self.database}")
        except mysql.connector.Error as e:
            print(e)
            self.conn = None

    def criar_tabelas(self):
        if self.conn is None:
            print("Erro! Não há conexão com o banco de dados.")
            return

        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(255) NOT NULL UNIQUE,
                    senha VARCHAR(255) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    nome_completo VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    is_admin TINYINT NOT NULL DEFAULT 0,
                    ultimo_login TIMESTAMP NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scanner (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hostname VARCHAR(255),
                    mac_address VARCHAR(255),
                    ip VARCHAR(255),
                    portas TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config_programa (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    logo_principal VARCHAR(255),
                    logo_rodape VARCHAR(255),
                    fonte_principal VARCHAR(255),
                    tamanho_fonte INT,
                    modo_global TINYINT NOT NULL DEFAULT 0
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferencias (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fonte_preferida VARCHAR(255) NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pc_salvo (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    ip VARCHAR(255) NOT NULL,
                    porta VARCHAR(255) NOT NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')

            script_dir = os.path.dirname(os.path.abspath(__file__))

            apoio_dir = os.path.join(script_dir, "apoio")
            if not os.path.exists(apoio_dir):
                os.makedirs(apoio_dir)

            cursor.execute('''
                INSERT INTO config_programa (data, logo_principal, logo_rodape, fonte_principal, tamanho_fonte, modo_global) VALUES (NOW(), %s, %s, %s, %s, %s)
            ''', (
                os.path.join(apoio_dir, "LOGO_R3.png"),
                os.path.join(apoio_dir, "LOGO_R6.png"),
                "Arial",
                18,
                0  # Valor padrão para modo_global
            ))
            print("Configuração padrão inserida com sucesso.")

            cursor.execute('''
                INSERT INTO preferencias (fonte_preferida) VALUES (%s)
            ''', ("Arial",))
            print("Preferências padrão inseridas com sucesso.")

            admin_password = hashlib.sha256("admin".encode()).hexdigest()

            cursor.execute('SELECT * FROM usuarios WHERE usuario = %s', ("admin",))
            admin_exists = cursor.fetchone()

            if not admin_exists:
                cursor.execute('''
                    INSERT INTO usuarios (usuario, senha, data_criacao, nome_completo, email, is_admin) VALUES (%s, %s, NOW(), %s, %s, %s)
                ''', ("admin", admin_password, "Administrador do Sistema", "admin@example.com", 1))
                print("Usuário admin inserido com sucesso.")
            else:
                print("Usuário admin já existe.")

            self.conn.commit()
            print("Tabelas criadas com sucesso.")
        except mysql.connector.Error as e:
            print(e)

    def mostrar_estrutura_tabelas(self):
        if self.conn is None:
            print("Erro! Não há conexão com o banco de dados.")
            return

        try:
            cursor = self.conn.cursor()

            cursor.execute("DESCRIBE usuarios")
            usuarios_info = cursor.fetchall()
            print("Estrutura da tabela 'usuarios':")
            for column in usuarios_info:
                print(column)

            cursor.execute("DESCRIBE scanner")
            scanner_info = cursor.fetchall()
            print("\nEstrutura da tabela 'scanner':")
            for column in scanner_info:
                print(column)

            cursor.execute("DESCRIBE config_programa")
            config_programa_info = cursor.fetchall()
            print("\nEstrutura da tabela 'config_programa':")
            for column in config_programa_info:
                print(column)

            cursor.execute("DESCRIBE preferencias")
            preferencias_info = cursor.fetchall()
            print("\nEstrutura da tabela 'preferencias':")
            for column in preferencias_info:
                print(column)

            cursor.execute("DESCRIBE pc_salvo")
            pc_salvo_info = cursor.fetchall()
            print("\nEstrutura da tabela 'pc_salvo':")
            for column in pc_salvo_info:
                print(column)
        except mysql.connector.Error as e:
            print(e)

    def fechar_conexao(self):
        if self.conn:
            self.conn.close()
            print("Conexão com o banco de dados fechada.")

def principal():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    config.read(config_path)

    host = config['mysql']['host']
    user = config['mysql']['user']
    password = config['mysql']['password']
    database = config['mysql']['database']
    port = config['mysql'].getint('port')

    gerenciador_bd = GerenciadorBancoDados(host, user, password, database, port)
    gerenciador_bd.criar_conexao()
    if gerenciador_bd.conn is not None:
        gerenciador_bd.criar_tabelas()
        gerenciador_bd.mostrar_estrutura_tabelas()
        gerenciador_bd.fechar_conexao()
    else:
        print("Erro! Não foi possível criar a conexão com o banco de dados.")

if __name__ == '__main__':
    principal()
