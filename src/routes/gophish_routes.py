# Routes pour interagir avec GoPhish

from flask import Blueprint, request, jsonify
from src.services.gophish_service import get_campaigns, create_campaign

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
