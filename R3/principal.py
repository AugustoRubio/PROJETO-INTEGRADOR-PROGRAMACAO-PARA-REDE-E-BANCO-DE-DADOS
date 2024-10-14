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
            # Dummy implementation for RedeAtual
            return "Dummy Network"

from PyQt5.QtWidgets import QCalendarWidget
from datetime import datetime

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
        usuario_logado = self.obter_usuario_logado()
        if usuario_logado:
            self.janela_principal = JanelaPrincipal(usuario_logado)
            self.janela_principal.show()
            self.hide()  # Hide the login window after successful login
        else:
            self.mostrar_erro('Erro ao obter informações do usuário logado.')

    def obter_usuario_logado(self):
        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT id, usuario, is_admin FROM usuarios WHERE usuario = ?', (self.input_usuario.text(),))
                resultado = cursor.fetchone()
                if resultado:
                    return {'id': resultado[0], 'usuario': resultado[1], 'is_admin': resultado[2]}
        except Exception as e:
            self.mostrar_erro(f"Erro ao obter usuário logado: {e}")
        return None

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()

#Começo da classe JanelaPrincipal
class JanelaPrincipal(QWidget):
    def __init__(self, usuario_logado):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Janela Principal')
        self.setGeometry(0, 0, 300, 200)
        self.center()

        layout = QVBoxLayout()

        # Adicionar informações do usuário logado no canto superior esquerdo da janela
        self.label_usuario_logado = QLabel(f"Usuário: {self.usuario_logado['usuario']} ({'Admin' if self.usuario_logado['is_admin'] else 'Comum'})", self)
        self.label_usuario_logado.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_usuario_logado, alignment=Qt.AlignLeft)

        self.botao_dashboard = QPushButton('DASHBOARD', self)
        layout.addWidget(self.botao_dashboard)

        self.botao_scanner_rede = QPushButton('Scanner de rede', self)
        self.botao_scanner_rede.clicked.connect(self.executar_scanner_rede)
        layout.addWidget(self.botao_scanner_rede)

        self.botao_config_usuarios = QPushButton('Configurações de usuários', self)
        self.botao_config_usuarios.clicked.connect(self.JanelaConfigUsuarios)
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

    def JanelaConfigUsuarios(self):
        self.janela_config_usuarios = JanelaConfigUsuarios()
        self.janela_config_usuarios.show()
        self.hide()
#Fim da classe JanelaPrincipal

