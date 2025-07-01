

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import os

def exportar_relatórios_em_pdf(relatorios, nome_arquivo="relatorio"):
    nome_completo = f"{nome_arquivo}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf"
    caminho = os.path.join(os.getcwd(), nome_completo)

    c = canvas.Canvas(caminho, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, "Relatório de Dados do Condomínio")

    y = height - 3 * cm
    c.setFont("Helvetica", 12)

    for r in relatorios:

        titulo = r.get('titulo', 'Sem título')
        data = r.get('data', 'Sem data')
        descricao = r.get('descricao', 'Sem descrição')
       
        c.drawString(2 * cm, y, f"Título: {r['titulo']}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Data: {r['data']}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Descrição: {r['descricao']}")
        y -= 1 * cm

        if y < 3 * cm:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 2 * cm

    c.save()
    return caminho