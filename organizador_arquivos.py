import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt

EXT_MAP = {
    'Imagens': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
    'Documentos': ['.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.rtf'],
    'Áudio': ['.mp3', '.wav', '.ogg', '.flac'],
    'Vídeos': ['.mp4', '.avi', '.mov', '.wmv', '.mkv'],
    'Compactados': ['.zip', '.rar', '.7z', '.tar', '.gz'],
}

def get_folder_type(ext):
    for folder, exts in EXT_MAP.items():
        if ext in exts:
            return folder
    return 'Outros'

class OrganizadorArquivos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Organizador de Arquivos')
        self.setGeometry(200, 200, 400, 180)
        self.folder_path = ''
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel('Selecione uma pasta para organizar os arquivos.')
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        self.btn_select = QPushButton('Selecionar Pasta')
        self.btn_select.clicked.connect(self.select_folder)
        layout.addWidget(self.btn_select)

        self.btn_organize = QPushButton('Organizar Arquivos')
        self.btn_organize.clicked.connect(self.organize_files)
        self.btn_organize.setEnabled(False)
        layout.addWidget(self.btn_organize)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Selecione a pasta')
        if folder:
            self.folder_path = folder
            self.label.setText(f'Pasta selecionada: {folder}')
            self.btn_organize.setEnabled(True)

    def organize_files(self):
        if not self.folder_path:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma pasta primeiro.')
            return
        try:
            count = 0
            for item in os.listdir(self.folder_path):
                full_path = os.path.join(self.folder_path, item)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(item)[1].lower()
                    folder_type = get_folder_type(ext)
                    target_folder = os.path.join(self.folder_path, folder_type)
                    os.makedirs(target_folder, exist_ok=True)
                    shutil.move(full_path, os.path.join(target_folder, item))
                    count += 1
            QMessageBox.information(self, 'Sucesso', f'Organização concluída! {count} arquivo(s) movido(s).')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao organizar arquivos:\n{str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = OrganizadorArquivos()
    win.show()
    sys.exit(app.exec())
