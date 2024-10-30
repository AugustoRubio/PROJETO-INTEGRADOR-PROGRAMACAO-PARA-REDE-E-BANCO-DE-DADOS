import configparser
import os

import mysql.connector

class Modo:
    def __init__(self):
        self.modo_atual = 'claro'
        self.config = self.carregar_configuracao()
        self.icone_modo_escuro = self.config['icone_modo_escuro']
        self.icone_modo_claro = self.config['icone_modo_claro']

    def carregar_configuracao(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        config.read(config_path)

        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        database = config['mysql']['database']
        port = config['mysql'].getint('port')

        try:
            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            ) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT icone_modo_escuro, icone_modo_claro FROM config_programa WHERE id = 1')
                config_data = cursor.fetchone()
                return config_data
        except mysql.connector.Error as e:
            print(e)
            return None

    def trocar_modo(self):
        if self.modo_atual == 'claro':
            self.modo_atual = 'escuro'
        else:
            self.modo_atual = 'claro'
        self.atualizar_switch()

    def atualizar_switch(self):
        if self.modo_atual == 'escuro':
            estilo = {
                "icone": self.icone_modo_escuro,
                "botao": {
                    "background-color": "#555555",
                    "color": "#FFFFFF",
                    "border": "2px solid #FFFFFF",
                    "border-radius": "15px",
                    "padding": "5px",
                    "text-align": "right",
                    "padding-right": "30px"
                },
                "botao_checked": {
                    "background-color": "#2E2E2E",
                    "color": "#FFFFFF",
                    "text-align": "right",
                    "padding-right": "30px"
                },
                "widget": {
                    "background-color": "#2E2E2E",
                    "color": "#FFFFFF",
                    "font-family": "fonte_principal",
                    "font-size": "tamanho_fonte"
                },
                "line_edit": {
                    "background-color": "#555555",
                    "color": "#FFFFFF"
                },
                "label": {
                    "color": "#FFFFFF"
                }
            }
        else:
            estilo = {
                "icone": self.icone_modo_claro,
                "botao": {
                    "background-color": "#DDDDDD",
                    "color": "#000000",
                    "border": "2px solid #000000",
                    "border-radius": "15px",
                    "padding": "5px",
                    "text-align": "left",
                    "padding-left": "30px"
                },
                "botao_checked": {
                    "background-color": "#FFFFFF",
                    "color": "#000000",
                    "text-align": "left",
                    "padding-left": "30px"
                },
                "widget": {
                    "background-color": "#FFFFFF",
                    "color": "#000000",
                    "font-family": "fonte_principal",
                    "font-size": "tamanho_fonte"
                },
                "line_edit": {
                    "background-color": "#FFFFFF",
                    "color": "#000000"
                },
                "label": {
                    "color": "#000000"
                }
            }
        return estilo