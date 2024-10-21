import json
from collections import defaultdict
import requests

class MonitorDeHardware:
    def __init__(self, url='http://localhost:8085/data.json'):
        self.url = url

    # Obtém informações de hardware a partir da URL fornecida
    def obter_info_hardware(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            info_hardware = response.json()
            return info_hardware
        else:
            return {}

class ExtratorDeInfoHardware:
    @staticmethod
    # Extrai informações de um nó específico
    def extrair_info(no):
        extraido = {
            'id': no.get('id', ''),
            'Texto': no.get('Text', ''),
            'Min': no.get('Min', ''),
            'Valor': no.get('Value', ''),
            'Max': no.get('Max', ''),
            'IdSensor': no.get('SensorId', ''),
            'Tipo': no.get('Type', ''),
            'URLImagem': no.get('ImageURL', ''),
            'Filhos': [ExtratorDeInfoHardware.extrair_info(filho) for filho in no.get('Children', [])]
        }
        return extraido

    @staticmethod
    # Obtém informações de hardware extraídas de todos os nós filhos
    def obter_info(info_hardware):
        return [ExtratorDeInfoHardware.extrair_info(hardware) for hardware in info_hardware.get('Children', [])]

    @staticmethod
    # Encontra sensores específicos dentro das informações extraídas
    def encontrar_sensores_especificos(info_extraida):
        sensores = {
            'CPU Total': None,
            'Temperatura CPU': None,
            'Carga RAM': None,
            'Carga GPU': None
        }

        # Percorre recursivamente os nós para encontrar os sensores específicos
        def percorrer(no):
            if no['Tipo'] == 'Load' and 'CPU Total' in no['Texto']:
                sensores['CPU Total'] = no['Valor']
            elif no['Tipo'] == 'Temperature' and 'Core (Tctl/Tdie)' in no['Texto']:
                sensores['Temperatura CPU'] = no['Valor']
            elif no['Tipo'] == 'Load' and 'Memory' in no['Texto']:
                sensores['Carga RAM'] = no['Valor']
            elif no['Tipo'] == 'Load' and 'GPU Core' in no['Texto']:
                sensores['Carga GPU'] = no['Valor']
            for filho in no['Filhos']:
                percorrer(filho)

        for info in info_extraida:
            percorrer(info)

        return sensores

# Agrupa e calcula a média dos valores por tipo de sensor
def agrupar_e_media_por_tipo(info_extraida):
    dados_agrupados = defaultdict(list)
    
    # Percorre recursivamente os nós para agrupar os dados por tipo
    def percorrer(no):
        if 'Tipo' in no and 'Valor' in no:
            try:
                valor = no['Valor'].replace(',', '.').split()[0] if no['Valor'] else '0'  # Lida com valores como "1,550 V"
                dados_agrupados[no['Tipo']].append(float(valor))
            except ValueError:
                pass  # ou trate o erro conforme necessário
        for filho in no.get('Filhos', []):
            percorrer(filho)
    
    for info in info_extraida:
        percorrer(info)
    
    # Calcula a média dos valores agrupados
    dados_media = {k: sum(v) / len(v) for k, v in dados_agrupados.items() if v}
    return dados_media

# Exemplo de uso
if __name__ == '__main__':
    # Busca dados reais da URL
    monitor = MonitorDeHardware()
    dados = monitor.obter_info_hardware()

    # Extrai e imprime as informações dos sensores
    extrator = ExtratorDeInfoHardware()
    info_extraida = extrator.obter_info(dados)

    # Função para imprimir informações dos sensores de forma hierárquica
    def imprimir_sensor(sensor, nivel=0):
        indentacao = "  " * nivel
        print(f"{indentacao}ID do Sensor: {sensor['id']}, Texto: {sensor['Texto']}")
        for filho in sensor['Filhos']:
            imprimir_sensor(filho, nivel + 1)

    for sensor in info_extraida:
        imprimir_sensor(sensor)

    # Encontra e imprime sensores específicos
    sensores_especificos = extrator.encontrar_sensores_especificos(info_extraida)
    print("\nSensores Específicos:")
    for chave, valor in sensores_especificos.items():
        print(f"{chave}: {valor}")
