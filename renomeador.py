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

def renomear_arquivos(pasta, arquivos, padrao_nome, somente_ext=None, adicionar_numero=True, comecar_em=1):
    renomeados = []
    num = comecar_em
    for nome in arquivos:
        ext = os.path.splitext(nome)[1]
        if somente_ext and ext.lower() != somente_ext.lower():
            continue
        if padrao_nome:
            novo_nome = padrao_nome
            if adicionar_numero:
                novo_nome += f'_{num}'
            novo_nome += ext
        else:
            novo_nome = f'{num}{ext}'
        origem = os.path.join(pasta, nome)
        destino = os.path.join(pasta, novo_nome)
        os.rename(origem, destino)
        renomeados.append((nome, novo_nome))
        num += 1
    return renomeados
