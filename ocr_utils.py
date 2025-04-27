import pytesseract
from PIL import Image
import pdfplumber
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import csv
import pandas as pd

def ocr_imagem(path_img, lang='eng'):
    img = Image.open(path_img)
    texto = pytesseract.image_to_string(img, lang=lang)
    return texto

def ocr_pdf(path_pdf, lang='eng'):
    resultados = []
    with pdfplumber.open(path_pdf) as pdf:
        for i, page in enumerate(pdf.pages):
            im = page.to_image(resolution=300)
            img = im.original
            texto = pytesseract.image_to_string(img, lang=lang)
            resultados.append((i+1, texto))
    return resultados

def ocr_pdf_to_pdf(path_pdf, output_pdf, lang='eng'):
    """
    Realiza OCR em cada página do PDF e gera um novo PDF com o texto extraído, mantendo a separação de páginas.
    """
    resultados = ocr_pdf(path_pdf, lang=lang)
    c = canvas.Canvas(output_pdf, pagesize=A4)
    largura, altura = A4
    for pag, texto in resultados:
        y = altura - 40
        for linha in texto.splitlines():
            c.drawString(40, y, linha)
            y -= 18
            if y < 40:
                c.showPage()
                y = altura - 40
        c.showPage()
    c.save()
    return output_pdf

def ocr_layout(img_path, lang='por'):
    """
    Executa OCR avançado extraindo estrutura de tabelas/campos usando Tesseract (TSV).
    Retorna uma lista de linhas, cada linha é uma lista de células (strings).
    """
    img = Image.open(img_path)
    tsv = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DATAFRAME)
    # Agrupa por linha (usando 'line_num') e por bloco (separação de tabelas)
    linhas = []
    for (block_num, par_num, line_num), grupo in tsv.groupby(['block_num','par_num','line_num']):
        linha = []
        for _, row in grupo.iterrows():
            if isinstance(row['text'], str) and row['text'].strip():
                linha.append(row['text'].strip())
        if linha:
            linhas.append(linha)
    return linhas

def ocr_layout_pdf(pdf_path, lang='por', paginas=None):
    """
    Executa OCR avançado em PDF, extraindo tabelas/campos estruturados de cada página.
    Retorna lista de DataFrames (um por página).
    Se paginas=None, processa todas. Se for lista, processa apenas as páginas indicadas (1-based).
    """
    resultados = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        indices = range(total) if paginas is None else [p-1 for p in paginas]
        for i in indices:
            page = pdf.pages[i]
            img = page.to_image(resolution=300).original
            tsv = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DATAFRAME)
            linhas = []
            for (block_num, par_num, line_num), grupo in tsv.groupby(['block_num','par_num','line_num']):
                linha = []
                for _, row in grupo.iterrows():
                    if isinstance(row['text'], str) and row['text'].strip():
                        linha.append(row['text'].strip())
                if linha:
                    linhas.append(linha)
            if linhas:
                # Padroniza número de colunas
                max_cols = max(len(l) for l in linhas)
                dados = [l + ['']*(max_cols-len(l)) for l in linhas]
                df = pd.DataFrame(dados)
                resultados.append(df)
            else:
                resultados.append(pd.DataFrame())
    return resultados

# Exemplo de uso:
# linhas = ocr_layout('minha_imagem.png')
# for l in linhas: print(l)

# Exemplo de uso:
# dfs = ocr_layout_pdf('meu.pdf')
# dfs[0].to_csv('pagina1.csv', index=False)
