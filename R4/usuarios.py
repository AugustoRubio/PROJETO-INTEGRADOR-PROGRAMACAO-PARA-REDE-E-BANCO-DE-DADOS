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

    def verificar_login(self, usuario, senha):
        if not usuario or not senha:
            raise ValueError("Por favor, preencha todos os campos.")

        try:
            with self._connect() as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT id, senha, ultimo_login FROM usuarios WHERE usuario = %s', (usuario,))
                resultado = cursor.fetchone()
        except mysql.connector.Error as e:
            raise ConnectionError(f"Erro ao verificar login: {e}")

        if resultado:
            usuario_id, senha_armazenada, ultimo_login = resultado
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()

            if senha_hash == senha_armazenada:
                if usuario_id == 1 and not ultimo_login:
                    return "alterar_senha"
                else:
                    self.registrar_login(usuario_id)
                    return "login_sucesso"
            else:
                raise ValueError("Senha incorreta.")
        else:
            raise ValueError("Usuário não encontrado.")

    def registrar_login(self, usuario_id):
        data_login = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self._connect() as conexao:
            cursor = conexao.cursor()
            cursor.execute('UPDATE usuarios SET ultimo_login = %s WHERE id = %s', (data_login, usuario_id))
            conexao.commit()

    def salvar_nova_senha(self, usuario, nova_senha, confirmar_senha):
        if not nova_senha or not confirmar_senha:
            raise ValueError("Todos os campos são obrigatórios.")

        if nova_senha != confirmar_senha:
            raise ValueError("As senhas não coincidem.")

        with self._connect() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT senha FROM usuarios WHERE usuario = %s', (usuario,))
            senha_atual_hash = cursor.fetchone()[0]
            nova_senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()

            if nova_senha_hash == senha_atual_hash:
                raise ValueError("A nova senha não pode ser igual à senha atual.")

            cursor.execute('UPDATE usuarios SET senha = %s, ultimo_login = %s WHERE usuario = %s', 
                           (nova_senha_hash, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), usuario))
            conexao.commit()
            self.registrar_login(usuario)

    def obter_usuario_logado(self, usuario):
        try:
            with self._connect() as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT id, usuario, is_admin FROM usuarios WHERE usuario = %s', (usuario,))
                resultado = cursor.fetchone()
                if resultado:
                    return {'id': resultado[0], 'usuario': resultado[1], 'is_admin': resultado[2]}
        except mysql.connector.Error as e:
            raise ConnectionError(f"Erro ao obter usuário logado: {e}")
        return None