import os
import shutil

EXT_MAP = {
    'Imagens': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
    'Documentos': ['.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.rtf'],
    'Áudio': ['.mp3', '.wav', '.ogg', '.flac'],
    'Vídeos': ['.mp4', '.avi', '.mov', '.wmv', '.mkv'],
    'Compactados': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'ISOs': ['.iso', '.bin', '.cue', '.img'],
    'Executáveis': ['.exe']
}

def get_folder_type(ext):
    for folder, exts in EXT_MAP.items():
        if ext in exts:
            return folder
    return 'Outros'


def organizar_pasta(folder_path):
    arquivos_movidos = []
    for item in os.listdir(folder_path):
        full_path = os.path.join(folder_path, item)
        if os.path.isfile(full_path):
            ext = os.path.splitext(item)[1].lower()
            folder_type = get_folder_type(ext)
            target_folder = os.path.join(folder_path, folder_type)
            os.makedirs(target_folder, exist_ok=True)
            shutil.move(full_path, os.path.join(target_folder, item))
            arquivos_movidos.append((item, folder_type))
    return arquivos_movidos
