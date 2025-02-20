# Routes pour afficher les pages HTML, évite de tout mélanger dans le fichier principal app.py

from flask import Blueprint, render_template, Flask, render_template, request, jsonify
from src.services.llm_service import generate_phishing_email 

bp = Blueprint('frontend', __name__, static_folder='../static', template_folder='../templates')

@bp.route('/')
def index():
    return render_template('home.html')


#@bp.route('/dashboard')
#def dashboard():
#    return render_template('dashboard.html')

@bp.route('/nouvelle_campagne')
def nouvelle_campagne():
    return render_template('new_campaign.html')

@bp.route('/generate_email', methods=['POST'])
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

@bp.route('/history')
def history():
    return render_template('historic.html')

@bp.route('/suivi')
def suivi():
    return render_template('follow_campaign.html')

@bp.route('/analyse')
def analyse():
    return render_template('analyse_correction.html')

@bp.route('/llm_statut')
def llm_statut():
    return render_template('status_llm.html')

@bp.route('/maj')
def maj():
    return render_template('status_maj.html')