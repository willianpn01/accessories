from PIL import Image
import os

def converter_imagem(input_paths, output_format, output_dir=None):
    """
    Converte uma ou mais imagens para o formato especificado ('png', 'jpg', etc).
    Retorna uma lista de tuplas (input, output).
    Se output_dir for fornecido, salva os arquivos lá.
    """
    if not isinstance(input_paths, list):
        input_paths = [input_paths]
    resultados = []
    for input_path in input_paths:
        img = Image.open(input_path)
        base = os.path.splitext(os.path.basename(input_path))[0]
        fmt = output_format.lower()
        if fmt == 'png':
            out_name = base + '.png'
            out_path = os.path.join(output_dir, out_name) if output_dir else os.path.splitext(input_path)[0] + '.png'
            img.save(out_path, format='PNG')
        elif fmt in ['jpg', 'jpeg', 'jfif']:
            out_name = base + '.jpg'
            out_path = os.path.join(output_dir, out_name) if output_dir else os.path.splitext(input_path)[0] + '.jpg'
            img = img.convert('RGB')
            img.save(out_path, format='JPEG')
        elif fmt == 'bmp':
            out_name = base + '.bmp'
            out_path = os.path.join(output_dir, out_name) if output_dir else os.path.splitext(input_path)[0] + '.bmp'
            img.save(out_path, format='BMP')
        elif fmt == 'gif':
            out_name = base + '.gif'
            out_path = os.path.join(output_dir, out_name) if output_dir else os.path.splitext(input_path)[0] + '.gif'
            img.save(out_path, format='GIF')
        elif fmt == 'webp':
            out_name = base + '.webp'
            out_path = os.path.join(output_dir, out_name) if output_dir else os.path.splitext(input_path)[0] + '.webp'
            img.save(out_path, format='WEBP')
        else:
            raise ValueError('Formato não suportado: ' + output_format)
        resultados.append((input_path, out_path))
    return resultados
