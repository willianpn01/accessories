from PIL import Image
import os

def converter_imagem(input_paths, output_format):
    """
    Converte uma ou mais imagens para o formato especificado ('png', 'jpg', etc).
    Retorna uma lista de tuplas (input, output).
    """
    if not isinstance(input_paths, list):
        input_paths = [input_paths]
    resultados = []
    for input_path in input_paths:
        img = Image.open(input_path)
        base, _ = os.path.splitext(input_path)
        fmt = output_format.lower()
        if fmt == 'png':
            out_path = base + '.png'
            img.save(out_path, format='PNG')
        elif fmt in ['jpg', 'jpeg', 'jfif']:
            out_path = base + '.jpg'
            img = img.convert('RGB')
            img.save(out_path, format='JPEG')
        elif fmt == 'bmp':
            out_path = base + '.bmp'
            img.save(out_path, format='BMP')
        elif fmt == 'gif':
            out_path = base + '.gif'
            img.save(out_path, format='GIF')
        elif fmt == 'webp':
            out_path = base + '.webp'
            img.save(out_path, format='WEBP')
        else:
            raise ValueError('Formato não suportado: ' + output_format)
        resultados.append((input_path, out_path))
    return resultados
