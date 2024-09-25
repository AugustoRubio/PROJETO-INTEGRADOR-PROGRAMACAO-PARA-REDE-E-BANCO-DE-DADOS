import subprocess
import tkinter as tk
import nmap
import sqlite3
from datetime import datetime
import socket
import ipaddress
import psutil
import os

def scanner():
    def escanear_propria_rede():
        def iniciar_escaneamento():
            global janela_resultados
            if janela_resultados:
                janela_resultados.destroy()
            
            portas_selecionadas = []
            if var_ssh.get():
                portas_selecionadas.append('22')
            if var_http.get():
                portas_selecionadas.append('80')
            if var_https.get():
                portas_selecionadas.append('443')
            
            portas = ','.join(portas_selecionadas)
            
            argumentos = []
            
            if var_quick_scan.get():
                argumentos.append('-T4 -F')  # Quick Scan
            if portas:
                argumentos.append(f'-p {portas}')
            
            argumentos_str = ' '.join(argumentos)
            
            # Exibe a janela de resultados antes de iniciar o escaneamento
            janela_resultados = tk.Toplevel()
            janela_resultados.title("Resultados do Escaneamento")
            janela_resultados.geometry("800x600")
            text_resultados = tk.Text(janela_resultados, wrap="word")
            text_resultados.insert("1.0", f"Comando executado: nmap {argumentos_str} {rede}\n\n")
            text_resultados.pack(expand=True, fill="both")
            janela_resultados.update()
            
            nm = nmap.PortScanner()
            try:
                nm.scan(hosts=str(rede), arguments=argumentos_str)
                
                resultados = []
                for host in nm.all_hosts():
                    hostname = nm[host].hostname() if var_quick_scan.get() else 'N/A'
                    mac_address = nm[host]['addresses'].get('mac', 'N/A')
                    ip_address = nm[host]['addresses'].get('ipv4', 'N/A')
                    portas_abertas = ', '.join([f"{port}/ABERTA" if port.isdigit() and nm[host].has_tcp(int(port)) and nm[host]['tcp'][int(port)]['state'] == 'open' else f"{port}/FECHADA" for port in portas.split(',') if port]) or 'N/D'
                    resultados.append((hostname, mac_address, ip_address, portas_abertas))
                
                # Guarda os resultados relevantes no banco de dados
                db_path = os.path.join(os.path.dirname(__file__), 'banco.db')
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    for resultado in resultados:
                        cursor.execute('''
                            INSERT INTO scanner (data, hostname, mac_address, ip, portas)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resultado[0], resultado[1], resultado[2], resultado[3]))
                    conn.commit()
                
                # Atualiza a janela de resultados com os dados do escaneamento
                resultado_texto = "\n".join([
                    f"Hostname: {r[0]} | MAC: {r[1]} | IP: {r[2]} | Portas: {r[3]}"
                    for r in resultados
                ])
                text_resultados.insert("end", resultado_texto)
            except Exception as e:
                text_resultados.insert("end", f"Erro ao executar o comando nmap: {e}")
            text_resultados.update()

        janela_propria_rede = tk.Toplevel()
        janela_propria_rede.title("Escanear Própria Rede")
        janela_propria_rede.geometry("400x300")
        
        var_quick_scan = tk.BooleanVar(value=True)
        var_ssh = tk.BooleanVar()
        var_http = tk.BooleanVar()
        var_https = tk.BooleanVar()
        
        chk_quick_scan = tk.Checkbutton(janela_propria_rede, text="Quick Scan (-T4 -F)", variable=var_quick_scan)
        chk_quick_scan.pack(pady=5)
        
        chk_ssh = tk.Checkbutton(janela_propria_rede, text="Porta 22 (SSH)", variable=var_ssh)
        chk_ssh.pack(pady=5)
        
        chk_http = tk.Checkbutton(janela_propria_rede, text="Porta 80 (HTTP)", variable=var_http)
        chk_http.pack(pady=5)
        
        chk_https = tk.Checkbutton(janela_propria_rede, text="Porta 443 (HTTPS)", variable=var_https)
        chk_https.pack(pady=5)
        
        btn_iniciar = tk.Button(janela_propria_rede, text="Iniciar Escaneamento", command=iniciar_escaneamento)
        btn_iniciar.pack(pady=20)
        
        btn_voltar = tk.Button(janela_propria_rede, text="Voltar ao Menu Principal", command=janela_propria_rede.destroy)
        btn_voltar.pack(pady=10)

    def escanear_outra_rede():
        def iniciar_escaneamento():
            global janela_resultados
            if janela_resultados:
                janela_resultados.destroy()
            
            rede = entry_rede.get()
            portas_selecionadas = []
            if var_ssh.get():
                portas_selecionadas.append('22')
            if var_http.get():
                portas_selecionadas.append('80')
            if var_https.get():
                portas_selecionadas.append('443')
            
            portas = ','.join(portas_selecionadas)
            
            argumentos = []
            
            if var_quick_scan.get():
                argumentos.append('-T4 -F')  # Quick Scan
            if portas:
                argumentos.append(f'-p {portas}')
            
            argumentos_str = ' '.join(argumentos)
            
            # Exibe a janela de resultados antes de iniciar o escaneamento
            janela_resultados = tk.Toplevel()
            janela_resultados.title("Resultados do Escaneamento")
            janela_resultados.geometry("800x600")
            text_resultados = tk.Text(janela_resultados, wrap="word")
            text_resultados.insert("1.0", f"Comando executado: nmap {argumentos_str} {rede}\n\n")
            text_resultados.pack(expand=True, fill="both")
            janela_resultados.update()
            
            nm = nmap.PortScanner()
            try:
                nm.scan(hosts=rede, arguments=argumentos_str)
                
                resultados = []
                for host in nm.all_hosts():
                    hostname = nm[host].hostname() if var_quick_scan.get() else 'N/A'
                    mac_address = nm[host]['addresses'].get('mac', 'N/A')
                    ip_address = nm[host]['addresses'].get('ipv4', 'N/A')
                    portas_abertas = ', '.join([f"{port}/ABERTA" if nm[host].has_tcp(int(port)) and nm[host]['tcp'][int(port)]['state'] == 'open' else f"{port}/FECHADA" for port in portas.split(',')]) or 'N/D'
                    resultados.append((hostname, mac_address, ip_address, portas_abertas))
                
                # Guarda os resultados relevantes no banco de dados
                db_path = os.path.join(os.path.dirname(__file__), 'banco.db')
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    for resultado in resultados:
                        cursor.execute('''
                            INSERT INTO scanner (data, hostname, mac_address, ip, portas)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resultado[0], resultado[1], resultado[2], resultado[3]))
                    conn.commit()
                
                # Atualiza a janela de resultados com os dados do escaneamento
                resultado_texto = "\n".join([
                    f"Hostname: {r[0]} | MAC: {r[1]} | IP: {r[2]} | Portas: {r[3]}"
                    for r in resultados
                ])
                text_resultados.insert("end", resultado_texto)
            except Exception as e:
                text_resultados.insert("end", f"Erro ao executar o comando nmap: {e}")
            text_resultados.update()

        janela_outra_rede = tk.Toplevel()
        janela_outra_rede.title("Escanear Outra Rede")
        janela_outra_rede.geometry("400x300")
        
        label_rede = tk.Label(janela_outra_rede, text="Digite a rede (ex: 192.168.1.0/24):")
        label_rede.pack(pady=5)
        entry_rede = tk.Entry(janela_outra_rede)
        entry_rede.pack(pady=5)
        
        var_quick_scan = tk.BooleanVar(value=True)
        var_ssh = tk.BooleanVar()
        var_http = tk.BooleanVar()
        var_https = tk.BooleanVar()
        
        chk_quick_scan = tk.Checkbutton(janela_outra_rede, text="Quick Scan (-T4 -F)", variable=var_quick_scan)
        chk_quick_scan.pack(pady=5)
        
        chk_ssh = tk.Checkbutton(janela_outra_rede, text="Porta 22 (SSH)", variable=var_ssh)
        chk_ssh.pack(pady=5)
        
        chk_http = tk.Checkbutton(janela_outra_rede, text="Porta 80 (HTTP)", variable=var_http)
        chk_http.pack(pady=5)
        
        chk_https = tk.Checkbutton(janela_outra_rede, text="Porta 443 (HTTPS)", variable=var_https)
        chk_https.pack(pady=5)
        
        btn_iniciar = tk.Button(janela_outra_rede, text="Iniciar Escaneamento", command=iniciar_escaneamento)
        btn_iniciar.pack(pady=20)
        
        btn_voltar = tk.Button(janela_outra_rede, text="Voltar ao Menu Principal", command=janela_outra_rede.destroy)
        btn_voltar.pack(pady=5)
            
    # Cria uma nova janela para opções de escaneamento
    janela_opcoes = tk.Toplevel()
    janela_opcoes.title("Opções de Escaneamento")
    janela_opcoes.geometry("400x300")

    # Obtém o endereço IP e a máscara de sub-rede
    ip = socket.gethostbyname(socket.gethostname())
    mascara = ipaddress.IPv4Network(f"{ip}/24", strict=False).netmask
    rede = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)
            
    # Exibe a rede do usuário
    label_rede_usuario = tk.Label(janela_opcoes, text=f"Sua rede: {rede}")
    label_rede_usuario.pack(pady=5)

    # Lista de adaptadores de rede
    adaptadores = psutil.net_if_addrs()
    adaptadores_nomes = list(adaptadores.keys())
    
    label_adaptador = tk.Label(janela_opcoes, text="Escolha o adaptador de rede:")
    label_adaptador.pack(pady=5)
    
    var_adaptador = tk.StringVar(value=adaptadores_nomes[0])
    dropdown_adaptadores = tk.OptionMenu(janela_opcoes, var_adaptador, *adaptadores_nomes)
    dropdown_adaptadores.pack(pady=5)

    btn_propria_rede = tk.Button(janela_opcoes, text="Escanear Própria Rede", command=escanear_propria_rede)
    btn_propria_rede.pack(pady=5)
    
    btn_outra_rede = tk.Button(janela_opcoes, text="Escanear Outra Rede", command=escanear_outra_rede)
    btn_outra_rede.pack(pady=5)
    
    btn_voltar = tk.Button(janela_opcoes, text="Voltar ao Menu Principal", command=janela_opcoes.destroy)
    btn_voltar.pack(pady=5)

    janela_opcoes.mainloop()

# Variável para armazenar a janela de resultados
janela_resultados = None
