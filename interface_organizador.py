import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QHBoxLayout, QComboBox, QTabWidget, QMainWindow, QDockWidget, QListView, QStackedWidget, QProgressBar, QLineEdit
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from organizador import organizar_pasta
from conversor_imagem import converter_imagem
from renomeador import listar_arquivos, renomear_arquivos
from redimensionador import redimensionar_imagens
from pdf_utils import dividir_pdf, mesclar_pdfs, imagens_para_pdf, extrair_texto_pdf
from ocr_utils import ocr_imagem, ocr_pdf, ocr_pdf_to_pdf
from docx_utils import docx_para_pdf, pdf_para_docx
from relatorio_utils import analisar_pasta, gerar_relatorio_html, gerar_relatorio_pdf, gerar_grafico_pizza
from log_utils import registrar_evento, registrar_erro, ler_logs, exportar_logs
import os

# Função para aplicar tema moderno
MODERN_STYLE = """
/* Tema escuro moderno para toda a aplicação */
QWidget {
    background: #23272e;
    color: #f1f1f1;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 15px;
}
QMainWindow {
    background: #21252b;
}
QTabWidget::pane {
    border: 1px solid #444;
    border-radius: 10px;
    background: #23272e;
    margin: 8px;
    box-shadow: 0px 2px 12px #111;
}
QTabBar::tab {
    background: #23272e;
    border: 1px solid #444;
    border-radius: 8px;
    padding: 8px 22px;
    margin: 2px;
    font-weight: 500;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4e6ef2, stop:1 #23272e);
    color: #fff;
    border: 2px solid #4e6ef2;
}
QPushButton {
    background: #323846;
    border-radius: 8px;
    border: 1px solid #444;
    padding: 8px 20px;
    font-size: 15px;
    font-weight: 500;
    margin: 6px 0;
}
QPushButton:hover {
    background: #4e6ef2;
    color: #fff;
    border: 1.5px solid #4e6ef2;
}
QPushButton:pressed {
    background: #3a3f4b;
}
QLabel {
    color: #f1f1f1;
    font-size: 15px;
}
QLineEdit, QComboBox, QListWidget, QSpinBox {
    background: #2c313c;
    border-radius: 6px;
    border: 1px solid #444;
    color: #f1f1f1;
    padding: 6px;
    font-size: 15px;
}
QListWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #353945;
}
QListWidget::item:selected {
    background: #4e6ef2;
    color: #fff;
}
QDockWidget {
    background: #23272e;
    border: none;
}
QDockWidget::title {
    background: transparent;
    color: #8aa4f7;
    font-size: 16px;
    font-weight: bold;
    padding: 8px 0 2px 8px;
}
QScrollBar:vertical {
    background: #23272e;
    width: 12px;
    margin: 0px 0px 0px 0px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #4e6ef2;
    min-height: 24px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QComboBox QAbstractItemView {
    background: #23272e;
    color: #f1f1f1;
    border-radius: 6px;
    selection-background-color: #4e6ef2;
    selection-color: #fff;
}
"""

# --- Worker Base para ações longas com progresso/cancelamento ---
class WorkerBase(QThread):
    progresso = pyqtSignal(int)
    resultado = pyqtSignal(object)
    erro = pyqtSignal(Exception)
    def __init__(self):
        super().__init__()
        self._cancelado = False
    def cancelar(self):
        self._cancelado = True
    def check_cancelado(self):
        if self._cancelado:
            raise Exception('Operação cancelada pelo usuário.')

# --- Worker para OCR de imagens ---
class OCRImagemWorker(WorkerBase):
    def __init__(self, imagens, lang):
        super().__init__()
        self.imagens = imagens
        self.lang = lang
    def run(self):
        from ocr_utils import ocr_imagem
        resultados = []
        total = len(self.imagens)
        try:
            for idx, img in enumerate(self.imagens):
                self.check_cancelado()
                texto = ocr_imagem(img, lang=self.lang)
                resultados.append((img, texto))
                self.progresso.emit(int((idx+1)/total*100))
            self.resultado.emit(resultados)
        except Exception as e:
            self.erro.emit(e)

# --- Worker para conversão de imagens ---
class ConversaoImagemWorker(WorkerBase):
    def __init__(self, arquivos, formato, pasta_saida):
        super().__init__()
        self.arquivos = arquivos
        self.formato = formato
        self.pasta_saida = pasta_saida
    def run(self):
        from conversor_imagem import converter_imagem
        resultados = []
        total = len(self.arquivos)
        try:
            for idx, arquivo in enumerate(self.arquivos):
                self.check_cancelado()
                out = converter_imagem(arquivo, self.formato, self.pasta_saida)
                resultados.append((arquivo, out))
                self.progresso.emit(int((idx+1)/total*100))
            self.resultado.emit(resultados)
        except Exception as e:
            self.erro.emit(e)

# --- Worker para redimensionamento de imagens ---
class RedimensionarWorker(WorkerBase):
    def __init__(self, arquivos, largura, altura, manter):
        super().__init__()
        self.arquivos = arquivos
        self.largura = largura
        self.altura = altura
        self.manter = manter
    def run(self):
        from redimensionador import redimensionar_imagens
        resultados = []
        total = len(self.arquivos)
        try:
            for idx, arquivo in enumerate(self.arquivos):
                self.check_cancelado()
                out = redimensionar_imagens([arquivo], self.largura, self.altura, self.manter)
                resultados.append((arquivo, out[0] if out else ''))
                self.progresso.emit(int((idx+1)/total*100))
            self.resultado.emit(resultados)
        except Exception as e:
            self.erro.emit(e)

class OrganizadorTab(QWidget):
    def __init__(self):
        super().__init__()
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
        self.list_widget = QListWidget()
        self.list_widget.setVisible(False)
        layout.addWidget(self.list_widget)
        self.folder_path = ''
        self.arquivos_movidos = []
        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Selecione a pasta')
        if folder:
            self.folder_path = folder
            self.label.setText(f'Pasta selecionada: {folder}')
            self.btn_organize.setEnabled(True)
            self.list_widget.clear()
            self.list_widget.setVisible(False)

    def organize_files(self):
        if not self.folder_path:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma pasta primeiro.')
            return
        try:
            self.arquivos_movidos = organizar_pasta(self.folder_path)
            if self.arquivos_movidos:
                QMessageBox.information(self, 'Sucesso', f'{len(self.arquivos_movidos)} arquivo(s) movido(s). Veja a lista abaixo.')
                self.list_widget.clear()
                for nome, pasta in self.arquivos_movidos:
                    item = QListWidgetItem(f'{nome}  →  {pasta}')
                    self.list_widget.addItem(item)
                self.list_widget.setVisible(True)
            else:
                QMessageBox.information(self, 'Nada a organizar', 'Nenhum arquivo foi movido.')
                self.list_widget.clear()
                self.list_widget.setVisible(False)
        except Exception as e:
            registrar_erro(e, contexto='Organizar arquivos')
            QMessageBox.critical(self, 'Erro', f'Erro ao organizar arquivos:\n{str(e)}')

class OCRImagemTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('OCR de Imagens'))
        self.btn_selecionar = QPushButton('Selecionar Imagens')
        self.btn_selecionar.clicked.connect(self.selecionar_imgs)
        layout.addWidget(self.btn_selecionar)
        self.label_imgs = QLabel('Nenhuma imagem selecionada.')
        layout.addWidget(self.label_imgs)
        self.btn_exec = QPushButton('Executar OCR')
        self.btn_exec.clicked.connect(self.exec_ocr_imgs)
        layout.addWidget(self.btn_exec)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.btn_cancelar = QPushButton('Cancelar')
        self.btn_cancelar.setVisible(False)
        self.btn_cancelar.clicked.connect(self.cancelar_ocr)
        layout.addWidget(self.btn_cancelar)
        self.result_list = QListWidget()
        layout.addWidget(self.result_list)
        self.setLayout(layout)
        self.imgs = []
        self.worker = None
    def selecionar_imgs(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Selecionar imagens', '', 'Imagens (*.png *.jpg *.jpeg *.bmp *.gif *.webp)')
        if files:
            self.imgs = files
            self.label_imgs.setText(f'{len(files)} imagem(ns) selecionada(s)')
        else:
            self.imgs = []
            self.label_imgs.setText('Nenhuma imagem selecionada.')
    def exec_ocr_imgs(self):
        if not self.imgs:
            QMessageBox.warning(self, 'Aviso', 'Selecione imagens primeiro.')
            return
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.btn_cancelar.setVisible(True)
        self.result_list.clear()
        self.worker = OCRImagemWorker(self.imgs, lang='eng')
        self.worker.progresso.connect(self.progress.setValue)
        self.worker.resultado.connect(self.ocr_finalizado)
        self.worker.erro.connect(self.ocr_erro)
        self.worker.start()
    def cancelar_ocr(self):
        if self.worker:
            self.worker.cancelar()
    def ocr_finalizado(self, resultados):
        self.progress.setVisible(False)
        self.btn_cancelar.setVisible(False)
        for img, texto in resultados:
            self.result_list.addItem(f'{os.path.basename(img)}: {texto[:60]}...')
        QMessageBox.information(self, 'OCR', 'OCR concluído!')
    def ocr_erro(self, exc):
        from log_utils import registrar_erro
        registrar_erro(exc, contexto='OCR de imagens')
        self.progress.setVisible(False)
        self.btn_cancelar.setVisible(False)
        QMessageBox.critical(self, 'Erro', f'Erro no OCR:\n{str(exc)}\n')

class ConversorTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Conversor de Imagens'))
        self.btn_selecionar = QPushButton('Selecionar Imagens')
        self.btn_selecionar.clicked.connect(self.selecionar_imgs)
        layout.addWidget(self.btn_selecionar)
        self.label_imgs = QLabel('Nenhuma imagem selecionada.')
        layout.addWidget(self.label_imgs)
        self.combo_formato = QComboBox()
        self.combo_formato.addItems(['PNG', 'JPG', 'JFIF', 'BMP', 'GIF', 'WEBP'])
        layout.addWidget(self.combo_formato)
        self.btn_exec = QPushButton('Converter')
        self.btn_exec.clicked.connect(self.exec_converter)
        layout.addWidget(self.btn_exec)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.btn_cancelar = QPushButton('Cancelar')
        self.btn_cancelar.setVisible(False)
        self.btn_cancelar.clicked.connect(self.cancelar_converter)
        layout.addWidget(self.btn_cancelar)
        self.result_list = QListWidget()
        layout.addWidget(self.result_list)
        self.setLayout(layout)
        self.imgs = []
        self.worker = None
    def selecionar_imgs(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Selecionar imagens', '', 'Imagens (*.png *.jpg *.jpeg *.bmp *.gif *.webp)')
        if files:
            self.imgs = files
            self.label_imgs.setText(f'{len(files)} imagem(ns) selecionada(s)')
        else:
            self.imgs = []
            self.label_imgs.setText('Nenhuma imagem selecionada.')
    def exec_converter(self):
        if not self.imgs:
            QMessageBox.warning(self, 'Aviso', 'Selecione imagens primeiro.')
            return
        pasta_saida = QFileDialog.getExistingDirectory(self, 'Selecione a pasta de saída')
        if not pasta_saida:
            return
        formato = self.combo_formato.currentText().lower()
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.btn_cancelar.setVisible(True)
        self.result_list.clear()
        self.worker = ConversaoImagemWorker(self.imgs, formato, pasta_saida)
        self.worker.progresso.connect(self.progress.setValue)
        self.worker.resultado.connect(self.converter_finalizado)
        self.worker.erro.connect(self.converter_erro)
        self.worker.start()
    def cancelar_converter(self):
        if self.worker:
            self.worker.cancelar()
    def converter_finalizado(self, resultados):
        self.progress.setVisible(False)
        self.btn_cancelar.setVisible(False)
        for inp, out in resultados:
            self.result_list.addItem(f'{os.path.basename(inp)} → {os.path.basename(out)}')
        QMessageBox.information(self, 'Conversão', 'Conversão concluída!')
    def converter_erro(self, exc):
        from log_utils import registrar_erro
        registrar_erro(exc, contexto='Conversão de imagens')
        self.progress.setVisible(False)
        self.btn_cancelar.setVisible(False)
        QMessageBox.critical(self, 'Erro', f'Erro na conversão:\n{str(exc)}\n')

class RedimensionadorTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Redimensionador de Imagens'))
        self.btn_selecionar = QPushButton('Selecionar Imagens')
        self.btn_selecionar.clicked.connect(self.selecionar_imgs)
        layout.addWidget(self.btn_selecionar)
        self.label_imgs = QLabel('Nenhuma imagem selecionada.')
        layout.addWidget(self.label_imgs)
        hbox = QHBoxLayout()
        self.input_largura = QLineEdit()
        self.input_largura.setPlaceholderText('Largura')
        hbox.addWidget(self.input_largura)
        self.input_altura = QLineEdit()
        self.input_altura.setPlaceholderText('Altura')
        hbox.addWidget(self.input_altura)
        self.chk_manter = QComboBox()
        self.chk_manter.addItems(['Manter proporção', 'Não manter'])
        hbox.addWidget(self.chk_manter)
        layout.addLayout(hbox)
        self.btn_exec = QPushButton('Redimensionar')
        self.btn_exec.clicked.connect(self.exec_redimensionar)
        layout.addWidget(self.btn_exec)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.btn_cancelar = QPushButton('Cancelar')
        self.btn_cancelar.setVisible(False)
        self.btn_cancelar.clicked.connect(self.cancelar_redim)
        layout.addWidget(self.btn_cancelar)
        self.result_list = QListWidget()
        layout.addWidget(self.result_list)
        self.setLayout(layout)
        self.imgs = []
        self.worker = None
    def selecionar_imgs(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Selecionar imagens', '', 'Imagens (*.png *.jpg *.jpeg *.bmp *.gif *.webp)')
        if files:
            self.imgs = files
            self.label_imgs.setText(f'{len(files)} imagem(ns) selecionada(s)')
        else:
            self.imgs = []
            self.label_imgs.setText('Nenhuma imagem selecionada.')
    def exec_redimensionar(self):
        if not self.imgs:
            QMessageBox.warning(self, 'Aviso', 'Selecione imagens primeiro.')
            return
        try:
            largura = int(self.input_largura.text())
            altura = int(self.input_altura.text())
        except Exception:
            QMessageBox.warning(self, 'Aviso', 'Digite largura e altura válidas.')
            return
        manter = self.chk_manter.currentIndex() == 0
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.btn_cancelar.setVisible(True)
        self.result_list.clear()
        self.worker = RedimensionarWorker(self.imgs, largura, altura, manter)
        self.worker.progresso.connect(self.progress.setValue)
        self.worker.resultado.connect(self.redim_finalizado)
        self.worker.erro.connect(self.redim_erro)
        self.worker.start()
    def cancelar_redim(self):
        if self.worker:
            self.worker.cancelar()
    def redim_finalizado(self, resultados):
        self.progress.setVisible(False)
        self.btn_cancelar.setVisible(False)
        for inp, out in resultados:
            self.result_list.addItem(f'{os.path.basename(inp)} → {os.path.basename(out)}')
        QMessageBox.information(self, 'Redimensionamento', 'Redimensionamento concluído!')
    def redim_erro(self, exc):
        from log_utils import registrar_erro
        registrar_erro(exc, contexto='Redimensionamento de imagens')
        self.progress.setVisible(False)
        self.btn_cancelar.setVisible(False)
        QMessageBox.critical(self, 'Erro', f'Erro no redimensionamento:\n{str(exc)}\n')

class PDFTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Manipulação de PDFs'))
        self.combo_funcao = QComboBox()
        self.combo_funcao.addItems([
            'Selecione a função...',
            'Dividir PDF',
            'Mesclar PDFs',
            'Imagens para PDF',
            'Extrair texto de PDF',
            'OCR: Extrair texto de imagem',
            'OCR: Extrair texto de PDF',
            'DOCX para PDF',
            'PDF para DOCX'
        ])
        self.combo_funcao.currentIndexChanged.connect(self.trocar_funcao)
        layout.addWidget(self.combo_funcao)
        self.stacked = QStackedWidget()
        # --- Página Dividir PDF ---
        div_widget = QWidget()
        div_group = QVBoxLayout(div_widget)
        div_group.addWidget(QLabel('Dividir PDF'))
        hdiv = QHBoxLayout()
        self.btn_dividir_pdf = QPushButton('Escolher PDF')
        self.btn_dividir_pdf.clicked.connect(self.select_pdf_dividir)
        hdiv.addWidget(self.btn_dividir_pdf)
        self.label_pdf_dividir = QLabel('Nenhum PDF selecionado.')
        hdiv.addWidget(self.label_pdf_dividir)
        div_group.addLayout(hdiv)
        self.input_paginas = QComboBox()
        self.input_paginas.setEditable(True)
        self.input_paginas.addItems(['1', '2', '5', '10'])
        div_group.addWidget(QLabel('Páginas por arquivo:'))
        div_group.addWidget(self.input_paginas)
        self.btn_exec_dividir = QPushButton('Dividir')
        self.btn_exec_dividir.clicked.connect(self.dividir_pdf)
        div_group.addWidget(self.btn_exec_dividir)
        self.list_divididos = QListWidget()
        div_group.addWidget(self.list_divididos)
        self.div_widget = div_widget
        self.stacked.addWidget(div_widget)
        # --- Página Mesclar PDFs ---
        merge_widget = QWidget()
        merge_group = QVBoxLayout(merge_widget)
        merge_group.addWidget(QLabel('Mesclar PDFs'))
        hmerge = QHBoxLayout()
        self.btn_mesclar_pdfs = QPushButton('Escolher PDFs')
        self.btn_mesclar_pdfs.clicked.connect(self.select_pdfs_mesclar)
        hmerge.addWidget(self.btn_mesclar_pdfs)
        self.label_pdfs_mesclar = QLabel('Nenhum PDF selecionado.')
        hmerge.addWidget(self.label_pdfs_mesclar)
        merge_group.addLayout(hmerge)
        self.btn_exec_mesclar = QPushButton('Mesclar')
        self.btn_exec_mesclar.clicked.connect(self.mesclar_pdfs)
        merge_group.addWidget(self.btn_exec_mesclar)
        self.label_merged = QLabel('')
        merge_group.addWidget(self.label_merged)
        self.merge_widget = merge_widget
        self.stacked.addWidget(merge_widget)
        # --- Página Imagens para PDF ---
        img2pdf_widget = QWidget()
        img2pdf_group = QVBoxLayout(img2pdf_widget)
        img2pdf_group.addWidget(QLabel('Imagens para PDF'))
        himg = QHBoxLayout()
        self.btn_imgs2pdf = QPushButton('Escolher Imagens')
        self.btn_imgs2pdf.clicked.connect(self.select_imgs2pdf)
        himg.addWidget(self.btn_imgs2pdf)
        self.label_imgs2pdf = QLabel('Nenhuma imagem selecionada.')
        himg.addWidget(self.label_imgs2pdf)
        img2pdf_group.addLayout(himg)
        self.btn_exec_imgs2pdf = QPushButton('Converter para PDF')
        self.btn_exec_imgs2pdf.clicked.connect(self.imgs2pdf)
        img2pdf_group.addWidget(self.btn_exec_imgs2pdf)
        self.label_img2pdf = QLabel('')
        img2pdf_group.addWidget(self.label_img2pdf)
        self.img2pdf_widget = img2pdf_widget
        self.stacked.addWidget(img2pdf_widget)
        # --- Página Extração de texto ---
        extr_widget = QWidget()
        extr_group = QVBoxLayout(extr_widget)
        extr_group.addWidget(QLabel('Extrair texto de PDF'))
        hextr = QHBoxLayout()
        self.btn_extrair_pdf = QPushButton('Escolher PDF')
        self.btn_extrair_pdf.clicked.connect(self.select_pdf_extrair)
        hextr.addWidget(self.btn_extrair_pdf)
        self.label_pdf_extrair = QLabel('Nenhum PDF selecionado.')
        hextr.addWidget(self.label_pdf_extrair)
        extr_group.addLayout(hextr)
        self.btn_exec_extrair = QPushButton('Extrair texto')
        self.btn_exec_extrair.clicked.connect(self.extrair_texto)
        extr_group.addWidget(self.btn_exec_extrair)
        self.texto_extraido = QListWidget()
        extr_group.addWidget(self.texto_extraido)
        self.extr_widget = extr_widget
        self.stacked.addWidget(extr_widget)
        # --- Página OCR: Imagem ---
        ocrimg_widget = QWidget()
        ocrimg_layout = QVBoxLayout(ocrimg_widget)
        ocrimg_layout.addWidget(QLabel('OCR: Extrair texto de Imagem'))
        hocrimg = QHBoxLayout()
        self.btn_ocrimg = QPushButton('Escolher Imagem')
        self.btn_ocrimg.clicked.connect(self.select_ocrimg)
        hocrimg.addWidget(self.btn_ocrimg)
        self.label_ocrimg = QLabel('Nenhuma imagem selecionada.')
        hocrimg.addWidget(self.label_ocrimg)
        ocrimg_layout.addLayout(hocrimg)
        self.btn_exec_ocrimg = QPushButton('Executar OCR')
        self.btn_exec_ocrimg.clicked.connect(self.exec_ocrimg)
        ocrimg_layout.addWidget(self.btn_exec_ocrimg)
        self.ocrimg_result = QListWidget()
        ocrimg_layout.addWidget(self.ocrimg_result)
        self.ocrimg_widget = ocrimg_widget
        self.stacked.addWidget(ocrimg_widget)
        # --- Página OCR: PDF ---
        ocrpdf_widget = QWidget()
        ocrpdf_layout = QVBoxLayout(ocrpdf_widget)
        ocrpdf_layout.addWidget(QLabel('OCR: Extrair texto de PDF (imagens)'))
        hocpdf = QHBoxLayout()
        self.btn_ocrpdf = QPushButton('Escolher PDF')
        self.btn_ocrpdf.clicked.connect(self.select_ocrpdf)
        hocpdf.addWidget(self.btn_ocrpdf)
        self.label_ocrpdf = QLabel('Nenhum PDF selecionado.')
        hocpdf.addWidget(self.label_ocrpdf)
        ocrpdf_layout.addLayout(hocpdf)
        self.btn_exec_ocrpdf = QPushButton('Executar OCR')
        self.btn_exec_ocrpdf.clicked.connect(self.exec_ocrpdf)
        ocrpdf_layout.addWidget(self.btn_exec_ocrpdf)
        self.ocrpdf_result = QListWidget()
        ocrpdf_layout.addWidget(self.ocrpdf_result)
        self.btn_ocrpdf_to_pdf = QPushButton('Gerar PDF com texto extraído (OCR)')
        self.btn_ocrpdf_to_pdf.clicked.connect(self.ocrpdf_to_pdf)
        ocrpdf_layout.addWidget(self.btn_ocrpdf_to_pdf)
        self.label_ocrpdf_to_pdf = QLabel('')
        ocrpdf_layout.addWidget(self.label_ocrpdf_to_pdf)
        self.ocrpdf_widget = ocrpdf_widget
        self.stacked.addWidget(ocrpdf_widget)
        # --- Página DOCX para PDF ---
        docx2pdf_widget = QWidget()
        docx2pdf_layout = QVBoxLayout(docx2pdf_widget)
        docx2pdf_layout.addWidget(QLabel('Converter DOCX para PDF'))
        hdocx = QHBoxLayout()
        self.btn_docx2pdf = QPushButton('Escolher DOCX')
        self.btn_docx2pdf.clicked.connect(self.select_docx2pdf)
        hdocx.addWidget(self.btn_docx2pdf)
        self.label_docx2pdf = QLabel('Nenhum arquivo selecionado.')
        hdocx.addWidget(self.label_docx2pdf)
        docx2pdf_layout.addLayout(hdocx)
        self.btn_exec_docx2pdf = QPushButton('Converter para PDF')
        self.btn_exec_docx2pdf.clicked.connect(self.exec_docx2pdf)
        docx2pdf_layout.addWidget(self.btn_exec_docx2pdf)
        self.label_docx2pdf_result = QLabel('')
        docx2pdf_layout.addWidget(self.label_docx2pdf_result)
        self.docx2pdf_widget = docx2pdf_widget
        self.stacked.addWidget(docx2pdf_widget)
        # --- Página PDF para DOCX ---
        pdf2docx_widget = QWidget()
        pdf2docx_layout = QVBoxLayout(pdf2docx_widget)
        pdf2docx_layout.addWidget(QLabel('Converter PDF para DOCX'))
        hpdfdocx = QHBoxLayout()
        self.btn_pdf2docx = QPushButton('Escolher PDF')
        self.btn_pdf2docx.clicked.connect(self.select_pdf2docx)
        hpdfdocx.addWidget(self.btn_pdf2docx)
        self.label_pdf2docx = QLabel('Nenhum arquivo selecionado.')
        hpdfdocx.addWidget(self.label_pdf2docx)
        pdf2docx_layout.addLayout(hpdfdocx)
        self.btn_exec_pdf2docx = QPushButton('Converter para DOCX')
        self.btn_exec_pdf2docx.clicked.connect(self.exec_pdf2docx)
        pdf2docx_layout.addWidget(self.btn_exec_pdf2docx)
        self.label_pdf2docx_result = QLabel('')
        pdf2docx_layout.addWidget(self.label_pdf2docx_result)
        self.pdf2docx_widget = pdf2docx_widget
        self.stacked.addWidget(pdf2docx_widget)
        # Inicialmente, nenhuma página
        self.stacked.setCurrentIndex(-1)
        layout.addWidget(self.stacked)
        self.setLayout(layout)
        # variáveis de estado
        self.pdf_dividir = ''
        self.pdfs_mesclar = []
        self.imgs2pdf = []
        self.pdf_extrair = ''
        self.ocrimg_path = ''
        self.ocrpdf_path = ''
        self.docx2pdf_path = ''
        self.pdf2docx_path = ''

    def trocar_funcao(self, idx):
        if idx <= 0:
            self.stacked.setCurrentIndex(-1)
        else:
            self.stacked.setCurrentIndex(idx-1)

    def select_pdf_dividir(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Escolha um PDF para dividir', '', 'PDF (*.pdf)')
        if file:
            self.pdf_dividir = file
            self.label_pdf_dividir.setText(os.path.basename(file))
        else:
            self.pdf_dividir = ''
            self.label_pdf_dividir.setText('Nenhum PDF selecionado.')

    def dividir_pdf(self):
        if not self.pdf_dividir:
            QMessageBox.warning(self, 'Aviso', 'Selecione um PDF primeiro.')
            return
        try:
            n = int(self.input_paginas.currentText())
            arquivos = dividir_pdf(self.pdf_dividir, paginas_por_arquivo=n)
            self.list_divididos.clear()
            for a in arquivos:
                self.list_divididos.addItem(a)
            QMessageBox.information(self, 'Sucesso', f'{len(arquivos)} arquivos criados.')
        except Exception as e:
            registrar_erro(e, contexto='Dividir PDF')
            QMessageBox.critical(self, 'Erro', f'Erro ao dividir PDF:\n{str(e)}')

    def select_pdfs_mesclar(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Escolha PDFs para mesclar', '', 'PDF (*.pdf)')
        if files:
            self.pdfs_mesclar = files
            self.label_pdfs_mesclar.setText(f'{len(files)} arquivos selecionados.')
        else:
            self.pdfs_mesclar = []
            self.label_pdfs_mesclar.setText('Nenhum PDF selecionado.')

    def mesclar_pdfs(self):
        if not self.pdfs_mesclar:
            QMessageBox.warning(self, 'Aviso', 'Selecione PDFs primeiro.')
            return
        try:
            out_path = QFileDialog.getSaveFileName(self, 'Salvar PDF Mesclado', '', 'PDF (*.pdf)')[0]
            if not out_path:
                return
            mesclar_pdfs(self.pdfs_mesclar, out_path)
            self.label_merged.setText(f'PDF mesclado salvo em: {out_path}')
        except Exception as e:
            registrar_erro(e, contexto='Mesclar PDFs')
            QMessageBox.critical(self, 'Erro', f'Erro ao mesclar PDFs:\n{str(e)}')

    def select_imgs2pdf(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Escolha imagens para PDF', '', 'Imagens (*.png *.jpg *.jpeg *.jfif *.bmp *.gif *.webp)')
        if files:
            self.imgs2pdf = files
            self.label_imgs2pdf.setText(f'{len(files)} imagens selecionadas.')
        else:
            self.imgs2pdf = []
            self.label_imgs2pdf.setText('Nenhuma imagem selecionada.')

    def imgs2pdf(self):
        if not self.imgs2pdf:
            QMessageBox.warning(self, 'Aviso', 'Selecione imagens primeiro.')
            return
        try:
            out_path = QFileDialog.getSaveFileName(self, 'Salvar PDF', '', 'PDF (*.pdf)')[0]
            if not out_path:
                return
            imagens_para_pdf(self.imgs2pdf, out_path)
            self.label_img2pdf.setText(f'PDF salvo em: {out_path}')
        except Exception as e:
            registrar_erro(e, contexto='Converter imagens para PDF')
            QMessageBox.critical(self, 'Erro', f'Erro ao converter para PDF:\n{str(e)}')

    def select_pdf_extrair(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Escolha um PDF para extrair texto', '', 'PDF (*.pdf)')
        if file:
            self.pdf_extrair = file
            self.label_pdf_extrair.setText(os.path.basename(file))
        else:
            self.pdf_extrair = ''
            self.label_pdf_extrair.setText('Nenhum PDF selecionado.')

    def extrair_texto(self):
        if not self.pdf_extrair:
            QMessageBox.warning(self, 'Aviso', 'Selecione um PDF primeiro.')
            return
        try:
            texto = extrair_texto_pdf(self.pdf_extrair)
            self.texto_extraido.clear()
            for linha in texto.splitlines():
                self.texto_extraido.addItem(linha)
            QMessageBox.information(self, 'Extração concluída', 'Texto extraído do PDF.')
        except Exception as e:
            registrar_erro(e, contexto='Extrair texto de PDF')
            QMessageBox.critical(self, 'Erro', f'Erro ao extrair texto:\n{str(e)}')

    def select_ocrimg(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Escolha uma imagem', '', 'Imagens (*.png *.jpg *.jpeg *.jfif *.bmp *.gif *.webp)')
        if file:
            self.ocrimg_path = file
            self.label_ocrimg.setText(os.path.basename(file))
        else:
            self.ocrimg_path = ''
            self.label_ocrimg.setText('Nenhuma imagem selecionada.')

    def exec_ocrimg(self):
        if not self.ocrimg_path:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma imagem primeiro.')
            return
        try:
            texto = ocr_imagem(self.ocrimg_path, lang='eng')
            self.ocrimg_result.clear()
            for linha in texto.splitlines():
                self.ocrimg_result.addItem(linha)
            QMessageBox.information(self, 'OCR concluído', 'Texto extraído da imagem.')
        except Exception as e:
            registrar_erro(e, contexto='OCR de imagem')
            QMessageBox.critical(self, 'Erro', f'Erro no OCR da imagem:\n{str(e)}')

    def select_ocrpdf(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Escolha um PDF', '', 'PDF (*.pdf)')
        if file:
            self.ocrpdf_path = file
            self.label_ocrpdf.setText(os.path.basename(file))
        else:
            self.ocrpdf_path = ''
            self.label_ocrpdf.setText('Nenhum PDF selecionado.')

    def exec_ocrpdf(self):
        if not self.ocrpdf_path:
            QMessageBox.warning(self, 'Aviso', 'Selecione um PDF primeiro.')
            return
        try:
            resultados = ocr_pdf(self.ocrpdf_path, lang='eng')
            self.ocrpdf_result.clear()
            for pag, texto in resultados:
                self.ocrpdf_result.addItem(f'--- Página {pag} ---')
                for linha in texto.splitlines():
                    self.ocrpdf_result.addItem(linha)
            QMessageBox.information(self, 'OCR concluído', 'Texto extraído das imagens do PDF.')
        except Exception as e:
            registrar_erro(e, contexto='OCR de PDF')
            QMessageBox.critical(self, 'Erro', f'Erro no OCR do PDF:\n{str(e)}')

    def ocrpdf_to_pdf(self):
        if not self.ocrpdf_path:
            QMessageBox.warning(self, 'Aviso', 'Selecione um PDF primeiro.')
            return
        try:
            out_path = QFileDialog.getSaveFileName(self, 'Salvar PDF OCR', '', 'PDF (*.pdf)')[0]
            if not out_path:
                return
            ocr_pdf_to_pdf(self.ocrpdf_path, out_path, lang='eng')
            self.label_ocrpdf_to_pdf.setText(f'PDF OCR salvo em: {out_path}')
            QMessageBox.information(self, 'PDF OCR', 'PDF com texto extraído salvo com sucesso!')
        except Exception as e:
            registrar_erro(e, contexto='Gerar PDF OCR')
            QMessageBox.critical(self, 'Erro', f'Erro ao gerar PDF OCR:\n{str(e)}')

    def select_docx2pdf(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Escolha um arquivo DOCX', '', 'DOCX (*.docx)')
        if file:
            self.docx2pdf_path = file
            self.label_docx2pdf.setText(os.path.basename(file))
        else:
            self.docx2pdf_path = ''
            self.label_docx2pdf.setText('Nenhum arquivo selecionado.')

    def exec_docx2pdf(self):
        if not hasattr(self, 'docx2pdf_path') or not self.docx2pdf_path:
            QMessageBox.warning(self, 'Aviso', 'Selecione um arquivo DOCX primeiro.')
            return
        try:
            out_path = QFileDialog.getSaveFileName(self, 'Salvar PDF', '', 'PDF (*.pdf)')[0]
            if not out_path:
                return
            docx_para_pdf(self.docx2pdf_path, out_path)
            self.label_docx2pdf_result.setText(f'PDF salvo em: {out_path}')
            QMessageBox.information(self, 'Conversão', 'DOCX convertido para PDF com sucesso!')
        except Exception as e:
            registrar_erro(e, contexto='Converter DOCX para PDF')
            QMessageBox.critical(self, 'Erro', f'Erro ao converter DOCX para PDF:\n{str(e)}')

    def select_pdf2docx(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Escolha um arquivo PDF', '', 'PDF (*.pdf)')
        if file:
            self.pdf2docx_path = file
            self.label_pdf2docx.setText(os.path.basename(file))
        else:
            self.pdf2docx_path = ''
            self.label_pdf2docx.setText('Nenhum arquivo selecionado.')

    def exec_pdf2docx(self):
        if not hasattr(self, 'pdf2docx_path') or not self.pdf2docx_path:
            QMessageBox.warning(self, 'Aviso', 'Selecione um arquivo PDF primeiro.')
            return
        try:
            out_path = QFileDialog.getSaveFileName(self, 'Salvar DOCX', '', 'DOCX (*.docx)')[0]
            if not out_path:
                return
            pdf_para_docx(self.pdf2docx_path, out_path)
            self.label_pdf2docx_result.setText(f'DOCX salvo em: {out_path}')
            QMessageBox.information(self, 'Conversão', 'PDF convertido para DOCX com sucesso!')
        except Exception as e:
            registrar_erro(e, contexto='Converter PDF para DOCX')
            QMessageBox.critical(self, 'Erro', f'Erro ao converter PDF para DOCX:\n{str(e)}')

class RelatorioWorker(QThread):
    progresso = pyqtSignal(int)
    resultado = pyqtSignal(object)
    erro = pyqtSignal(Exception)
    def __init__(self, pasta, n_maiores=5):
        super().__init__()
        self.pasta = pasta
        self.n_maiores = n_maiores
        self._cancelado = False
    def cancelar(self):
        self._cancelado = True
    def run(self):
        try:
            from relatorio_utils import analisar_pasta
            def on_progress(pct):
                self.progresso.emit(pct)
                if self._cancelado:
                    raise Exception('Operação cancelada pelo usuário.')
            resultado = analisar_pasta(self.pasta, self.n_maiores, on_progress=on_progress)
            self.resultado.emit(resultado)
        except Exception as e:
            self.erro.emit(e)

class RelatorioTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Gerador de Relatórios Automáticos'))
        hbox = QHBoxLayout()
        self.btn_select = QPushButton('Selecionar Pasta')
        self.btn_select.clicked.connect(self.select_folder)
        hbox.addWidget(self.btn_select)
        self.label_pasta = QLabel('Nenhuma pasta selecionada.')
        hbox.addWidget(self.label_pasta)
        layout.addLayout(hbox)
        self.btn_analisar = QPushButton('Analisar e Gerar Relatório')
        self.btn_analisar.clicked.connect(self.analisar)
        self.btn_analisar.setEnabled(False)
        layout.addWidget(self.btn_analisar)
        self.combo_saida = QComboBox()
        self.combo_saida.addItems(['HTML', 'PDF'])
        layout.addWidget(QLabel('Formato do Relatório:'))
        layout.addWidget(self.combo_saida)
        self.list_resumo = QListWidget()
        layout.addWidget(self.list_resumo)
        self.btn_salvar = QPushButton('Salvar Relatório')
        self.btn_salvar.clicked.connect(self.gerar_relatorio)
        self.btn_salvar.setEnabled(False)
        layout.addWidget(self.btn_salvar)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.btn_cancelar = QPushButton('Cancelar')
        self.btn_cancelar.setVisible(False)
        self.btn_cancelar.clicked.connect(self.cancelar_analise)
        layout.addWidget(self.btn_cancelar)
        self.setLayout(layout)
        self.pasta = ''
        self.tipos = None
        self.total_arquivos = 0
        self.total_tamanho = 0
        self.n_subpastas = 0
        self.maior_sub = None
        self.menor_sub = None
        self.maiores_subs = None
        self.profundidade_max = 0
        self.worker = None

    def select_folder(self):
        pasta = QFileDialog.getExistingDirectory(self, 'Selecione a pasta para análise')
        if pasta:
            self.pasta = pasta
            self.label_pasta.setText(pasta)
            self.btn_analisar.setEnabled(True)
            self.btn_salvar.setEnabled(False)
            self.list_resumo.clear()
        else:
            self.pasta = ''
            self.label_pasta.setText('Nenhuma pasta selecionada.')
            self.btn_analisar.setEnabled(False)
            self.btn_salvar.setEnabled(False)
            self.list_resumo.clear()

    def analisar(self):
        if not self.pasta:
            return
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.btn_cancelar.setVisible(True)
        self.btn_analisar.setEnabled(False)
        self.worker = RelatorioWorker(self.pasta, n_maiores=5)
        self.worker.resultado.connect(self.analisar_finalizado)
        self.worker.erro.connect(self.analisar_erro)
        self.worker.progresso.connect(self.progress.setValue)
        self.worker.start()

    def cancelar_analise(self):
        if self.worker:
            self.worker.cancelar()

    def analisar_finalizado(self, resultado):
        (
            self.tipos, self.total_arquivos, self.total_tamanho,
            self.n_subpastas, self.maior_sub, self.menor_sub,
            self.maiores_subs, self.profundidade_max
        ) = resultado
        self.progress.setVisible(False)
        self.btn_cancelar.setVisible(False)
        self.btn_analisar.setEnabled(True)
        self.list_resumo.clear()
        self.list_resumo.addItem(f'Total de arquivos: {self.total_arquivos}')
        self.list_resumo.addItem(f'Tamanho total: {self.total_tamanho/1024/1024:.2f} MB')
        self.list_resumo.addItem(f'Total de subpastas: {self.n_subpastas}')
        self.list_resumo.addItem(f'Profundidade máxima: {self.profundidade_max}')
        if self.n_subpastas > 0:
            if self.maiores_subs:
                self.list_resumo.addItem('Maiores subpastas:')
                for sub, tam in self.maiores_subs:
                    self.list_resumo.addItem(f'  {os.path.relpath(sub, self.pasta)}: {tam/1024/1024:.2f} MB')
            if self.maior_sub and self.maior_sub[0]:
                self.list_resumo.addItem(f'Subpasta maior: {os.path.relpath(self.maior_sub[0], self.pasta)} ({self.maior_sub[1]/1024/1024:.2f} MB)')
            if self.menor_sub and self.menor_sub[0]:
                self.list_resumo.addItem(f'Subpasta menor: {os.path.relpath(self.menor_sub[0], self.pasta)} ({self.menor_sub[1]/1024/1024:.2f} MB)')
        for ext, info in sorted(self.tipos.items(), key=lambda x: -x[1]['quantidade']):
            self.list_resumo.addItem(f'{ext}: {info["quantidade"]} arquivos, {info["tamanho"]/1024/1024:.2f} MB')
        self.btn_salvar.setEnabled(True)

    def analisar_erro(self, exc):
        from log_utils import registrar_erro
        registrar_erro(exc, contexto='Análise de pasta/relatório')
        self.progress.setVisible(False)
        self.btn_cancelar.setVisible(False)
        self.btn_analisar.setEnabled(True)
        QMessageBox.critical(self, 'Erro', f'Erro na análise da pasta:\n{str(exc)}')

    def gerar_relatorio(self):
        if not self.pasta or not self.tipos:
            return
        fmt = self.combo_saida.currentText()
        grafico_b64 = gerar_grafico_pizza(self.tipos)
        if fmt == 'HTML':
            out_path, _ = QFileDialog.getSaveFileName(self, 'Salvar Relatório HTML', '', 'HTML (*.html)')
            if not out_path:
                return
            gerar_relatorio_html(
                self.pasta, self.tipos, self.total_arquivos, self.total_tamanho, out_path,
                self.n_subpastas, self.maior_sub, self.menor_sub, self.maiores_subs, self.profundidade_max, grafico_b64
            )
            QMessageBox.information(self, 'Relatório', f'Relatório HTML salvo em: {out_path}')
        else:
            out_path, _ = QFileDialog.getSaveFileName(self, 'Salvar Relatório PDF', '', 'PDF (*.pdf)')
            if not out_path:
                return
            gerar_relatorio_pdf(
                self.pasta, self.tipos, self.total_arquivos, self.total_tamanho, out_path,
                self.n_subpastas, self.maior_sub, self.menor_sub, self.maiores_subs, self.profundidade_max
            )
            QMessageBox.information(self, 'Relatório', f'Relatório PDF salvo em: {out_path}')

class LogsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Logs do Sistema'))
        filtro_layout = QHBoxLayout()
        self.input_data = QLineEdit()
        self.input_data.setPlaceholderText('Filtrar por data (AAAA-MM-DD)')
        self.input_tipo = QComboBox()
        self.input_tipo.addItems(['', 'INFO', 'ERRO', 'WARNING'])
        self.btn_filtrar = QPushButton('Filtrar')
        self.btn_filtrar.clicked.connect(self.carregar_logs)
        filtro_layout.addWidget(self.input_data)
        filtro_layout.addWidget(self.input_tipo)
        filtro_layout.addWidget(self.btn_filtrar)
        layout.addLayout(filtro_layout)
        self.list_logs = QListWidget()
        layout.addWidget(self.list_logs)
        self.btn_refresh = QPushButton('Atualizar')
        self.btn_refresh.clicked.connect(self.carregar_logs)
        layout.addWidget(self.btn_refresh)
        self.btn_exportar = QPushButton('Exportar Logs')
        self.btn_exportar.clicked.connect(self.exportar_logs)
        layout.addWidget(self.btn_exportar)
        self.setLayout(layout)
        self.carregar_logs()

    def carregar_logs(self):
        data = self.input_data.text().strip()
        tipo = self.input_tipo.currentText().strip() or None
        self.list_logs.clear()
        for linha in ler_logs(filtro_data=data if data else None, filtro_tipo=tipo):
            self.list_logs.addItem(linha.strip())

    def exportar_logs(self):
        caminho, _ = QFileDialog.getSaveFileName(self, 'Exportar Logs', '', 'TXT (*.txt)')
        if not caminho:
            return
        if exportar_logs(caminho):
            QMessageBox.information(self, 'Exportação', f'Logs exportados para: {caminho}')
        else:
            QMessageBox.warning(self, 'Exportação', 'Nenhum log para exportar.')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Suite de Utilitários')
        self.setGeometry(150, 150, 700, 550)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        self.dock = QDockWidget('Funcionalidades', self)
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        dock_widget = QWidget()
        dock_layout = QVBoxLayout()
        self.btn_abrir_organizador = QPushButton('Organizador de Arquivos')
        self.btn_abrir_organizador.clicked.connect(self.open_organizador_tab)
        dock_layout.addWidget(self.btn_abrir_organizador)
        self.btn_abrir_ocrimg = QPushButton('OCR de Imagens')
        self.btn_abrir_ocrimg.clicked.connect(self.open_ocrimg_tab)
        dock_layout.addWidget(self.btn_abrir_ocrimg)
        self.btn_abrir_conversor = QPushButton('Conversor de Imagem')
        self.btn_abrir_conversor.clicked.connect(self.open_conversor_tab)
        dock_layout.addWidget(self.btn_abrir_conversor)
        self.btn_abrir_renomeador = QPushButton('Renomeador de Arquivos')
        self.btn_abrir_renomeador.clicked.connect(self.open_renomeador_tab)
        dock_layout.addWidget(self.btn_abrir_renomeador)
        self.btn_abrir_redimensionador = QPushButton('Redimensionador de Imagens')
        self.btn_abrir_redimensionador.clicked.connect(self.open_redimensionador_tab)
        dock_layout.addWidget(self.btn_abrir_redimensionador)
        self.btn_abrir_pdf = QPushButton('Manipulação de PDFs')
        self.btn_abrir_pdf.clicked.connect(self.open_pdf_tab)
        dock_layout.addWidget(self.btn_abrir_pdf)
        self.btn_abrir_relatorio = QPushButton('Gerador de Relatórios')
        self.btn_abrir_relatorio.clicked.connect(self.open_relatorio_tab)
        dock_layout.addWidget(self.btn_abrir_relatorio)
        self.btn_abrir_logs = QPushButton('Logs do Sistema')
        self.btn_abrir_logs.clicked.connect(self.open_logs_tab)
        dock_layout.addWidget(self.btn_abrir_logs)
        dock_layout.addStretch()
        dock_widget.setLayout(dock_layout)
        self.dock.setWidget(dock_widget)
        self.open_tabs = {}

    def open_organizador_tab(self):
        if 'organizador' not in self.open_tabs:
            tab = OrganizadorTab()
            idx = self.tabs.addTab(tab, 'Organizador de Arquivos')
            self.tabs.setCurrentIndex(idx)
            self.open_tabs['organizador'] = tab
        else:
            idx = self.tabs.indexOf(self.open_tabs['organizador'])
            self.tabs.setCurrentIndex(idx)

    def open_ocrimg_tab(self):
        if 'ocrimg' not in self.open_tabs:
            tab = OCRImagemTab()
            idx = self.tabs.addTab(tab, 'OCR de Imagens')
            self.tabs.setCurrentIndex(idx)
            self.open_tabs['ocrimg'] = tab
        else:
            idx = self.tabs.indexOf(self.open_tabs['ocrimg'])
            self.tabs.setCurrentIndex(idx)

    def open_conversor_tab(self):
        if 'conversor' not in self.open_tabs:
            tab = ConversorTab()
            idx = self.tabs.addTab(tab, 'Conversor de Imagem')
            self.tabs.setCurrentIndex(idx)
            self.open_tabs['conversor'] = tab
        else:
            idx = self.tabs.indexOf(self.open_tabs['conversor'])
            self.tabs.setCurrentIndex(idx)

    def open_renomeador_tab(self):
        if 'renomeador' not in self.open_tabs:
            tab = RenomeadorTab()
            idx = self.tabs.addTab(tab, 'Renomeador de Arquivos')
            self.tabs.setCurrentIndex(idx)
            self.open_tabs['renomeador'] = tab
        else:
            idx = self.tabs.indexOf(self.open_tabs['renomeador'])
            self.tabs.setCurrentIndex(idx)

    def open_redimensionador_tab(self):
        if 'redimensionador' not in self.open_tabs:
            tab = RedimensionadorTab()
            idx = self.tabs.addTab(tab, 'Redimensionador de Imagens')
            self.tabs.setCurrentIndex(idx)
            self.open_tabs['redimensionador'] = tab
        else:
            idx = self.tabs.indexOf(self.open_tabs['redimensionador'])
            self.tabs.setCurrentIndex(idx)

    def open_pdf_tab(self):
        if 'pdf' not in self.open_tabs:
            tab = PDFTab()
            idx = self.tabs.addTab(tab, 'Manipulação de PDFs')
            self.tabs.setCurrentIndex(idx)
            self.open_tabs['pdf'] = tab
        else:
            idx = self.tabs.indexOf(self.open_tabs['pdf'])
            self.tabs.setCurrentIndex(idx)

    def open_relatorio_tab(self):
        if 'relatorio' not in self.open_tabs:
            tab = RelatorioTab()
            idx = self.tabs.addTab(tab, 'Gerador de Relatórios')
            self.tabs.setCurrentIndex(idx)
            self.open_tabs['relatorio'] = tab
        else:
            idx = self.tabs.indexOf(self.open_tabs['relatorio'])
            self.tabs.setCurrentIndex(idx)

    def open_logs_tab(self):
        if 'logs' not in self.open_tabs:
            tab = LogsTab()
            idx = self.tabs.addTab(tab, 'Logs do Sistema')
            self.tabs.setCurrentIndex(idx)
            self.open_tabs['logs'] = tab
        else:
            idx = self.tabs.indexOf(self.open_tabs['logs'])
            self.tabs.setCurrentIndex(idx)

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        for key, tab in list(self.open_tabs.items()):
            if tab == widget:
                del self.open_tabs[key]
        self.tabs.removeTab(index)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_STYLE)
    win = MainWindow()
    win.setWindowIcon(QIcon.fromTheme('applications-utilities'))
    win.show()
    sys.exit(app.exec())
