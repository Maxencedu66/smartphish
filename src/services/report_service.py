from flask import send_file
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame, Spacer, BaseDocTemplate, PageTemplate
from reportlab.lib.units import inch
from src.routes.auth_routes import get_db_connection
import os


def download_report_styled(campaign_id):
    conn = get_db_connection()
    row = conn.execute("SELECT content FROM reports WHERE campaign_id = ?", (campaign_id,)).fetchone()
    conn.close()

    if not row:
        return "Rapport introuvable", 404

    content = row["content"]
    lines = content.split("\n")

    # Préparer le PDF
    buffer = BytesIO()
    width, height = A4
    margin = 50

    # Styles
    styles = getSampleStyleSheet()

    normal_style = ParagraphStyle(
        name="Normal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        spaceBefore=4
    )

    section_title_style = ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=20,
        textColor=colors.darkblue,
        spaceBefore=12,
        spaceAfter=6,
    )

    # Construction du contenu
    story = []

    # Ajout du logo et du titre sur chaque page
    def header_footer(canvas, doc):
        # Logo
        logo_path = "./src/static/img/logo.png"
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            canvas.drawImage(logo, margin, height - 70, width=80, preserveAspectRatio=True, mask='auto')

        # Titre centré
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawCentredString(width / 2, height - 50, "📄 Rapport de Campagne - SmartPhish")

        # Ligne de séparation
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(1)
        canvas.line(margin, height - 80, width - margin, height - 80)

        # Pied de page
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(width - margin, 20, f"Page {doc.page}")

    # Traitement des lignes
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 10))
            continue
        if line.lower().startswith("résultats") or \
           line.lower().startswith("analyse") or \
           line.lower().startswith("recommandations") or \
           line.lower().startswith("conclusion") or \
           line.lower().startswith("introduction"):
            story.append(Paragraph(line, section_title_style))
        else:
            story.append(Paragraph(line, normal_style))

    # Document
    doc = BaseDocTemplate(buffer, pagesize=A4,
                          leftMargin=margin, rightMargin=margin,
                          topMargin=120, bottomMargin=40)

    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id='normal')

    doc.addPageTemplates([PageTemplate(id='SmartPhish', frames=frame, onPage=header_footer)])

    # Génère le PDF
    doc.build(story)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name=f"rapport_campagne_{campaign_id}.pdf",
                     mimetype="application/pdf")
