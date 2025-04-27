import os

def listar_arquivos(pasta, extensao=None):
    arquivos = []
    for nome in os.listdir(pasta):
        caminho = os.path.join(pasta, nome)
        if os.path.isfile(caminho):
            if extensao:
                if nome.lower().endswith(extensao.lower()):
                    arquivos.append(nome)
            else:
                arquivos.append(nome)
    return arquivos

def renomear_arquivos(pasta, arquivos, nome_base, somente_ext=None, adicionar_numero=True):
    """
    Renomeia arquivos na pasta. Se adicionar_numero=False, evita sobrescrever arquivos existentes.
    Retorna lista de tuplas (original, novo_nome).
    """
    renomeados = []
    contador = 1
    for arquivo in arquivos:
        ext = os.path.splitext(arquivo)[1]
        if somente_ext and ext.lower() != somente_ext.lower():
            continue
        novo_nome = nome_base
        if adicionar_numero:
            novo_nome += f'_{contador}'
            contador += 1
        novo_nome += ext
        origem = os.path.join(pasta, arquivo)
        destino = os.path.join(pasta, novo_nome)
        if not adicionar_numero and os.path.exists(destino):
            # Evita sobrescrever: gera nome alternativo
            base, ext2 = os.path.splitext(novo_nome)
            i = 2
            while os.path.exists(os.path.join(pasta, f"{base}({i}){ext2}")):
                i += 1
            destino = os.path.join(pasta, f"{base}({i}){ext2}")
        os.rename(origem, destino)
        renomeados.append((arquivo, os.path.basename(destino)))
    return renomeados
