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

    def criar_tabelas(self):
        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            ) as conn:
                cursor = conn.cursor()

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
                        fonte_padrao VARCHAR(255),
                        tamanho_fonte_padrao INT,
                        modo_global TINYINT NOT NULL DEFAULT 0
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

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS preferenciais_usuarios (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        usuario_id INT NOT NULL,
                        fonte_perso VARCHAR(255) NOT NULL,
                        tamanho_fonte_perso INT,
                        fonte_alterada TINYINT NOT NULL DEFAULT 0,
                        tamanho_fonte_alterado TINYINT NOT NULL DEFAULT 0,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                    )
                ''')

                script_dir = os.path.dirname(os.path.abspath(__file__))
                apoio_dir = os.path.join(script_dir, "apoio")
                if not os.path.exists(apoio_dir):
                    os.makedirs(apoio_dir)

                cursor.execute('SELECT COUNT(*) FROM config_programa WHERE id = 1')
                config_exists = cursor.fetchone()[0]

                if config_exists == 0:
                    cursor.execute('''
                        INSERT INTO config_programa (id, data, logo_principal, logo_rodape, fonte_padrao, tamanho_fonte_padrao, modo_global) 
                        VALUES (1, NOW(), %s, %s, %s, %s, %s)
                    ''', (
                        os.path.join(apoio_dir, "LOGO_R3.png"),
                        os.path.join(apoio_dir, "LOGO_R6.png"),
                        "Arial",
                        18,
                        0
                    ))
                    print("Configuração padrão inserida com sucesso.")
                else:
                    print("Configuração padrão já existe.")

                admin_password = hashlib.sha256("admin".encode()).hexdigest()

                cursor.execute('SELECT * FROM usuarios WHERE usuario = %s', ("admin",))
                admin_exists = cursor.fetchone()

                if not admin_exists:
                    cursor.execute('''
                        INSERT INTO usuarios (usuario, senha, data_criacao, nome_completo, email, is_admin) 
                        VALUES (%s, %s, NOW(), %s, %s, %s)
                    ''', ("admin", admin_password, "Administrador do Sistema", "admin@example.com", 1))
                    admin_id = cursor.lastrowid
                    cursor.execute('''
                        INSERT INTO preferenciais_usuarios (usuario_id, fonte_perso, tamanho_fonte_perso, fonte_alterada, tamanho_fonte_alterado) 
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (admin_id, "Arial", 18, 0, 0))
                    print("Usuário admin e preferências inseridos com sucesso.")
                else:
                    print("Usuário admin já existe.")

                conn.commit()
                print("Tabelas criadas com sucesso.")
        except mysql.connector.Error as e:
            print(e)

    def mostrar_estrutura_tabelas(self):
        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            ) as conn:
                cursor = conn.cursor()

                tabelas = ["usuarios", "scanner", "config_programa", "pc_salvo", "preferenciais_usuarios"]
                for tabela in tabelas:
                    cursor.execute(f"DESCRIBE {tabela}")
                    info = cursor.fetchall()
                    print(f"\nEstrutura da tabela '{tabela}':")
                    for column in info:
                        print(column)

                cursor.execute("SELECT id, data_criacao, ultimo_login FROM usuarios")
                usuarios = cursor.fetchall()
                print("\nDados da tabela 'usuarios':")
                for usuario in usuarios:
                    id, data_criacao, ultimo_login = usuario
                    data_criacao = data_criacao.strftime("%d/%m/%Y %H:%M:%S") if data_criacao else None
                    ultimo_login = ultimo_login.strftime("%d/%m/%Y %H:%M:%S") if ultimo_login else None
                    print(f"ID: {id}, Data Criação: {data_criacao}, Último Login: {ultimo_login}")

        except mysql.connector.Error as e:
            print(e)

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
    gerenciador_bd.criar_tabelas()
    gerenciador_bd.mostrar_estrutura_tabelas()

if __name__ == '__main__':
    principal()
