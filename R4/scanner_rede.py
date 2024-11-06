import subprocess
import nmap
import mysql.connector
from datetime import datetime
import socket
import ipaddress
import locale

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
        conexao = None
        try:
            conexao = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            cursor = conexao.cursor()
            for resultado in resultados:
                cursor.execute('''
                    INSERT INTO scanner (data, hostname, mac_address, ip, portas)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resultado[0], resultado[1], resultado[2], resultado[3]))
            conexao.commit()
            cursor.close()
        except mysql.connector.Error as e:
            print(f"Erro ao salvar resultados: {e}")
        finally:
            if conexao:
                conexao.close()
            
    def obter_informacoes(self):
        try:
            conexao = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            cursor = conexao.cursor(dictionary=True)
            cursor.execute('SELECT * FROM scanner')
            resultados = cursor.fetchall()
            cursor.close()
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
            # Executa o comando ping
            num_pacotes = 2  # Número de pacotes a serem enviados
            output = subprocess.run(['ping', '-n', str(num_pacotes), self.ip], capture_output=True, text=True)

            # Verifica a quantidade de pacotes recebidos
            for line in output.stdout.splitlines():
                if "Received =" in line:
                    received_packets = int(line.split("Received = ")[1].split(",")[0])
                    return received_packets > 0
            return False
        except Exception as e:
            print(f"Erro ao executar o comando ping: {e}")
            return False
