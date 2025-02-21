# Gestion de GoPhish via l'API

import requests
from src.config import Config

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Config.GOPHISH_API_KEY}"
}

def get_campaigns():
    """Récupère la liste des campagnes GoPhish"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/campaigns", headers=HEADERS)
    return response.json()

def create_campaign(data):
    """Crée une nouvelle campagne de phishing"""
    response = requests.post(f"{Config.GOPHISH_API_URL}/campaigns", json=data, headers=HEADERS)
    return response.json()
