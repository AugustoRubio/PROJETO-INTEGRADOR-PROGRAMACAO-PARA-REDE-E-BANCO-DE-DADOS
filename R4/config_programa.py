import mysql.connector
import os
from PyQt5.QtWidgets import QFileDialog, QApplication
import configparser

class ConfiguracaoProgramaDB:
    def __init__(self, app):
        self.app = app
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

    def atualizar_configuracao(self, id_config, data=None, logo_principal=None, logo_rodape=None, fonte_principal=None, tamanho_fonte=None):
        def validar_e_salvar_logo(logo, nome_arquivo):
            if logo:
                extensao = os.path.splitext(logo)[1].lower()
                if extensao in ['.jpg', '.png']:
                    caminho_logo = os.path.join('apoio', nome_arquivo + extensao)
                    for file in os.listdir('apoio'):
                        if file.startswith(nome_arquivo) and file.endswith(('.jpg', '.png')):
                            os.remove(os.path.join('apoio', file))
                    with open(logo, 'rb') as f_src, open(caminho_logo, 'wb') as f_dst:
                        f_dst.write(f_src.read())
                    return caminho_logo
                else:
                    raise ValueError("Extensão de arquivo inválida. Use apenas .jpg ou .png.")
            return None

        logo_principal_path = validar_e_salvar_logo(logo_principal, 'logo_principal')
        logo_rodape_path = validar_e_salvar_logo(logo_rodape, 'logo_rodape')

        with mysql.connector.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                query = 'UPDATE config_programa SET '
                params = []
                if data:
                    query += 'data = %s, '
                    params.append(data)
                if logo_principal_path:
                    query += 'logo_principal = %s, '
                    params.append(logo_principal_path)
                if logo_rodape_path:
                    query += 'logo_rodape = %s, '
                    params.append(logo_rodape_path)
                if fonte_principal:
                    query += 'fonte_principal = %s, '
                    params.append(fonte_principal)
                if tamanho_fonte:
                    query += 'tamanho_fonte = %s, '
                    params.append(tamanho_fonte)
                query = query.rstrip(', ') + ' WHERE id = %s'
                params.append(id_config)
                cursor.execute(query, params)
                conn.commit()

    def obter_configuracao(self, id_config):
        with mysql.connector.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM config_programa WHERE id = %s', (id_config,))
                result = cursor.fetchone()
                return result
            
    def carregar_preferencias_usuario(self, usuario_id):
        with mysql.connector.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT fonte_perso, tamanho_fonte_perso, fonte_alterada, tamanho_fonte_alterado
                    FROM preferenciais_usuarios
                    WHERE usuario_id = %s
                ''', (usuario_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'fonte_perso': result[0],
                        'tamanho_fonte_perso': result[1],
                        'fonte_alterada': result[2],
                        'tamanho_fonte_alterado': result[3]
                    }
                return None
                        
    def deletar_configuracao(self, id_config):
        with mysql.connector.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM config_programa WHERE id = %s', (id_config,))
                conn.commit()

    def selecionar_imagem(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "Selecione uma imagem", "", "Imagens (*.jpg *.png)", options=options)
        return file_name or None
    
    def salvar_configuracoes(self, usuario_logado, fonte_usuario, tamanho_fonte_usuario, logo_principal=None, logo_rodape=None, fonte_padrao=None, tamanho_fonte_padrao=None, modo_padrao=None, resetar_fonte=False):
        try:
            with mysql.connector.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    if usuario_logado.get('is_admin'):
                        campos = []
                        valores = []
                        if logo_principal:
                            caminho_logo_principal = self.validar_e_salvar_logo(logo_principal, 'logo_principal')
                            campos.append('logo_principal = %s')
                            valores.append(caminho_logo_principal)
                        if logo_rodape:
                            caminho_logo_rodape = self.validar_e_salvar_logo(logo_rodape, 'logo_rodape')
                            campos.append('logo_rodape = %s')
                            valores.append(caminho_logo_rodape)
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
        except mysql.connector.Error:
            pass
        
    def carregar_configuracoes(self):
        try:
            with mysql.connector.connect(
                host=self.connection_params['host'],
                user=self.connection_params['user'],
                password=self.connection_params['password'],
                database=self.connection_params['database'],
                port=self.connection_params['port']
            ) as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT logo_principal, logo_rodape, fonte_padrao, tamanho_fonte_padrao, modo_global FROM config_programa WHERE id = 1')
                configuracao = cursor.fetchone()
        except mysql.connector.Error as e:
            self.mostrar_erro(f"Erro ao buscar configuração do banco de dados: {e}")
            return

        if configuracao:
            self.logo_principal, self.logo_rodape, self.fonte_padrao, self.tamanho_fonte_padrao, self.modo_global = configuracao
            self.modo.modo_atual = 'escuro' if self.modo_global == 1 else 'claro'
        else:
            self.mostrar_erro("Configuração não encontrada no banco de dados.")
            return
        
    
    if __name__ == "__main__":
        import sys
        app = QApplication(sys.argv)
        sys.exit(app.exec_())