#Começo da classe JanelaScannerRede
class JanelaScannerRede(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

        self.janela_principal = JanelaPrincipal(self.usuario_logado)
        self.setWindowTitle('Scanner de Rede')
        self.setGeometry(100, 100, 400, 300)
        self.center()
    def closeEvent(self, event):
        event.accept()
        layout = QVBoxLayout()

        self.botao_escanear_rede = QPushButton('Escanear a própria rede', self)
        self.botao_escanear_rede.clicked.connect(self.abrir_janela_opcoes_scanner)
        layout.addWidget(self.botao_escanear_rede)

        self.botao_ver_dados = QPushButton('Ver dados armazenados', self)
        self.botao_ver_dados.clicked.connect(self.abrir_janela_ver_informacoes)
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

    def abrir_janela_ver_informacoes(self):
        self.janela_ver_informacoes = JanelaVerInformacoes()
        self.janela_ver_informacoes.show()

    def voltar_menu_principal(self):
        self.janela_principal = JanelaPrincipal()
        self.janela_principal.show()
        self.close()

    def closeEvent(self, event):
        self.voltar_menu_principal()

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()

#Inicio da classe JanelaOpcoesScanner
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
#Fim da classe JanelaOpcoesScanner

#Inicio da classe JanelaVerInformacoes
class JanelaVerInformacoes(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Informações Armazenadas')
        self.setGeometry(100, 100, 600, 400)
        self.center()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Selecione a data no calendário:', self)
        layout.addWidget(self.label_instrucoes)

        self.calendario = QCalendarWidget(self)
        self.calendario.setSelectedDate(datetime.now().date())
        self.calendario.clicked.connect(self.atualizar_data_selecionada)
        layout.addWidget(self.calendario)

        self.input_data = QLineEdit(self)
        self.input_data.setText(self.calendario.selectedDate().toString('dd/MM/yyyy'))
        self.input_data.setReadOnly(True)
        layout.addWidget(self.input_data)

        self.botao_ver_informacoes = QPushButton('Ver Informações Armazenadas', self)
        self.botao_ver_informacoes.clicked.connect(self.ver_informacoes_armazenadas)
        layout.addWidget(self.botao_ver_informacoes)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def atualizar_data_selecionada(self):
        data_selecionada = self.calendario.selectedDate().toString('dd/MM/yyyy')
        self.input_data.setText(data_selecionada)

    def ver_informacoes_armazenadas(self):
        data_selecionada = self.input_data.text()

        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT * FROM scanner WHERE data LIKE ?', (f'%{data_selecionada}%',))
                resultados = cursor.fetchall()

            if not resultados:
                self.mostrar_erro("Nenhuma informação encontrada para a data selecionada.")
                return

            self.janela_resultados = QWidget()
            self.janela_resultados.setWindowTitle('Informações Armazenadas')
            self.janela_resultados.setGeometry(100, 100, 600, 400)
            layout = QVBoxLayout()

            texto_resultados = "\n".join([
                f"ID: {r[0]} | Data: {r[1]} | Hostname: {r[2]} | MAC: {r[3]} | IP: {r[4]} | Portas: {r[5]}"
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
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar informações: {e}")

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
#Fim da classe JanelaVerInformacoes

# Inicio da classe JanelaConfigUsuarios
class JanelaConfigUsuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        self.setWindowTitle('Configurações de Usuários')
        self.setGeometry(100, 100, 600, 400)
        self.center()

        layout = QVBoxLayout()

        self.label_instrucoes = QLabel('Gerencie os usuários do sistema:', self)
        layout.addWidget(self.label_instrucoes, alignment=Qt.AlignTop)

        self.botao_adicionar_usuario = QPushButton('Adicionar Usuário', self)
        self.botao_adicionar_usuario.clicked.connect(self.adicionar_usuario)
        layout.addWidget(self.botao_adicionar_usuario, alignment=Qt.AlignTop)

        self.botao_remover_usuario = QPushButton('Remover Usuário', self)
        self.botao_remover_usuario.clicked.connect(self.remover_usuario)
        layout.addWidget(self.botao_remover_usuario, alignment=Qt.AlignTop)

        self.botao_editar_usuario = QPushButton('Editar Usuário', self)
        self.botao_editar_usuario.clicked.connect(self.editar_usuario)
        layout.addWidget(self.botao_editar_usuario, alignment=Qt.AlignTop)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def adicionar_usuario(self):
        # Implementar lógica para adicionar usuário
        QMessageBox.information(self, 'Adicionar Usuário', 'Funcionalidade de adicionar usuário ainda não implementada.')

    def remover_usuario(self):
        # Implementar lógica para remover usuário
        QMessageBox.information(self, 'Remover Usuário', 'Funcionalidade de remover usuário ainda não implementada.')

    def editar_usuario(self):
        usuario_logado = self.obter_usuario_logado()
        if not usuario_logado:
            self.mostrar_erro('Erro ao obter informações do usuário logado.')
            return

        if usuario_logado['is_admin']:
            self.editar_usuario_admin(usuario_logado)
        else:
            self.ver_informacoes_usuario(usuario_logado)

    def obter_usuario_logado(self):
        # Implementar lógica para obter o usuário logado
        # Esta função deve retornar um dicionário com as informações do usuário logado
        # Exemplo: {'id': 1, 'usuario': 'admin', 'is_admin': 1}
        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT id, usuario, is_admin FROM usuarios WHERE usuario = ?', (self.usuario_logado,))
                resultado = cursor.fetchone()
                if resultado:
                    return {'id': resultado[0], 'usuario': resultado[1], 'is_admin': resultado[2]}
        except Exception as e:
            self.mostrar_erro(f"Erro ao obter usuário logado: {e}")
        return None

    def editar_usuario_admin(self, usuario_logado):
        # Implementar lógica para editar informações de outros usuários
        # Excluir a possibilidade de editar as próprias informações e IDs
        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT id, usuario, nome_completo, email, is_admin FROM usuarios WHERE id != ?', (usuario_logado['id'],))
                usuarios = cursor.fetchall()

            if not usuarios:
                self.mostrar_erro("Nenhum outro usuário encontrado.")
                return

            self.janela_editar_usuario = QWidget()
            self.janela_editar_usuario.setWindowTitle('Editar Usuário')
            self.janela_editar_usuario.setGeometry(100, 100, 600, 400)
            layout = QVBoxLayout()

            for usuario in usuarios:
                label_usuario = QLabel(f"ID: {usuario[0]} | Usuário: {usuario[1]} | Nome: {usuario[2]} | Email: {usuario[3]} | Admin: {'Sim' if usuario[4] else 'Não'}")
                layout.addWidget(label_usuario)

                botao_editar = QPushButton('Editar', self.janela_editar_usuario)
                botao_editar.clicked.connect(lambda _, u=usuario: self.abrir_janela_edicao(u))
                layout.addWidget(botao_editar)

            botao_fechar = QPushButton('Fechar', self.janela_editar_usuario)
            botao_fechar.clicked.connect(self.janela_editar_usuario.close)
            layout.addWidget(botao_fechar)

            self.janela_editar_usuario.setLayout(layout)
            self.janela_editar_usuario.show()
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar usuários: {e}")

    def abrir_janela_edicao(self, usuario):
        self.janela_edicao = QWidget()
        self.janela_edicao.setWindowTitle('Editar Informações do Usuário')
        self.janela_edicao.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        self.input_nome_completo = QLineEdit(self.janela_edicao)
        self.input_nome_completo.setText(usuario[2])
        layout.addWidget(QLabel('Nome Completo:'))
        layout.addWidget(self.input_nome_completo)

        self.input_email = QLineEdit(self.janela_edicao)
        self.input_email.setText(usuario[3])
        layout.addWidget(QLabel('Email:'))
        layout.addWidget(self.input_email)

        self.checkbox_is_admin = QCheckBox('Administrador', self.janela_edicao)
        self.checkbox_is_admin.setChecked(usuario[4])
        layout.addWidget(self.checkbox_is_admin)

        botao_salvar = QPushButton('Salvar', self.janela_edicao)
        botao_salvar.clicked.connect(lambda: self.salvar_edicao_usuario(usuario[0]))
        layout.addWidget(botao_salvar)

        botao_cancelar = QPushButton('Cancelar', self.janela_edicao)
        botao_cancelar.clicked.connect(self.janela_edicao.close)
        layout.addWidget(botao_cancelar)

        self.janela_edicao.setLayout(layout)
        self.janela_edicao.show()

    def salvar_edicao_usuario(self, usuario_id):
        nome_completo = self.input_nome_completo.text()
        email = self.input_email.text()
        is_admin = 1 if self.checkbox_is_admin.isChecked() else 0

        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('UPDATE usuarios SET nome_completo = ?, email = ?, is_admin = ? WHERE id = ?', (nome_completo, email, is_admin, usuario_id))
                conexao.commit()
            QMessageBox.information(self, 'Sucesso', 'Informações do usuário atualizadas com sucesso.')
            self.janela_edicao.close()
            self.janela_editar_usuario.close()
        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar informações do usuário: {e}")

    def ver_informacoes_usuario(self, usuario_logado):
        try:
            with sqlite3.connect('banco.db') as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT id, usuario, nome_completo, email, is_admin FROM usuarios WHERE id = ?', (usuario_logado['id'],))
                usuario = cursor.fetchone()

            if not usuario:
                self.mostrar_erro("Usuário não encontrado.")
                return

            self.janela_ver_usuario = QWidget()
            self.janela_ver_usuario.setWindowTitle('Informações do Usuário')
            self.janela_ver_usuario.setGeometry(100, 100, 400, 300)
            layout = QVBoxLayout()

            label_usuario = QLabel(f"ID: {usuario[0]} | Usuário: {usuario[1]} | Nome: {usuario[2]} | Email: {usuario[3]} | Admin: {'Sim' if usuario[4] else 'Não'}")
            layout.addWidget(label_usuario)

            botao_fechar = QPushButton('Fechar', self.janela_ver_usuario)
            botao_fechar.clicked.connect(self.janela_ver_usuario.close)
            layout.addWidget(botao_fechar)

            self.janela_ver_usuario.setLayout(layout)
            self.janela_ver_usuario.show()
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar informações do usuário: {e}")

    def mostrar_erro(self, mensagem):
        QMessageBox.critical(self, 'Erro', mensagem)
        self.show()
# Fim da classe JanelaConfigUsuarios

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
