import mysql.connector
import configparser

#Inicio da classe InserirConfiguracao
class InserirConfiguracao:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mysql_config = config['mysql']
        self.connection_params = {
            'host': mysql_config['host'],
            'user': mysql_config['user'],
            'password': mysql_config['password'],
            'database': mysql_config['database'],
            'port': int(mysql_config['port']),
        }

    def inserir_configuracao(self, data, logo_principal, logo_rodape, fonte_principal, tamanho_fonte):
        with mysql.connector.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO config_programa (data, logo_principal, logo_rodape, fonte_principal, tamanho_fonte)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (data, logo_principal, logo_rodape, fonte_principal, tamanho_fonte))
                conn.commit()
#Fim da classe InserirConfiguracao

#Inicio da classe AtualizarConfiguracao
class AtualizarConfiguracao:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mysql_config = config['mysql']
        self.connection_params = {
            'host': mysql_config['host'],
            'user': mysql_config['user'],
            'password': mysql_config['password'],
            'database': mysql_config['database'],
            'port': int(mysql_config['port']),
        }
#Fim da classe AtualizarConfiguracao

#Inicio da classe ObterConfiguracao
class ObterConfiguracao:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mysql_config = config['mysql']
        self.connection_params = {
            'host': mysql_config['host'],
            'user': mysql_config['user'],
            'password': mysql_config['password'],
            'database': mysql_config['database'],
            'port': int(mysql_config['port']),
        }

    def obter_configuracao(self, id_config):
        with mysql.connector.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM config_programa WHERE id = %s', (id_config,))
                result = cursor.fetchone()
                return result
#Fim da classe ObterConfiguracao

