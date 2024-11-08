import sqlite3
import os
from PyQt5.QtWidgets import QFileDialog, QApplication

class ConfiguracaoProgramaDB:
    def __init__(self, caminho_banco_dados, app):
        self.caminho_banco_dados = caminho_banco_dados
        self.app = app

    def inserir_configuracao(self, data, logo_principal, logo_rodape, fonte_principal, tamanho_fonte):
        with sqlite3.connect(self.caminho_banco_dados) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO config_programa (data, logo_principal, logo_rodape, fonte_principal, tamanho_fonte)
                VALUES (?, ?, ?, ?, ?)
            ''', (data, logo_principal, logo_rodape, fonte_principal, tamanho_fonte))
            conn.commit()

    def atualizar_configuracao(self, id_config, data=None, logo_principal=None, logo_rodape=None, fonte_principal=None, tamanho_fonte=None):
        def validar_e_salvar_logo(logo, nome_arquivo):
            if logo:
                extensao = os.path.splitext(logo)[1].lower()
                if extensao in ['.jpg', '.png']:
                    caminho_logo = os.path.join('apoio', nome_arquivo + extensao)
                    
                    # Remove existing files with the same base name
                    for file in os.listdir('apoio'):
                        if file.startswith(nome_arquivo) and file.endswith(('.jpg', '.png')):
                            os.remove(os.path.join('apoio', file))
                    
                    with open(logo, 'rb') as f_src:
                        with open(caminho_logo, 'wb') as f_dst:
                            f_dst.write(f_src.read())
                    return caminho_logo
                else:
                    raise ValueError("Extensão de arquivo inválida. Use apenas .jpg ou .png.")
            return None

        logo_principal_path = validar_e_salvar_logo(logo_principal, 'logo_principal')
        logo_rodape_path = validar_e_salvar_logo(logo_rodape, 'logo_rodape')

        with sqlite3.connect(self.caminho_banco_dados) as conn:
            cursor = conn.cursor()
            query = 'UPDATE config_programa SET '
            params = []
            if data:
                query += 'data = ?, '
                params.append(data)
            if logo_principal_path:
                query += 'logo_principal = ?, '
                params.append(logo_principal_path)
            if logo_rodape_path:
                query += 'logo_rodape = ?, '
                params.append(logo_rodape_path)
            if fonte_principal:
                query += 'fonte_principal = ?, '
                params.append(fonte_principal)
            if tamanho_fonte:
                query += 'tamanho_fonte = ?, '
                params.append(tamanho_fonte)
            query = query.rstrip(', ') + ' WHERE id = ?'
            params.append(id_config)
            cursor.execute(query, params)
            conn.commit()

    def obter_configuracao(self, id_config):
        with sqlite3.connect(self.caminho_banco_dados) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM config_programa WHERE id = ?', (id_config,))
            return cursor.fetchone()

    def deletar_configuracao(self, id_config):
        with sqlite3.connect(self.caminho_banco_dados) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM config_programa WHERE id = ?', (id_config,))
            conn.commit()

    def selecionar_imagem(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "Selecione uma imagem", "", "Imagens (*.jpg *.png)", options=options)
        if file_name:
            return file_name
        return None
    
    def salvar_configuracoes(self, usuario_logado, fonte_usuario, tamanho_fonte_usuario, logo_principal=None, logo_rodape=None, fonte_padrao=None, tamanho_fonte_padrao=None, modo_padrao=None, resetar_fonte=False):
        try:
            with sqlite3.connect(self.caminho_banco_dados) as conn:
                cursor = conn.cursor()
                if usuario_logado.get('is_admin'):
                    campos = []
                    valores = []
                    if logo_principal:
                        caminho_logo_principal = self.validar_e_salvar_logo(logo_principal, 'logo_principal')
                        campos.append('logo_principal = ?')
                        valores.append(caminho_logo_principal)
                    if logo_rodape:
                        caminho_logo_rodape = self.validar_e_salvar_logo(logo_rodape, 'logo_rodape')
                        campos.append('logo_rodape = ?')
                        valores.append(caminho_logo_rodape)
                    if fonte_padrao:
                        campos.append('fonte_padrao = ?')
                        valores.append(fonte_padrao)
                    if tamanho_fonte_padrao:
                        campos.append('tamanho_fonte_padrao = ?')
                        valores.append(tamanho_fonte_padrao)
                    if modo_padrao is not None:
                        campos.append('modo_global = ?')
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
                            SET fonte_perso = ?, tamanho_fonte_perso = ?, fonte_alterada = 0, tamanho_fonte_alterado = 0
                            WHERE usuario_id = ?
                        ''', (fonte_padrao, tamanho_fonte_padrao, usuario_logado['id']))
                else:
                    cursor.execute('''
                        UPDATE preferenciais_usuarios
                        SET fonte_perso = ?, tamanho_fonte_perso = ?, fonte_alterada = 1, tamanho_fonte_alterado = 1
                        WHERE usuario_id = ?
                    ''', (fonte_usuario, tamanho_fonte_usuario, usuario_logado['id']))
                conn.commit()
        except sqlite3.Error as e:
            pass  # Handle error accordingly

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    sys.exit(app.exec_())
