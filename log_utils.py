import os
from datetime import datetime
import traceback

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'eventos.log')

# Tipos: INFO, ERRO, WARNING, etc.
def registrar_evento(evento, tipo='INFO'):
    os.makedirs(LOG_DIR, exist_ok=True)
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'[{dt}] [{tipo}] {evento}\n')

def registrar_erro(exc: Exception, contexto=''):
    tb = traceback.format_exc()
    msg = f'{contexto} | {str(exc)}\n{tb}'
    registrar_evento(msg, tipo='ERRO')

def ler_logs(filtro_data=None, filtro_tipo=None):
    if not os.path.exists(LOG_FILE):
        return []
    linhas = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for linha in f:
            if filtro_data and filtro_data not in linha:
                continue
            if filtro_tipo and f'[{filtro_tipo}]' not in linha:
                continue
            linhas.append(linha)
    return linhas

def exportar_logs(destino):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, 'r', encoding='utf-8') as fsrc:
        with open(destino, 'w', encoding='utf-8') as fdst:
            fdst.write(fsrc.read())
    return True
