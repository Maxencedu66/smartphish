# Routes pour interagir avec GoPhish

from flask import Blueprint, request, jsonify
from src.services.gophish_service import get_campaigns, create_campaign, get_groups, create_group, delete_group, update_group

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
    """Retourne la liste des groupes GoPhish."""
    return jsonify(get_groups())

@gophish_bp.route('/groups/<int:group_id>', methods=['GET'])
def fetch_group(group_id):
    """Renvoie le détail d'un groupe en JSON."""
    return jsonify(get_group(group_id))
    

@gophish_bp.route('/groups', methods=['POST'])
def new_gophish_group():
    """Crée un nouveau groupe via Gophish."""
    data = request.json
    return jsonify(create_group(data))

@gophish_bp.route('/groups/<int:group_id>', methods=['DELETE'])
def delete_gophish_group(group_id):
    """Supprime un groupe GoPhish."""
    return jsonify(delete_group(group_id))

@gophish_bp.route('/groups/<int:group_id>', methods=['PUT'])
def update_gophish_group(group_id):
    """Met à jour un groupe GoPhish."""
    data = request.json
    return jsonify(update_group(group_id, data))
    