#Inicio da classe AtualizarConfiguracao
class CarregarPreferenciasUsuario:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mysql_config = config['mysql']
        self.connection_params = {
            'host': mysql_config['host'],
            'user': mysql_config['user'],
            'password': mysql_config['password'],
            'database': mysql_config['database'],
            'port': int(mysql_config['port']),
        }

    def carregar_preferencias_usuario(self, usuario_id):
        with mysql.connector.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT fonte_perso, tamanho_fonte_perso, fonte_alterada, tamanho_fonte_alterado, modo_tela
                    FROM preferenciais_usuarios
                    WHERE usuario_id = %s
                ''', (usuario_id,))
                result = cursor.fetchone()
                if result:
                    preferencias_usuario = {
                        'fonte_perso': result[0],
                        'tamanho_fonte_perso': result[1],
                        'fonte_alterada': result[2],
                        'tamanho_fonte_alterado': result[3],
                        'modo_tela': 'escuro' if result[4] == 1 else 'claro'
                    }
                    
                    cursor.execute('SELECT icone_modo_escuro, icone_modo_claro FROM config_programa WHERE id = 1')
                    config_result = cursor.fetchone()
                    if config_result:
                        preferencias_usuario['icone_modo_escuro'] = config_result[0]
                        preferencias_usuario['icone_modo_claro'] = config_result[1]
                    
                    return preferencias_usuario
                return None
#Fim da classe CarregarPreferenciasUsuario

#Inicio da classe AtualizarConfiguracao
class DeletarConfiguracao:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mysql_config = config['mysql']
        self.connection_params = {
            'host': mysql_config['host'],
            'user': mysql_config['user'],
            'password': mysql_config['password'],
            'database': mysql_config['database'],
            'port': int(mysql_config['port']),
        }

    def deletar_configuracao(self, id_config):
        with mysql.connector.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM config_programa WHERE id = %s', (id_config,))
                conn.commit()
#Fim da classe DeletarConfiguracao

#Inicio da classe AtualizarConfiguracao
class SalvarConfiguracoes:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mysql_config = config['mysql']
        self.connection_params = {
            'host': mysql_config['host'],
            'user': mysql_config['user'],
            'password': mysql_config['password'],
            'database': mysql_config['database'],
            'port': int(mysql_config['port']),
        }

    def salvar_configuracoes(self, caminho_logo_principal, caminho_logo_rodape, fonte_padrao, tamanho_fonte_padrao, modo_padrao, resetar_fonte, fonte_usuario, tamanho_fonte_usuario, usuario_logado):
        try:
            with mysql.connector.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    valores = []
                    campos = []
                    if caminho_logo_principal:
                        valores.append(caminho_logo_principal)
                        campos.append('logo_principal = %s')
                    if caminho_logo_rodape:
                        valores.append(caminho_logo_rodape)
                        campos.append('logo_rodape = %s')
                    if fonte_padrao:
                        campos.append('fonte_padrao = %s')
                        valores.append(fonte_padrao)
                    if tamanho_fonte_padrao:
                        campos.append('tamanho_fonte_padrao = %s')
                        valores.append(tamanho_fonte_padrao)
                    if modo_padrao is not None:
                        campos.append('modo_global = %s')
                        valores.append(modo_padrao)
                    if campos:
                        query = f"UPDATE config_programa SET {', '.join(campos)} WHERE id = 1"
                        cursor.execute(query, valores)
                    if resetar_fonte:
                        cursor.execute('SELECT fonte_padrao, tamanho_fonte_padrao FROM config_programa WHERE id = 1')
                        config = cursor.fetchone()
                        if config:
                            fonte_padrao, tamanho_fonte_padrao = config
                            cursor.execute('''
                                UPDATE preferenciais_usuarios
                                SET fonte_perso = %s, tamanho_fonte_perso = %s, fonte_alterada = 0, tamanho_fonte_alterado = 0
                                WHERE usuario_id = %s
                            ''', (fonte_padrao, tamanho_fonte_padrao, usuario_logado['id']))
                    else:
                        cursor.execute('''
                            UPDATE preferenciais_usuarios
                            SET fonte_perso = %s, tamanho_fonte_perso = %s, fonte_alterada = 1, tamanho_fonte_alterado = 1
                            WHERE usuario_id = %s
                        ''', (fonte_usuario, tamanho_fonte_usuario, usuario_logado['id']))
                    conn.commit()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao salvar configurações: {e}")

    def mostrar_erro(self, mensagem):
        print(mensagem)
    
    def salvar_preferencia_modo(self, modo_atual, usuario_logado):
        try:
            with mysql.connector.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    modo_tela = 1 if modo_atual == 'escuro' else 0
                    cursor.execute('UPDATE preferenciais_usuarios SET modo_tela = %s WHERE usuario_id = %s', (modo_tela, usuario_logado['id']))
                    conn.commit()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao salvar preferência de modo: {e}")

    def editar_preferencias_usuario(self, usuario_id, nova_fonte_perso, novo_tamanho_fonte_perso):
        try:
            with mysql.connector.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        UPDATE preferenciais_usuarios
                        SET fonte_perso = %s, tamanho_fonte_perso = %s, fonte_alterada = 1, tamanho_fonte_alterado = 1
                        WHERE usuario_id = %s
                    ''', (nova_fonte_perso, novo_tamanho_fonte_perso, usuario_id))
                    conn.commit()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao editar preferências do usuário: {e}")
#Fim da classe SalvarConfiguracoes

#Inicio da classe CarregarConfiguracoes
class CarregarConfiguracoes:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mysql_config = config['mysql']
        self.connection_params = {
            'host': mysql_config['host'],
            'user': mysql_config['user'],
            'password': mysql_config['password'],
            'database': mysql_config['database'],
            'port': int(mysql_config['port']),
        }

    def mostrar_erro(self, mensagem):
        print(mensagem)

    def carregar_configuracoes(self):
        try:
            with mysql.connector.connect(**self.connection_params) as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT logo_principal, logo_rodape, fonte_padrao, tamanho_fonte_padrao, modo_global FROM config_programa WHERE id = 1')
                configuracao = cursor.fetchone()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao buscar configuração do banco de dados: {e}")
            return

        if configuracao:
            self.logo_principal, self.logo_rodape, self.fonte_padrao, self.tamanho_fonte_padrao, modo_global = configuracao
            self.modo_atual = 'escuro' if modo_global == 1 else 'claro'
        else:
            self.mostrar_erro("Configuração não encontrada no banco de dados.")
#Fim da classe CarregarConfiguracoes