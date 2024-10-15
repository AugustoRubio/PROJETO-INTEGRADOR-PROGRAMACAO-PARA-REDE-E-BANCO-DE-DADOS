class Modo:
    def __init__(self):
        self.modo_atual = 'claro'

    def trocar_modo(self):
        if self.modo_atual == 'claro':
            self.modo_atual = 'escuro'
        else:
            self.modo_atual = 'claro'
        self.atualizar_switch()

    def atualizar_switch(self):
        if self.modo_atual == 'escuro':
            estilo = {
                "icone": 'apoio/sun-mode.png',
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
                "icone": 'apoio/night-mode.png',
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