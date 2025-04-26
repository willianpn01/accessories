from PIL import Image
import os

def redimensionar_imagens(arquivos, largura, altura, manter_proporcao=True):
    """
    Redimensiona imagens para o tamanho especificado.
    Se manter_proporcao for True, ajusta para caber dentro de (largura, altura) mantendo proporção.
    Retorna lista de tuplas (input, output).
    """
    resultados = []
    for arquivo in arquivos:
        img = Image.open(arquivo)
        if manter_proporcao:
            img.thumbnail((largura, altura), Image.LANCZOS)
        else:
            img = img.resize((largura, altura), Image.LANCZOS)
        base, ext = os.path.splitext(arquivo)
        out_path = f"{base}_resized{ext}"
        img.save(out_path)
        resultados.append((arquivo, out_path))
    return resultados
