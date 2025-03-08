# Routes pour afficher les pages HTML, évite de tout mélanger dans le fichier principal app.py

from flask import Blueprint, render_template, Flask, render_template, request, jsonify, redirect, url_for
from src.services.llm_service import generate_phishing_email 
from src.services.gophish_service import get_campaigns, get_groups, create_group, delete_group, update_group, get_groupsid
import json

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

@bp.route('/configuration')
def configuration():
    return render_template('configuration.html')

#@bp.route('/config-groups')
#def config_groups():
#    return render_template('config-groups.html')

@bp.route('/config-emails')
def config_emails():
    return render_template('config-emails.html')

@bp.route('/config-landing-pages')
def config_landing_pages():
    return render_template('config-landing-pages.html')

@bp.route('/new-campaign')
def new_campaign():
    return render_template('new-campaign.html')

@bp.route('/follow-campaign')
def follow_campaign():
    campaigns = get_campaigns()  # Récupérer les campagnes GoPhish
    
    return render_template('follow-campaign.html', campaigns=campaigns)

@bp.route("/details_campaign/<int:campaign_id>")
def details_campaign(campaign_id):
    campaigns = get_campaigns()

    # Recherche de la campagne avec l'ID reçu
    selected_campaign = next((c for c in campaigns if c["id"] == campaign_id), None)

    if not selected_campaign:
        return "Campagne non trouvée", 404
    
    return render_template("details-campaign.html", campaign=selected_campaign)

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

@bp.route('/config-groups')
def config_groups():
    groups_data = get_groups()  # Renvoie un tableau de groupes
    return render_template('config-groups.html', groups=groups_data)

@bp.route('/config-groups/<int:group_id>', methods=['GET'])
def get_group_frontend(group_id):
    """
    Retourne UN groupe en JSON (pour remplir la modale "Edit Group").
    """
    group_data = get_groupsid(group_id)
    return jsonify(group_data)

@bp.route('/config-groups', methods=['POST'])
def newgroup_submit():
    """
    Crée un nouveau groupe depuis une requête JSON (Fetch API).
    Retourne une réponse JSON.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    name = data.get('name')
    targets = data.get('targets', [])

    if not name:
        return jsonify({"error": "Le champ 'name' est requis"}), 400
    
    # Appel GoPhish
    response = create_group({"name": name, "targets": targets})

    if 'error' in response:
        return jsonify(response), 400

    return jsonify(response), 200

@bp.route('/config-groups/<int:group_id>', methods=['PUT'])
def update_group_frontend(group_id):
    """
    Reçoit la requête PUT du front-end, et met à jour ce groupe via GoPhish.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    # GoPhish exige "id": group_id dans le JSON complet.
    if "id" not in data:
        data["id"] = group_id

    response = update_group(group_id, data)

    if "error" in response:
        return jsonify(response), 400

    return jsonify(response), 200

@bp.route('/config-groups/<int:group_id>', methods=['DELETE'])
def delete_group_frontend(group_id):
    """
    Supprime un groupe (DELETE) via GoPhish.
    """
    response = delete_group(group_id)
    return jsonify(response)

