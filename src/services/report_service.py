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
    Découpe un texte généré par IA en sections reconnaissables.
    Nettoie le texte des caractères * typiques du markdown.
    Reconnaît les titres avec ou sans mise en forme Markdown.
    Retourne une liste de tuples (titre, contenu).
    """

    # 🔹 Nettoyage Markdown : suppression des étoiles
    text = re.sub(r'\*+', '', text)

    # 🔹 Titres attendus (analyse détaillée supprimée)
    TITRE_SECTIONS = {
        "analyse des résultats généraux": "Analyse des résultats généraux",
        "recommandations": "Recommandations",
        "conclusion": "Conclusion"
    }

    # 🔹 Pattern regex : détecte les titres seuls sur une ligne
    pattern = re.compile(
        r'^\s*(Analyse des résultats généraux|Recommandations|Conclusion)\s*$',
        re.IGNORECASE | re.MULTILINE
    )

    matches = list(pattern.finditer(text))
    sections = []

    if not matches:
        return [("Analyse complète", text.strip())]

    for i, match in enumerate(matches):
        titre_brut = match.group(1).strip().lower()
        titre_normalisé = TITRE_SECTIONS.get(titre_brut, titre_brut.title())
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        contenu = text[start:end].strip()
        if contenu:
            sections.append((titre_normalisé, contenu))

    # 🔹 Ajout de sections manquantes avec contenu vide
    titres_extraits = [t for t, _ in sections]
    for titre_attendu in TITRE_SECTIONS.values():
        if titre_attendu not in titres_extraits:
            sections.append((titre_attendu, ""))

    return sections


def download_report_styled(campaign_id):
    """
    Cherche le dernier rapport Word généré pour une campagne donnée et le renvoie en téléchargement.
    """
    # Répertoire contenant les rapports générés
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))

    # Récupérer les rapports triés par date (du plus récent au plus ancien)
    candidates = sorted(
        Path(reports_dir).glob(f"rapport_campagne_{campaign_id}_*.docx"),
        key=os.path.getmtime,
        reverse=True
    )

    latest_file = candidates[0] if candidates else None
    if not latest_file:
        return "Rapport introuvable", 404

    # Envoyer le fichier en téléchargement
    return send_file(
        str(latest_file),
        as_attachment=True,
        download_name=latest_file.name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )