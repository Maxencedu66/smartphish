# Routes pour interagir avec GoPhish

from flask import Blueprint, request, jsonify
from src.services.gophish_service import *

gophish_bp = Blueprint('gophish', __name__)

@gophish_bp.route('/campaigns', methods=['GET'])
def list_campaigns():
    """Retourne la liste des campagnes actives."""
    return jsonify(get_campaigns())

@gophish_bp.route('/campaigns', methods=['POST'])
def new_campaign():
    """Crée une nouvelle campagne de phishing."""
    data = request.json
    return jsonify(create_campaign(data))

#------------------------------
# Routes pour la gestion des groupes
# ------------------------------

@gophish_bp.route('/groups', methods=['GET'])
def list_groups():
    """Retourne la liste des groupes GoPhish en JSON."""
    return jsonify(get_groups())

@gophish_bp.route('/groups/<int:group_id>', methods=['GET'])
def fetch_group(group_id):
    """Retourne UN groupe en JSON."""
    return jsonify(get_groupsid(group_id))

@gophish_bp.route('/groups', methods=['POST'])
def new_gophish_group():
    """Crée un nouveau groupe via Gophish."""
    data = request.json
    return jsonify(create_group(data))

@gophish_bp.route('/groups/<int:group_id>', methods=['PUT'])
def update_gophish_group(group_id):
    """Met à jour un groupe GoPhish."""
    data = request.json
    return jsonify(update_group(group_id, data))

@gophish_bp.route('/groups/<int:group_id>', methods=['DELETE'])
def delete_gophish_group(group_id):
    """Supprime un groupe GoPhish."""
    return jsonify(delete_group(group_id))



#------------------------------
# Routes pour la gestion des sendings profiles
# ------------------------------

# Récupérer tous les Sending Profiles
@gophish_bp.route('/sending_profiles', methods=['GET'])
def list_sending_profiles():
    return jsonify(get_sending_profiles())

# Récupérer un Sending Profile spécifique
@gophish_bp.route('/sending_profiles/<int:profile_id>', methods=['GET'])
def get_sending_profile_route(profile_id):
    return jsonify(get_sending_profile(profile_id))

# Créer un Sending Profile
@gophish_bp.route('/sending_profiles', methods=['POST'])
def new_sending_profile():
    data = request.json
    return jsonify(create_sending_profile(data))

# Mettre à jour un Sending Profile
@gophish_bp.route('/sending_profiles/<int:profile_id>', methods=['PUT'])
def update_sending_profile_route(profile_id):
    data = request.json
    return jsonify(update_sending_profile(profile_id, data))

# Supprimer un Sending Profile
@gophish_bp.route('/sending_profiles/<int:profile_id>', methods=['DELETE'])
def delete_sending_profile_route(profile_id):
    return jsonify(delete_sending_profile(profile_id))