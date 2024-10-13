import subprocess
import tkinter as tk
import nmap
import sqlite3
from datetime import datetime
import socket
import ipaddress
import psutil
import os

#Inicio da classe ScannerRede
class ScannerRede:
    def __init__(self, portas_selecionadas=None, escaneamento_rapido=True):
        self.portas_selecionadas = portas_selecionadas if portas_selecionadas else []
        self.escaneamento_rapido = escaneamento_rapido
        self.escaneamento_concluido = False  # Variável para indicar se o escaneamento foi concluído

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
                if self.escaneamento_rapido and not self.portas_selecionadas:
                    resultados.append((nome_host, endereco_mac, endereco_ip, 'N/A'))
                else:
                    portas_abertas = ', '.join([f"{port}/ABERTA" if port.isdigit() and nm[host].has_tcp(int(port)) and nm[host]['tcp'][int(port)]['state'] == 'open' else f"{port}/FECHADA" for port in self.portas_selecionadas if port]) or 'N/D'
                    resultados.append((nome_host, endereco_mac, endereco_ip, portas_abertas))

            # Guarda os resultados relevantes no banco de dados
            caminho_db = os.path.join(os.path.dirname(__file__), 'banco.db')
            with sqlite3.connect(caminho_db) as conn:
                cursor = conn.cursor()
                for resultado in resultados:
                    cursor.execute('''
                        INSERT INTO scanner (data, hostname, mac_address, ip, portas)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (datetime.now().strftime('%d/%m/%Y %H:%M:%S'), resultado[0], resultado[1], resultado[2], resultado[3]))
                conn.commit()

            self.escaneamento_concluido = True  # Marca o escaneamento como concluído

            # Retorna os resultados do escaneamento
            return resultados
        except Exception as e:
            print(f"Erro ao executar o comando nmap: {e}")
            self.escaneamento_concluido = False  # Marca o escaneamento como não concluído em caso de erro
            return None
#Fim da classe ScannerRede

#Inicio da classe mostra a rede atual
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
#Fim da classe RedeAtual