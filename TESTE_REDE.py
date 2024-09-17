# Criar um menu e manipular informações de um banco de dados com SQLite3
import sqlite3
import os
import nmap
from datetime import datetime
import time
from tqdm import tqdm
import socket
import ipaddress
import psutil

# Define a pasta da criação do arquivo a mesma do arquivo .py
pasta = os.path.dirname(__file__)
# Define qual o arquivo que vai usar e dentro da mesma pasta do .py
arquivo = os.path.join(pasta, "arq_rede.db")

# Define o caminho do executável do nmap
nmap_path = r"C:\Program Files (x86)\Nmap\nmap.exe"
if not os.path.exists(nmap_path):
    raise FileNotFoundError(f"Nmap executable not found at {nmap_path}")

# Configura o caminho do nmap para o nmap.PortScanner
nmap.PortScanner().nmap_executable = nmap_path

#Verifica se o arquivo do BANCO DE DADOS existe, se não existir cria o arquivo com os parametros padrão.
def verifica_arquivo(arquivo):
    if not os.path.exists(arquivo):
        cria_banco(arquivo)
    else:
        verifica_base_inicial(arquivo)

def cria_banco(arquivo):
    with sqlite3.connect(arquivo) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS escaneamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                hostname TEXT,
                mac_address TEXT,
                ip TEXT,
                porta_22 TEXT,
                porta_80 TEXT
            )
        ''')
        conn.commit()

#Verifica se o BANCO DE DADOS possui a estrutura inicial correta, se não tiver cria a estrutura.
def verifica_base_inicial(arquivo):
    with sqlite3.connect(arquivo) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='escaneamentos';")
        if not cursor.fetchone():
            cria_banco(arquivo)

#Usa o nmap para escanear a rede e retorna uma lista com os resultados
def escanear_rede(rede):
    nm = nmap.PortScanner()
    nm.scan(hosts=rede, arguments='-p 22,80', timeout=30)
    resultados = []
    hosts = nm.all_hosts()

    #Procura as informações de cada host e adiciona na lista de resultados    
    for host in tqdm(hosts, desc="Escaneando hosts", unit="host"):
        hostname = nm[host].hostname()
        mac_address = nm[host]['addresses'].get('mac', 'N/A')
        ip = nm[host]['addresses'].get('ipv4', 'N/A')
        porta_22 = 'open' if 22 in nm[host]['tcp'] and nm[host]['tcp'][22]['state'] == 'open' else 'closed'
        porta_80 = 'open' if 80 in nm[host]['tcp'] and nm[host]['tcp'][80]['state'] == 'open' else 'closed'
        resultados.append((hostname, mac_address, ip, porta_22, porta_80))
        time.sleep(0.1)  # Simulate some delay for progress bar visibility
    return resultados

#Salva os resultados no BANCO DE DADOS
def salvar_resultados(arquivo, resultados):
    data = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with sqlite3.connect(arquivo) as conn:
        cursor = conn.cursor()
        for resultado in resultados:
            cursor.execute('''
                INSERT INTO escaneamentos (data, hostname, mac_address, ip, porta_22, porta_80)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data, *resultado))
        conn.commit()

#Permite visualizar as informações do BANCO DE DADOS de acordo com a data
def visualizar_informacoes(arquivo, data):
    with sqlite3.connect(arquivo) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM escaneamentos WHERE data LIKE ?
        ''', (f'%{data}%',))
        resultados = cursor.fetchall()
        
        if resultados:
            print("-" * 80)
            print(f"{'ID':<5} | {'Data':<20} | {'Hostname':<15} | {'MAC Address':<17} | {'IP':<15} | {'Porta 22':<10} | {'Porta 80':<10}")
            print("-" * 80)
            for resultado in resultados:
                id, data, hostname, mac_address, ip, porta_22, porta_80 = resultado
                print(f"{id:<5} | {data:<20} | {hostname:<15} | {mac_address:<17} | {ip:<15} | {porta_22:<10} | {porta_80:<10}")
            print("-" * 80)
        else:
            print("Nenhum resultado encontrado para a data fornecida.")

#Função para obter dentro do menu a rede local atual do computador
def obter_rede_local():
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)
    netmask = None

    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip_local:
                netmask = addr.netmask
                break
        if netmask:
            break

    if not netmask:
        raise ValueError("Could not determine the netmask for the local IP address.")

    cidr = netmask_to_cidr(netmask)
    rede_local = f"{ip_local}/{cidr}"
    return rede_local

#Função para converter a máscara de rede para CIDR
def netmask_to_cidr(netmask):
    return sum(bin(int(x)).count('1') for x in netmask.split('.'))

#Menu principal
def menu():
    verifica_arquivo(arquivo)
    rede_sugerida = obter_rede_local()
    while True:
        try:
            print("1- Escanear a rede")
            print("2- Visualizar informações pela data")
            print("3- Sair")
            opcao = input("Escolha uma opção: ")
            if opcao == '1':
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"1- Usar a rede atual ({rede_sugerida})")
                print("2- Digitar outra rede")
                print("9- Voltar ao menu principal")
                sub_opcao = input("Escolha uma opção: ")
                if sub_opcao == '1':
                    rede = rede_sugerida
                elif sub_opcao == '2':
                    rede = input(f"Digite a rede que deseja escanear (ex: {rede_sugerida}): ")
                elif sub_opcao == '9':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                else:
                    print("Opção inválida. Retornando ao menu principal.")
                    continue
                resultados = escanear_rede(rede)
                salvar_resultados(arquivo, resultados)
                print("Escaneamento concluído e salvo no banco de dados.")
            elif opcao == '2':
                os.system('cls' if os.name == 'nt' else 'clear')
                data = input("Digite a data para visualizar (ex: 01/10/2023): ")
                if data == '9':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                visualizar_informacoes(arquivo, data)
            elif opcao == '3':
                print("Saindo...")
                break
            elif opcao == '9':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            else:
                print("Opção inválida. Tente novamente.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}. Retornando ao menu principal.")

if __name__ == "__main__":
    menu()

# Fim do código
