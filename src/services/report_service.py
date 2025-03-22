from flask import send_file
from io import BytesIO
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from dateutil.parser import parse as parse_date
import os
import re
import locale

from src.routes.auth_routes import get_db_connection
from src.config import Config
from gophish import Gophish
from src.lib.goreport import Goreport


def download_report_styled(campaign_id):
    print("📄 Téléchargement du rapport DOCX stylisé pour la campagne", campaign_id)

    # Connexion à la base
    conn = get_db_connection()
    row = conn.execute("SELECT content FROM reports WHERE campaign_id = ?", (campaign_id,)).fetchone()
    campaign = conn.execute("SELECT name, created_date FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
    conn.close()

    if not row:
        return "Rapport introuvable", 404

    content = row["content"]
    lines = content.split("\n")
    campaign_name = campaign["name"] if campaign else f"Campagne {campaign_id}"

    # 🔤 Format de date lisible
    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "fr_FR")
        except locale.Error:
            print("⚠️ Locale FR non disponible, fallback anglais")

    if campaign and campaign["created_date"]:
        date_obj = parse_date(campaign["created_date"])
    else:
        date_obj = datetime.utcnow()

    campaign_date = date_obj.strftime("%-d %B %Y")  # Exemple : 8 mars 2025

    # 📊 Données GoPhish
    goreport = Goreport(report_format="word", config_file=None, google=False, verbose=False)
    goreport.api = Gophish(Config.GOPHISH_API_KEY, host=Config.GOPHISH_API_URL, verify=False)
    goreport.campaign = goreport.api.campaigns.get(campaign_id=campaign_id)
    goreport.collect_all_campaign_info(combine_reports=False)
    goreport.process_timeline_events(combine_reports=False)
    goreport.process_results(combine_reports=False)

    # 📄 Création document Word
    doc = Document()
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    section = doc.sections[0]
    header = section.header
    header_para = header.paragraphs[0]
    logo_path = "./src/static/img/logo.png"
    if os.path.exists(logo_path):
        run = header_para.add_run()
        run.add_picture(logo_path, width=Inches(0.7))
        header_para.alignment = WD_ALIGN_PARAGRAPH.LEFT

    title_para = doc.add_paragraph()
    title_run = title_para.add_run(f"Campagne SmartPhish – {campaign_name}\nDate : {campaign_date}")
    title_run.font.size = Pt(14)
    title_run.bold = True
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("")  # espacement

    def add_section_title(text):
        p = doc.add_paragraph()
        run = p.add_run(text.upper())
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x00, 0x47, 0x8F)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # ✨ Partie IA
    for line in lines:
        line = line.strip()
        line = re.sub(r"\*+", "", line)
        if not line:
            doc.add_paragraph("")
            continue
        if re.match(r"^\d+\.", line) or line.lower().startswith(
            ("introduction", "résultats", "analyse", "recommandations", "conclusion")
        ):
            add_section_title(line)
        else:
            doc.add_paragraph(line)

    # 📊 Stats de campagne
    doc.add_paragraph("")
    
    # 🧠 Comportement des utilisateurs
    doc.add_paragraph("")
    add_section_title("DETAILS COMPORTEMENTS UTILISATEURS")


    # Création du tableau
    table = doc.add_table(rows=1, cols=7)
    table.style = "Table Grid"

    # Ligne d’en-tête
    hdr_cells = table.rows[0].cells
    headers = ["Email Address", "Open", "Click", "Data", "Report", "OS", "Browser"]
    for i, text in enumerate(headers):
        hdr_cells[i].text = text
        run = hdr_cells[i].paragraphs[0].runs[0]
        run.bold = True
        run.font.size = Pt(10)
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Lignes des utilisateurs
    for target in goreport.campaign_results_summary:
        row_cells = table.add_row().cells
        email = target["email"]
        opened = "✘"
        clicked = "✘"
        submitted = "✘"
        reported = "✘"
        os_info = "N/A"
        browser_info = "N/A"

        if target["opened"]:
            opened = "✔"
        if target["clicked"]:
            clicked = "✔"
        if target["submitted"]:
            submitted = "✔"
        if target["reported"]:
            reported = "✔"

        # Cherche user-agent si clics
        if target["email"] in goreport.targets_clicked:
            for event in goreport.timeline:
                if event.message == "Clicked Link" and event.email == target["email"]:
                    from user_agents import parse
                    ua = parse(event.details["browser"]["user-agent"])
                    browser_info = f"{ua.browser.family} {ua.browser.version_string}"
                    os_info = f"{ua.os.family} {ua.os.version_string}"

        values = [email, opened, clicked, submitted, reported, os_info, browser_info]
        for i, val in enumerate(values):
            row_cells[i].text = val
            row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER


    # 📥 Génération du fichier
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M")
    filename = f"rapport_campagne_{campaign_id}_{timestamp}.docx"

    return send_file(buffer, as_attachment=True,
                     download_name=filename,
                     mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
