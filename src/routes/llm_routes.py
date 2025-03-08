# Routes pour la gestion du LLM (Génération des emails)
from flask import Blueprint, request, jsonify
from src.services.llm_service import generate_phishing_email, get_ollama_status

llm_bp = Blueprint('llm', __name__)

@llm_bp.route('/generate-email', methods=['POST'])
def generate_email():
    """Appelle le service LLM pour générer un email de phishing et retourne le résultat en JSON."""
    data = request.json
    scenario = data.get("scenario")
    entreprise = data.get("entreprise", "")
    expediteur = data.get("expediteur", "")
    email_expediteur = data.get("email_expediteur", "")

    user_data = {
        "scénario": scenario,
        "entreprise": entreprise,
        "expéditeur": expediteur,
        "email_expediteur": email_expediteur
    }

    try:
        generated_email = generate_phishing_email(user_data)
        return jsonify({"object": generated_email['object'], "content": generated_email['content']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@llm_bp.route('/status', methods=['GET'])
def get_status():
    """Retourne les informations sur les modèles téléchargés et/ou en mémoire via Ollama."""
    return jsonify(get_ollama_status())