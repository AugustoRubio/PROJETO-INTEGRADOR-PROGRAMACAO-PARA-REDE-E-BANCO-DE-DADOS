import hashlib
import sqlite3
from datetime import datetime

#Inicio da classe ConfigUsuarios
class ConfigUsuarios:
    def __init__(self, usuario_logado):
        self.usuario_logado = usuario_logado

    def adicionar_usuario(self, usuario, nome_completo, email, senha, is_admin):
        if not self.usuario_logado['is_admin']:
            raise PermissionError("Somente administradores podem adicionar usuários.")

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with sqlite3.connect('banco.db') as conexao:
            cursor = conexao.cursor()
            cursor.execute('''
                INSERT INTO usuarios (usuario, senha, data_criacao, nome_completo, email, is_admin)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (usuario, senha_hash, data_criacao, nome_completo, email, is_admin))
            conexao.commit()

    def remover_usuario(self, usuario_id):
        if not self.usuario_logado['is_admin']:
            raise PermissionError("Somente administradores podem remover usuários.")

        if usuario_id == 1:
            raise ValueError("O administrador padrão não pode ser removido.")

        if usuario_id == self.usuario_logado['id']:
            raise ValueError("Você não pode remover o usuário atualmente logado.")

        with sqlite3.connect('banco.db') as conexao:
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
            conexao.commit()

    def listar_usuarios(self):
        with sqlite3.connect('banco.db') as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT id, usuario, nome_completo, email, is_admin FROM usuarios')
            return cursor.fetchall()

    def editar_usuario(self, usuario_id, usuario, nome_completo, email, is_admin):
        with sqlite3.connect('banco.db') as conexao:
            cursor = conexao.cursor()
            cursor.execute('UPDATE usuarios SET usuario = ?, nome_completo = ?, email = ?, is_admin = ? WHERE id = ?', 
                           (usuario, nome_completo, email, is_admin, usuario_id))
            conexao.commit()

    def alterar_senha(self, usuario_id, nova_senha):
        senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()

        with sqlite3.connect('banco.db') as conexao:
            cursor = conexao.cursor()
            cursor.execute('UPDATE usuarios SET senha = ? WHERE id = ?', (senha_hash, usuario_id))
            conexao.commit()

    def ver_informacoes_usuario(self, usuario_id):
        with sqlite3.connect('banco.db') as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT id, usuario, nome_completo, email, is_admin FROM usuarios WHERE id = ?', (usuario_id,))
            return cursor.fetchone()
#Fim da classe ConfigUsuarios
