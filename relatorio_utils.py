import os
from collections import defaultdict
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import io
import base64
from typing import Callable

def analisar_pasta(pasta, n_maiores=5, on_progress: Callable[[int], None]=None):
    tipos = defaultdict(lambda: {'quantidade': 0, 'tamanho': 0})
    total_arquivos = 0
    total_tamanho = 0
    subpastas = {}
    profundidades = []
    # Coleta todas as subpastas para granularidade
    all_dirs = []
    for root, dirs, files in os.walk(pasta):
        all_dirs.append(root)
    total_dirs = len(all_dirs)
    for idx, root in enumerate(all_dirs):
        # Progresso granular
        if on_progress and total_dirs > 0:
            on_progress(int((idx/total_dirs)*100))
        files = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
        if root != pasta:
            tamanho_sub = sum(os.path.getsize(os.path.join(root, f)) for f in files if os.path.isfile(os.path.join(root, f)))
            subpastas[root] = tamanho_sub
            profundidades.append(root[len(pasta):].count(os.sep))
        for f in files:
            ext = os.path.splitext(f)[1].lower() or 'Sem Extensão'
            caminho = os.path.join(root, f)
            try:
                tamanho = os.path.getsize(caminho)
            except Exception:
                tamanho = 0
            tipos[ext]['quantidade'] += 1
            tipos[ext]['tamanho'] += tamanho
            total_arquivos += 1
            total_tamanho += tamanho
    if on_progress:
        on_progress(100)
    n_subpastas = len(subpastas)
    maior_sub = max(subpastas.items(), key=lambda x: x[1], default=(None, 0))
    menor_sub = min(subpastas.items(), key=lambda x: x[1], default=(None, 0))
    maiores_subs = sorted(subpastas.items(), key=lambda x: -x[1])[:n_maiores]
    profundidade_max = max(profundidades) if profundidades else 0
    return tipos, total_arquivos, total_tamanho, n_subpastas, maior_sub, menor_sub, maiores_subs, profundidade_max

def gerar_grafico_pizza(tipos):
    labels = []
    sizes = []
    for ext, info in sorted(tipos.items(), key=lambda x: -x[1]['quantidade']):
        labels.append(ext)
        sizes.append(info['quantidade'])
    if not sizes:
        return None
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_b64

def gerar_relatorio_html(pasta, tipos, total_arquivos, total_tamanho, saida, n_subpastas=None, maior_sub=None, menor_sub=None, maiores_subs=None, profundidade_max=None, grafico_b64=None):
    dt = datetime.now().strftime('%d/%m/%Y %H:%M')
    html = f"""
    <html><head><meta charset='utf-8'><title>Relatório da Pasta</title>
    <style>
    body {{ font-family: Arial, sans-serif; background: #f8f8fa; color: #222; }}
    h1 {{ color: #4e6ef2; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
    th, td {{ border: 1px solid #aaa; padding: 8px; text-align: left; }}
    th {{ background: #4e6ef2; color: #fff; }}
    tr:nth-child(even) {{ background: #e7eaff; }}
    </style></head><body>
    <h1>Relatório da Pasta: {os.path.basename(pasta)}</h1>
    <p>Gerado em: {dt}</p>
    <p>Total de arquivos: <b>{total_arquivos}</b><br>Total de tamanho: <b>{total_tamanho/1024/1024:.2f} MB</b></p>
    """
    if n_subpastas is not None:
        html += f"<p>Total de subpastas: <b>{n_subpastas}</b></p>"
        if profundidade_max is not None:
            html += f"<p>Profundidade máxima de subpastas: <b>{profundidade_max}</b></p>"
        if maiores_subs:
            html += "<p>Maiores subpastas:</p><ul>"
            for sub, tam in maiores_subs:
                html += f"<li>{os.path.relpath(sub, pasta)}: {tam/1024/1024:.2f} MB</li>"
            html += "</ul>"
        if maior_sub and maior_sub[0]:
            html += f"<p>Subpasta com maior tamanho: <b>{os.path.relpath(maior_sub[0], pasta)}</b> ({maior_sub[1]/1024/1024:.2f} MB)</p>"
        if menor_sub and menor_sub[0]:
            html += f"<p>Subpasta com menor tamanho: <b>{os.path.relpath(menor_sub[0], pasta)}</b> ({menor_sub[1]/1024/1024:.2f} MB)</p>"
    if grafico_b64:
        html += f'<h3>Distribuição dos tipos de arquivo</h3><img src="data:image/png;base64,{grafico_b64}" style="max-width:500px;">'
    html += "<table><tr><th>Tipo</th><th>Quantidade</th><th>Tamanho Total (MB)</th></tr>"
    for ext, info in sorted(tipos.items(), key=lambda x: -x[1]['quantidade']):
        html += f"<tr><td>{ext}</td><td>{info['quantidade']}</td><td>{info['tamanho']/1024/1024:.2f}</td></tr>"
    html += "</table></body></html>"
    with open(saida, 'w', encoding='utf-8') as f:
        f.write(html)
    return saida

def gerar_relatorio_pdf(pasta, tipos, total_arquivos, total_tamanho, saida, n_subpastas=None, maior_sub=None, menor_sub=None, maiores_subs=None, profundidade_max=None):
    doc = SimpleDocTemplate(saida, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = []
    dt = datetime.now().strftime('%d/%m/%Y %H:%M')
    elems.append(Paragraph(f"Relatório da Pasta: <b>{os.path.basename(pasta)}</b>", styles['Title']))
    elems.append(Paragraph(f"Gerado em: {dt}", styles['Normal']))
    elems.append(Paragraph(f"Total de arquivos: <b>{total_arquivos}</b> &nbsp;&nbsp; Total de tamanho: <b>{total_tamanho/1024/1024:.2f} MB</b>", styles['Normal']))
    if n_subpastas is not None:
        elems.append(Paragraph(f"Total de subpastas: <b>{n_subpastas}</b>", styles['Normal']))
        if profundidade_max is not None:
            elems.append(Paragraph(f"Profundidade máxima de subpastas: <b>{profundidade_max}</b>", styles['Normal']))
        if maiores_subs:
            elems.append(Paragraph("Maiores subpastas:", styles['Normal']))
            for sub, tam in maiores_subs:
                elems.append(Paragraph(f"- {os.path.relpath(sub, pasta)}: {tam/1024/1024:.2f} MB", styles['Normal']))
        if maior_sub and maior_sub[0]:
            elems.append(Paragraph(f"Subpasta com maior tamanho: <b>{os.path.relpath(maior_sub[0], pasta)}</b> ({maior_sub[1]/1024/1024:.2f} MB)", styles['Normal']))
        if menor_sub and menor_sub[0]:
            elems.append(Paragraph(f"Subpasta com menor tamanho: <b>{os.path.relpath(menor_sub[0], pasta)}</b> ({menor_sub[1]/1024/1024:.2f} MB)", styles['Normal']))
    elems.append(Spacer(1, 18))
    data = [['Tipo', 'Quantidade', 'Tamanho Total (MB)']]
    for ext, info in sorted(tipos.items(), key=lambda x: -x[1]['quantidade']):
        data.append([ext, str(info['quantidade']), f"{info['tamanho']/1024/1024:.2f}"])
    t = Table(data, colWidths=[100, 100, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4e6ef2')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
    ]))
    elems.append(t)
    doc.build(elems)
    return saida
