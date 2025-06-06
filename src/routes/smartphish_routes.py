# Routes pour interagir avec GoPhish directement depuis l'API de SmartPhish, permet d'utiliser l'api avec CURL sans affichage du frontend.

from flask import Blueprint, request, jsonify
from src.services.smartphish_service import *

smartphish_bp = Blueprint('smartphish', __name__)

#------------------------------
# Routes pour la gestion des campagnes
# ------------------------------

@smartphish_bp.route('/campaigns', methods=['GET'])
def list_campaigns():
    """Retourne la liste des campagnes actives."""
    return jsonify(get_campaigns())

@smartphish_bp.route('/campaigns', methods=['POST'])
def new_campaign():
    """Crée une nouvelle campagne de phishing."""
    data = request.json
    return jsonify(create_campaign(data))

# Récupérer les détails d'une campagne
@smartphish_bp.route('/campaigns/<int:campaign_id>', methods=['GET'])
def get_campaign_route(campaign_id):
    return jsonify(get_campaign(campaign_id))

# Récupérer les événements d'une campagne
@smartphish_bp.route('/campaigns/<int:campaign_id>/timeline', methods=['GET'])
def get_campaign_events_route(campaign_id):
    return jsonify(get_campaign_events(campaign_id))

# Récupérer les résultats d'une campagne
@smartphish_bp.route('/campaigns/<int:campaign_id>/results', methods=['GET'])
def get_campaign_results_route(campaign_id):
    return jsonify(get_campaign_results(campaign_id))

# Récupérer le résumé d'une campagne
@smartphish_bp.route('/campaigns/<int:campaign_id>/summary', methods=['GET'])
def get_campaign_summary_route(campaign_id):
    return jsonify(get_campaign_summary(campaign_id))


# Supprimer une campagne
@smartphish_bp.route('/campaigns/<int:campaign_id>', methods=['DELETE'])
def delete_campaign_route(campaign_id):
    return jsonify(delete_campaign(campaign_id))

# Marquer une campagne comme terminée
@smartphish_bp.route('/campaigns/<int:campaign_id>/complete', methods=['GET'])
def complete_campaign_route(campaign_id):
    return jsonify(complete_campaign(campaign_id))






#------------------------------
# Routes pour la gestion des groupes
# ------------------------------

@smartphish_bp.route('/groups', methods=['GET'])
def list_groups():
    """Retourne la liste des groupes GoPhish en JSON."""
    return jsonify(get_groups())

@smartphish_bp.route('/groups/<int:group_id>', methods=['GET'])
def fetch_group(group_id):
    """Retourne UN groupe en JSON."""
    return jsonify(get_groupsid(group_id))

@smartphish_bp.route('/groups', methods=['POST'])
def new_gophish_group():
    """Crée un nouveau groupe via Gophish."""
    data = request.json
    return jsonify(create_group(data))

@smartphish_bp.route('/groups/<int:group_id>', methods=['PUT'])
def update_gophish_group(group_id):
    """Met à jour un groupe GoPhish."""
    data = request.json
    return jsonify(update_group(group_id, data))

@smartphish_bp.route('/groups/<int:group_id>', methods=['DELETE'])
def delete_gophish_group(group_id):
    """Supprime un groupe GoPhish."""
    return jsonify(delete_group(group_id))






#------------------------------
# Routes pour la gestion des sendings profiles
# ------------------------------

# Récupérer tous les Sending Profiles
@smartphish_bp.route('/sending_profiles', methods=['GET'])
def list_sending_profiles():
    return jsonify(get_sending_profiles())

# Récupérer un Sending Profile spécifique
@smartphish_bp.route('/sending_profiles/<int:profile_id>', methods=['GET'])
def get_sending_profile_route(profile_id):
    return jsonify(get_sending_profile(profile_id))

# Créer un Sending Profile
@smartphish_bp.route('/sending_profiles', methods=['POST'])
def new_sending_profile():
    data = request.json
    return jsonify(create_sending_profile(data))

# Mettre à jour un Sending Profile
@smartphish_bp.route('/sending_profiles/<int:profile_id>', methods=['PUT'])
def update_sending_profile_route(profile_id):
    data = request.json
    return jsonify(update_sending_profile(profile_id, data))

# Supprimer un Sending Profile
@smartphish_bp.route('/sending_profiles/<int:profile_id>', methods=['DELETE'])
def delete_sending_profile_route(profile_id):
    return jsonify(delete_sending_profile(profile_id))







#------------------------------
# Routes pour la gestion des landing pages
# ------------------------------

@smartphish_bp.route('/landing_pages', methods=['GET'])
def list_landing_pages():
    """Retourne la liste des Landing Pages."""
    return jsonify(get_landing_pages())

@smartphish_bp.route('/landing_pages/<int:landing_page_id>', methods=['GET'])
def fetch_landing_page(landing_page_id):
    """Retourne une Landing Page spécifique."""
    return jsonify(get_landing_page(landing_page_id))

@smartphish_bp.route('/landing_pages', methods=['POST'])
def new_landing_page():
    """Crée une nouvelle Landing Page."""
    data = request.json
    return jsonify(create_landing_page(data))

@smartphish_bp.route('/landing_pages/<int:landing_page_id>', methods=['PUT'])
def update_landing_page_route(landing_page_id):
    """Met à jour une Landing Page existante."""
    data = request.json
    return jsonify(update_landing_page(landing_page_id, data))

@smartphish_bp.route('/landing_pages/<int:landing_page_id>', methods=['DELETE'])
def delete_landing_page_route(landing_page_id):
    """Supprime une Landing Page."""
    return jsonify(delete_landing_page(landing_page_id))

@smartphish_bp.route('/import_site', methods=['POST'])
def import_site_route():
    """
    Importe un site en récupérant le HTML via l'endpoint d'import de GoPhish.
    Le body doit contenir les champs 'url', 'include_resources', etc.
    """
    data = request.json
    response = import_site(data)  
    return jsonify(response)
