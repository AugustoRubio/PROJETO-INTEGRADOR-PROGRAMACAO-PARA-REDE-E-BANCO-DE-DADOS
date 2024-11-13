import subprocess
import nmap
import mysql.connector
from datetime import datetime
import socket
import ipaddress
import locale
import platform

# Define a localidade para PT-BR
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

# Inicio da classe ScannerRede
class ScannerRede:
    def __init__(self, host, user, password, database, port, portas_selecionadas=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.escaneamento_rapido = False
        self.portas_selecionadas = portas_selecionadas if portas_selecionadas else ['80', '22', '443']  # Default ports if none provided
        self.escaneamento_concluido = False

    def escanear(self):
        # Obtém o endereço IP e a máscara de sub-rede
        ip = socket.gethostbyname(socket.gethostname())
        mascara = ipaddress.IPv4Network(f"{ip}/24", strict=False).netmask
        rede = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)

        argumentos = []

        if self.escaneamento_rapido and not self.portas_selecionadas:
            argumentos.append('-T4 -F')  # Quick Scan
        if self.portas_selecionadas:
            portas = ','.join(self.portas_selecionadas)
            argumentos.append(f'-p {portas}')
        if self.escaneamento_rapido:
            argumentos.append('-T4')

        argumentos_str = ' '.join(argumentos)

        nm = nmap.PortScanner()
        try:
            nm.scan(hosts=str(rede), arguments=argumentos_str)

            resultados = []
            for host in nm.all_hosts():
                nome_host = nm[host].hostname() if self.escaneamento_rapido else 'N/A'
                endereco_mac = nm[host]['addresses'].get('mac', 'N/A')
                endereco_ip = nm[host]['addresses'].get('ipv4', 'N/A')
                portas_abertas = ', '.join([
                    f"{port}/ABERTA" if port.isdigit() and nm[host].has_tcp(int(port)) and 'tcp' in nm[host] and int(port) in nm[host]['tcp'] and nm[host]['tcp'][int(port)]['state'] == 'open' 
                    else f"{port}/FECHADA" 
                    for port in self.portas_selecionadas
                ])
                if not portas_abertas:
                    portas_abertas = 'N/D'
                resultados.append((nome_host, endereco_mac, endereco_ip, portas_abertas))

            self.salvar_resultados(resultados)

            self.escaneamento_concluido = True  # Marca o escaneamento como concluído

            # Retorna os resultados do escaneamento
            return resultados
        except Exception as e:
            print(f"Erro ao executar o comando nmap: {e}")
            self.escaneamento_concluido = False  # Marca o escaneamento como não concluído em caso de erro
            return None

    def salvar_resultados(self, resultados):
        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            ) as conexao:
                cursor = conexao.cursor()
                for resultado in resultados:
                    cursor.execute('''
                        INSERT INTO scanner (usuario_id, data, hostname, mac_address, ip, portas)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resultado[0], resultado[1], resultado[2], resultado[3]))
                conexao.commit()
                cursor.close()
        except mysql.connector.Error as e:
            print(f"Erro ao salvar resultados: {e}")
            
    def obter_informacoes(self):
        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            ) as conexao:
                with conexao.cursor(dictionary=True) as cursor:
                    cursor.execute('SELECT * FROM scanner')
                    resultados = cursor.fetchall()
                    return resultados
        except mysql.connector.Error as e:
            print(f"Erro ao obter informações: {e}")
            return None

class RedeAtual:
    def __init__(self):
        pass

    def obter_rede_atual(self):
        try:
            # Obtém o endereço IP e a máscara de sub-rede
            ip = socket.gethostbyname(socket.gethostname())
            mascara = ipaddress.IPv4Network(f"{ip}/24", strict=False).netmask
            rede = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)
            return str(rede)
        except Exception as e:
            print(f"Erro ao obter a rede atual: {e}")
            return None
# Fim da classe RedeAtual

class PingIP:
    def __init__(self, ip):
        self.ip = ip

    def ping(self):
        try:
            # Define o comando de ping baseado no sistema operacional
            if platform.system().lower() == 'windows':
                command = ['ping', '-n', '3', '-w', '1000', self.ip]
            else:
                command = ['ping', '-c', '3', '-W', '1', self.ip]

            output = subprocess.run(command, capture_output=True, text=True)

            # Verifica a quantidade de pacotes recebidos
            if output.returncode == 0:
                resultado = 1  # Ping bem-sucedido
            else:
                resultado = 0  # Ping falhou
        except Exception as e:
            print(f"Erro ao executar o comando ping: {e}")
            resultado = 0  # Erro ao executar o comando ping
        
        return resultado


class CarregarResultadosCalendario:
    def __init__(self, host, user, password, database, port, data_selecionada):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.data_selecionada = data_selecionada

    def carregar_resultados(self):
        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            ) as conexao:
                cursor = conexao.cursor()
                cursor.execute('SELECT data, hostname, mac_address, ip, portas FROM scanner WHERE DATE(data) = %s', (datetime.strptime(self.data_selecionada, '%d/%m/%Y').date(),))
                resultados = cursor.fetchall()

                if not resultados:
                    return "Nenhuma informação encontrada para a data selecionada."

                resultados_formatados = []
                for resultado in resultados:
                    resultados_formatados.append({
                        'data': resultado[0],
                        'hostname': resultado[1],
                        'mac_address': resultado[2],
                        'ip': resultado[3],
                        'portas': resultado[4]
                    })
                return resultados_formatados
        except mysql.connector.Error as e:
            return f"Erro ao buscar informações: {e}"