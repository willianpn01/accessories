import pytesseract
from PIL import Image
import pdfplumber
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

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
