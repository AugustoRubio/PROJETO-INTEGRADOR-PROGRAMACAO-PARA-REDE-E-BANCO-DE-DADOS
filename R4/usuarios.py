import hashlib
import mysql.connector
from datetime import datetime

class ConfigUsuarios:
    def __init__(self, usuario_logado, host, user, password, database, port):
        self.usuario_logado = usuario_logado
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port

    def _connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )

    def adicionar_usuario(self, usuario, nome_completo, email, senha, is_admin):
        if not self.usuario_logado['is_admin']:
            raise PermissionError("Somente administradores podem adicionar usuários.")

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with self._connect() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO usuarios (usuario, senha, data_criacao, nome_completo, email, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (usuario, senha_hash, data_criacao, nome_completo, email, is_admin))
                conexao.commit()
                # Obter o ID do novo usuário
                usuario_id = cursor.lastrowid

                # Inserir as preferências padrão para o novo usuário
                cursor.execute('''
                    INSERT INTO preferenciais_usuarios (usuario_id, fonte_perso, tamanho_fonte_perso, fonte_alterada, tamanho_fonte_alterado, modo_tela)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (usuario_id, "Arial", 18, 0, 0, 0))
                conexao.commit()

    def remover_usuario(self, usuario_id):
        if not self.usuario_logado['is_admin']:
            raise PermissionError("Somente administradores podem remover usuários.")

        if usuario_id == 1:
            raise ValueError("O administrador padrão não pode ser removido.")

        if usuario_id == self.usuario_logado['id']:
            raise ValueError("Você não pode remover o usuário atualmente logado.")

        with self._connect() as conexao:
            cursor = conexao.cursor()
            # Remover das preferências do usuário
            cursor.execute('DELETE FROM preferenciais_usuarios WHERE usuario_id = %s', (usuario_id,))
            # Remover da tabela de usuários
            cursor.execute('DELETE FROM usuarios WHERE id = %s', (usuario_id,))
            conexao.commit()

    def listar_usuarios(self):
        with self._connect() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT id, usuario, nome_completo, email, is_admin FROM usuarios')
            return cursor.fetchall()

    def editar_usuario(self, usuario_id, usuario, nome_completo, email, is_admin):
        with self._connect() as conexao:
            cursor = conexao.cursor()
            cursor.execute('UPDATE usuarios SET usuario = %s, nome_completo = %s, email = %s, is_admin = %s WHERE id = %s', 
                           (usuario, nome_completo, email, is_admin, usuario_id))
            conexao.commit()

    def alterar_senha(self, usuario_id, nova_senha):
        senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()

        with self._connect() as conexao:
            cursor = conexao.cursor()
            cursor.execute('UPDATE usuarios SET senha = %s WHERE id = %s', (senha_hash, usuario_id))
            conexao.commit()

    def ver_informacoes_usuario(self, usuario_id):
        with self._connect() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT id, usuario, nome_completo, email, is_admin FROM usuarios WHERE id = %s', (usuario_id,))
            return cursor.fetchone()
