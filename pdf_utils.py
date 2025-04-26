from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import os
import pdfplumber

def dividir_pdf(input_pdf, paginas_por_arquivo=1):
    reader = PdfReader(input_pdf)
    arquivos = []
    for i in range(0, len(reader.pages), paginas_por_arquivo):
        writer = PdfWriter()
        for j in range(i, min(i+paginas_por_arquivo, len(reader.pages))):
            writer.add_page(reader.pages[j])
        out_path = f"{os.path.splitext(input_pdf)[0]}_parte_{i//paginas_por_arquivo+1}.pdf"
        with open(out_path, 'wb') as f:
            writer.write(f)
        arquivos.append(out_path)
    return arquivos

def mesclar_pdfs(lista_pdfs, output_pdf):
    writer = PdfWriter()
    for pdf in lista_pdfs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_pdf, 'wb') as f:
        writer.write(f)
    return output_pdf

def imagens_para_pdf(lista_imagens, output_pdf):
    imgs = [Image.open(img).convert('RGB') for img in lista_imagens]
    if imgs:
        imgs[0].save(output_pdf, save_all=True, append_images=imgs[1:])
    return output_pdf

def extrair_texto_pdf(input_pdf):
    texto = ''
    with pdfplumber.open(input_pdf) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() or ''
            texto += '\n'
    return texto
