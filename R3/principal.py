import sys
import sqlite3
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QDesktopWidget, QCheckBox
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QEvent
import os
try:
    from scanner_rede import RedeAtual
    from scanner_rede import ScannerRede as ScannerRedeExterno
except ImportError:
    class RedeAtual:
        def obter_rede_atual(self):
            rede_atual = RedeAtual()
            return rede_atual.obter_rede_atual()

# Define the ScannerRede class
class ScannerRede:
    def __init__(self, portas_selecionadas, escaneamento_rapido):
        self.portas_selecionadas = portas_selecionadas
        self.escaneamento_rapido = escaneamento_rapido

    def escanear(self):
        # Implement the network scanning logic here
        # For now, return a dummy result for testing
        return [("Host1", "00:11:22:33:44:55", "192.168.1.1", self.portas_selecionadas)]

class JanelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 800, 600)  # Define o tamanho da janela
        self.setWindowState(Qt.WindowMaximized)  # Permite que a janela seja maximizada

        # Buscar configuração do banco de dados
        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT logo_principal, logo_rodape, fonte_principal, tamanho_fonte FROM config_programa WHERE id = 1')
                configuracao = cursor.fetchone()
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar configuração do banco de dados: {e}")
            return

        if configuracao:
            logo_principal, logo_rodape, fonte_principal, tamanho_fonte = configuracao
        else:
            self.mostrar_erro("Configuração não encontrada no banco de dados.")
            return

        self.layout = QVBoxLayout()

        # Adicionar logo principal
        if logo_principal:
            self.label_logo_principal = QLabel(self)
            self.label_logo_principal.setAlignment(Qt.AlignCenter)
            if logo_principal.endswith('.gif'):
                self.movie_logo_principal = QMovie(logo_principal)
                self.label_logo_principal.setMovie(self.movie_logo_principal)
                self.movie_logo_principal.start()
            else:
                self.pixmap_logo_principal = QPixmap(logo_principal)
                self.label_logo_principal.setPixmap(self.pixmap_logo_principal.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.layout.addWidget(self.label_logo_principal)

        # Definir fonte
        if fonte_principal and tamanho_fonte:
            self.setFont(QFont(fonte_principal, tamanho_fonte))

        self.label_usuario = QLabel('Usuário:', self)
        self.label_usuario.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_usuario, alignment=Qt.AlignCenter)

        self.input_usuario = QLineEdit(self)
        self.input_usuario.setMaximumWidth(300)
        self.input_usuario.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.input_usuario, alignment=Qt.AlignCenter)
        self.input_usuario.setFocus()

        self.label_senha = QLabel('Senha:', self)
        self.label_senha.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_senha, alignment=Qt.AlignCenter)

        self.input_senha = QLineEdit(self)
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setMaximumWidth(300)
        self.input_senha.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.input_senha, alignment=Qt.AlignCenter)

        self.botao_login = QPushButton('Login', self)
        self.botao_login.setMaximumWidth(300)
        self.botao_login.setStyleSheet("margin-left: auto; margin-right: auto;")  # Centraliza o botão
        self.botao_login.clicked.connect(self.verificar_login)
        self.layout.addWidget(self.botao_login, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        self.input_senha.returnPressed.connect(self.verificar_login)

        # Adicionar logo do rodapé
        if logo_rodape:
            self.label_logo_rodape = QLabel(self)
            self.label_logo_rodape.setAlignment(Qt.AlignCenter)
            self.pixmap_logo_rodape = QPixmap(logo_rodape)
            self.label_logo_rodape.setPixmap(self.pixmap_logo_rodape.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.layout.addWidget(self.label_logo_rodape)

    def verificar_login(self):
        usuario = self.input_usuario.text()
        senha = self.input_senha.text()

        if not usuario or not senha:
            QMessageBox.warning(self, 'Erro', 'Por favor, preencha todos os campos.')
            return

        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT senha FROM usuarios WHERE usuario = ?', (usuario,))
                resultado = cursor.fetchone()
        except Exception as e:
            self.mostrar_erro(f"Erro ao verificar login: {e}")
            return

        if resultado:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if senha_hash == resultado[0]:
                self.abrir_janela_principal()
            else:
                QMessageBox.warning(self, 'Erro', 'Senha incorreta.')
        else:
            QMessageBox.warning(self, 'Erro', 'Usuário não encontrado.')

    def abrir_janela_principal(self):
        self.janela_principal = JanelaPrincipal()
        self.janela_principal.show()
        self.hide()  # Hide the login window after successful login

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()

#Começo da classe JanelaPrincipal
class JanelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Janela Principal')
        self.setGeometry(0, 0, 300, 200)
        self.center()

        layout = QVBoxLayout()

        self.botao_dashboard = QPushButton('DASHBOARD', self)
        layout.addWidget(self.botao_dashboard)

        self.botao_scanner_rede = QPushButton('Scanner de rede', self)
        self.botao_scanner_rede.clicked.connect(self.executar_scanner_rede)
        layout.addWidget(self.botao_scanner_rede)

        self.botao_config_usuarios = QPushButton('Configurações de usuários', self)
        layout.addWidget(self.botao_config_usuarios)

        self.botao_config_programa = QPushButton('Configuração do programa', self)
        layout.addWidget(self.botao_config_programa)

        self.botao_sair = QPushButton('SAIR', self)
        self.botao_sair.clicked.connect(self.confirmar_saida)
        layout.addWidget(self.botao_sair)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        self.confirmar_saida(event)

    def confirmar_saida(self, event=None):
        reply = QMessageBox.question(self, 'Confirmação', 'Tem certeza que deseja sair?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if event:
                event.accept()
            else:
                self.close()
        elif event:
            if event.type() == QEvent.Close:
                event.ignore()

    def executar_scanner_rede(self):
        self.janela_scanner_rede = JanelaScannerRede()
        self.janela_scanner_rede.show()
        self.hide()  # Use hide() instead of close() to prevent triggering closeEvent
#Fim da classe JanelaPrincipal

#Começo da classe JanelaScannerRede
class JanelaScannerRede(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Scanner de Rede')
        self.setGeometry(100, 100, 400, 300)
        self.center()

        layout = QVBoxLayout()

        self.botao_escanear_rede = QPushButton('Escanear a própria rede', self)
        self.botao_escanear_rede.clicked.connect(self.abrir_janela_opcoes_scanner)
        layout.addWidget(self.botao_escanear_rede)

        self.botao_ver_dados = QPushButton('Ver dados armazenados', self)
        self.botao_ver_dados.clicked.connect(self.ver_dados)
        layout.addWidget(self.botao_ver_dados)

        self.botao_voltar = QPushButton('Voltar ao menu principal', self)
        self.botao_voltar.clicked.connect(self.voltar_menu_principal)
        layout.addWidget(self.botao_voltar)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def abrir_janela_opcoes_scanner(self):
        self.janela_opcoes_scanner = JanelaOpcoesScanner()
        self.janela_opcoes_scanner.show()

    def ver_dados(self):
        try:
            caminho_db = os.path.join(os.path.dirname(__file__), 'banco.db')
            with sqlite3.connect(caminho_db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM scanner')
                dados = cursor.fetchall()

            dados_texto = "\n".join([
                f"Data: {d[0]}, Nome do Host: {d[1]}, MAC: {d[2]}, IP: {d[3]}, Portas: {d[4]}"
                for d in dados
            ])
            QMessageBox.information(self, 'Dados Armazenados', dados_texto)
        except Exception as e:
            self.mostrar_erro(f"Erro ao ver dados: {e}")

    def voltar_menu_principal(self):
        self.janela_principal = JanelaPrincipal()
        self.janela_principal.show()
        self.close()

    def closeEvent(self, event):
        self.voltar_menu_principal()

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()

class JanelaOpcoesScanner(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Opções de Scanner de Rede')
        self.setGeometry(100, 100, 400, 300)
        self.center()

        layout = QVBoxLayout()

        # Adicionar label para mostrar a rede atual do usuário
        self.label_rede_atual = QLabel('Rede Atual: Obtendo...', self)
        layout.addWidget(self.label_rede_atual)

        # Adicionar checkboxes para seleção de portas
        self.checkbox_escanear_rapido = QCheckBox('Escaneamento Rápido', self)
        self.checkbox_escanear_rapido.setChecked(True)
        layout.addWidget(self.checkbox_escanear_rapido)

        self.checkbox_porta_22 = QCheckBox('Porta 22 (SSH)', self)
        self.checkbox_porta_22.setChecked(False)
        layout.addWidget(self.checkbox_porta_22)

        self.checkbox_porta_80 = QCheckBox('Porta 80 (HTTP)', self)
        self.checkbox_porta_80.setChecked(False)
        layout.addWidget(self.checkbox_porta_80)

        self.checkbox_porta_443 = QCheckBox('Porta 443 (HTTPS)', self)
        self.checkbox_porta_443.setChecked(False)
        layout.addWidget(self.checkbox_porta_443)

        self.botao_escanear_rede = QPushButton('Escanear', self)
        self.botao_escanear_rede.clicked.connect(self.escanear_rede)
        layout.addWidget(self.botao_escanear_rede)

        self.setLayout(layout)

        # Atualizar a rede atual do usuário
        self.atualizar_rede_atual()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def atualizar_rede_atual(self):
        try:
            rede_atual = RedeAtual()
            rede = rede_atual.obter_rede_atual()

            if rede:
                self.label_rede_atual.setText(f"Rede Atual: {rede}")
            else:
                self.label_rede_atual.setText("Erro ao obter rede")
        except Exception as e:
            self.mostrar_erro(f"Erro ao atualizar rede atual: {e}")

    def escanear_rede(self):
        try:
            portas_selecionadas = []
            if self.checkbox_porta_22.isChecked():
                portas_selecionadas.append('22')
            if self.checkbox_porta_80.isChecked():
                portas_selecionadas.append('80')
            if self.checkbox_porta_443.isChecked():
                portas_selecionadas.append('443')

            escaneamento_rapido = self.checkbox_escanear_rapido.isChecked()

            # Importar e usar a classe ScannerRede do arquivo scanner_rede.py
            scanner = ScannerRedeExterno(portas_selecionadas, escaneamento_rapido)
            resultados = scanner.escanear()

            # Exibir os resultados em uma nova janela
            self.mostrar_resultados(resultados)
        except Exception as e:
            self.mostrar_erro(f"Erro ao escanear rede: {e}")

    def mostrar_resultados(self, resultados):
        self.janela_resultados = QWidget()
        self.janela_resultados.setWindowTitle('Resultados do Escaneamento')
        self.janela_resultados.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        texto_resultados = "\n".join([
            f"Nome do Host: {r[0]} | MAC: {r[1]} | IP: {r[2]} | Portas: {r[3]}"
            for r in resultados
        ])
        label_resultados = QLabel(texto_resultados)
        label_resultados.setAlignment(Qt.AlignTop)
        layout.addWidget(label_resultados)

        botao_fechar = QPushButton('Fechar', self.janela_resultados)
        botao_fechar.clicked.connect(self.janela_resultados.close)
        layout.addWidget(botao_fechar)

        self.janela_resultados.setLayout(layout)
        self.janela_resultados.show()

        # Check if the scan is completed and show a message
        if hasattr(self, 'escaneamento_concluido') and self.escaneamento_concluido:
            QMessageBox.information(self.janela_resultados, 'Escaneamento Concluído', 'O escaneamento foi concluído com sucesso!')

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        janela = JanelaLogin()
        janela.show()
        sys.exit(app.exec_())
    except Exception as e:
        app = QApplication(sys.argv)
        QMessageBox.critical(None, 'Erro Fatal', f"Ocorreu um erro fatal: {e}")
        app.exec_()
        sys.exit(1)
