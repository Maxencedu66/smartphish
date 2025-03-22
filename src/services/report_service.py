import subprocess
import os
import re
from flask import send_file
from datetime import datetime
from pathlib import Path
from docx import Document
from docx.shared import Pt
from io import BytesIO
import ollama
from src.config import Config
from gophish import Gophish
from src.lib.goreport import Goreport
from src.services.llm_service import generate_ai_analysis

def get_latest_goreport_docx(campaign_id):
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    candidates = sorted(Path(reports_dir).glob(f"rapport_campagne_{campaign_id}_*.docx"), key=os.path.getmtime, reverse=True)
    return candidates[0] if candidates else None

def generate_docx_with_goreport(campaign_id, force=False):
    print(f"🚀 Génération GoReport pour la campagne {campaign_id}")

    # Dossier de stockage des rapports
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    reports_path = Path(reports_dir)
    pattern = f"rapport_campagne_{campaign_id}_*.docx"

    # Si force est True, supprimer les anciens rapports pour cette campagne
    if force:
        for f in reports_path.glob(pattern):
            try:
                os.remove(f)
                print(f"🗑 Suppression de l'ancien rapport : {f}")
            except Exception as e:
                print("Erreur lors de la suppression :", e)

    # Lancement de GoReport pour générer le rapport de base
    result = subprocess.run(
        ["python3", "GoReport.py", "--id", str(campaign_id), "--format", "word"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services")),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ GoReport Error:", result.stderr)
        raise RuntimeError("Erreur GoReport : " + result.stderr)

    print("✅ GoReport exécuté avec succès")

    # Récupérer le dernier fichier généré
    latest_file = None
    for f in sorted(reports_path.glob(pattern), key=os.path.getmtime, reverse=True):
        latest_file = f
        break

    if not latest_file:
        raise FileNotFoundError("Aucun fichier DOCX généré par GoReport")

    print(f"📄 Rapport trouvé : {latest_file}")

    # Génération du texte d'analyse via l'IA
    ai_text = generate_ai_analysis(campaign_id)
    # Ouvrir le document généré pour y ajouter le rapport d'analyse
    document = Document(str(latest_file))
    document.add_page_break()
    document.add_heading("Analyse de la campagne", level=1)
    # Découper le texte généré en sections
    sections = split_ai_text_into_sections(ai_text)
    for title, content in sections:
        document.add_heading(title, level=2)
        p = document.add_paragraph(content)
        p.style.font.size = Pt(11)
    
    # Sauvegarder le document final
    document.save(str(latest_file))
    
    # Retourner le fichier final
    return send_file(
        str(latest_file),
        as_attachment=True,
        download_name=latest_file.name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

def split_ai_text_into_sections(text):
    """
    Découpe le texte généré par l'IA en sections en utilisant un pattern sur les titres (ex : "1. Analyse des résultats généraux:")
    """
    pattern = re.compile(r'(\d+\.\s*[^:]+:)')
    parts = pattern.split(text)
    sections = []
    # Si le premier élément est vide, on commence à l'index 1
    start = 1 if parts and parts[0].strip() == "" else 0
    for i in range(start, len(parts) - 1, 2):
        heading = parts[i].strip()
        content = parts[i+1].strip()
        sections.append((heading, content))
    # Si le découpage ne fonctionne pas (texte non structuré), on renvoie le texte complet sous un seul titre
    if not sections:
        sections.append(("Analyse complète", text))
    return sections

def download_report_styled(campaign_id):
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    candidates = sorted(Path(reports_dir).glob(f"rapport_campagne_{campaign_id}_*.docx"), key=os.path.getmtime, reverse=True)
    latest_file = candidates[0] if candidates else None
    if not latest_file:
        return "Rapport introuvable", 404
    return send_file(
        str(latest_file),
        as_attachment=True,
        download_name=latest_file.name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
