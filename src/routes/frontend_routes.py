# Routes pour afficher les pages HTML, évite de tout mélanger dans le fichier principal app.py

from flask import Blueprint, render_template, Flask, render_template, request, jsonify
from src.services.llm_service import generate_phishing_email 
from src.services.gophish_service import get_campaigns

bp = Blueprint('frontend', __name__, static_folder='../static', template_folder='../templates')


#@bp.route('/dashboard')
#def dashboard():
#    return render_template('dashboard.html')

@bp.route('/generate-email', methods=['POST'])
def generate_email():
    """ Appelle LLM.py pour générer un email de phishing et le retourne en JSON. """
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

    generated_email = generate_phishing_email(user_data)

    return jsonify({"object": generated_email['object'], "content": generated_email['content']})


# Routes pour afficher les pages HTML

@bp.route('/')
def index():
    return render_template('home.html')

@bp.route('/history')
def history():
    return render_template('history.html')

@bp.route('/new-campaign')
def new_campaign():
    return render_template('new-campaign.html')

@bp.route('/follow-campaign')
def follow_campaign():
    campaigns = get_campaigns()  # Récupérer les campagnes GoPhish
    return render_template('follow-campaign.html', campaigns=campaigns)

@bp.route('/analysis-correction')
def analysis_correction():
    return render_template('analysis-correction.html')

@bp.route('/llm-status')
def llm_status():
    return render_template('llm-status.html')

@bp.route('/llm-training')
def llm_training():
    return render_template('llm-training.html')

@bp.route('/llm-settings')
def llm_settings():
    return render_template('llm-settings.html')

@bp.route('/maj-status')
def maj_status():
    return render_template('maj-status.html')