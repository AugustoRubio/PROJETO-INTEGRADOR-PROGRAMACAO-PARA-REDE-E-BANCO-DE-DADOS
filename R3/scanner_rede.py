import subprocess
import tkinter as tk
import nmap
import sqlite3
from datetime import datetime
import socket
import ipaddress
import psutil
import os

class ScannerRede:
    def __init__(self):
        pass

    def escanear(self):
        # Obtém o endereço IP e a máscara de sub-rede
        ip = socket.gethostbyname(socket.gethostname())
        mascara = ipaddress.IPv4Network(f"{ip}/24", strict=False).netmask
        rede = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)

        # Configurações de escaneamento
        escaneamento_rapido = True
        portas_selecionadas = ['22', '80', '443']  # Exemplo de portas selecionadas

        portas = ','.join(portas_selecionadas)

        argumentos = []

        if escaneamento_rapido and not portas:
            argumentos.append('-T4 -F')  # Quick Scan
        if portas:
            argumentos.append(f'-p {portas}')
        if escaneamento_rapido:
            argumentos.append('-T4')

        argumentos_str = ' '.join(argumentos)

        nm = nmap.PortScanner()
        try:
            nm.scan(hosts=str(rede), arguments=argumentos_str)

            resultados = []
            for host in nm.all_hosts():
                nome_host = nm[host].hostname() if escaneamento_rapido else 'N/A'
                endereco_mac = nm[host]['addresses'].get('mac', 'N/A')
                endereco_ip = nm[host]['addresses'].get('ipv4', 'N/A')
                portas_abertas = ', '.join([f"{port}/ABERTA" if port.isdigit() and nm[host].has_tcp(int(port)) and nm[host]['tcp'][int(port)]['state'] == 'open' else f"{port}/FECHADA" for port in portas.split(',') if port]) or 'N/D'
                resultados.append((nome_host, endereco_mac, endereco_ip, portas_abertas))

            # Guarda os resultados relevantes no banco de dados
            caminho_db = os.path.join(os.path.dirname(__file__), 'banco.db')
            with sqlite3.connect(caminho_db) as conn:
                cursor = conn.cursor()
                for resultado in resultados:
                    cursor.execute('''
                        INSERT INTO scanner (data, nome_host, endereco_mac, ip, portas)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resultado[0], resultado[1], resultado[2], resultado[3]))
                conn.commit()

            # Exibe os resultados do escaneamento
            resultado_texto = "\n".join([
                f"Nome do Host: {r[0]} | MAC: {r[1]} | IP: {r[2]} | Portas: {r[3]}"
                for r in resultados
            ])
            print(resultado_texto)
        except Exception as e:
            print(f"Erro ao executar o comando nmap: {e}")
