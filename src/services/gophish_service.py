# Gestion de GoPhish via l'API

import requests
from src.config import Config


HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Config.GOPHISH_API_KEY}"
}

def get_campaigns():
    """Récupère la liste des campagnes GoPhish en HTTPS"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/campaigns", headers=HEADERS, verify=False)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse de GoPhish invalide", "status_code": response.status_code, "content": response.text}

def create_campaign(data):
    """Crée une nouvelle campagne de phishing"""
    print("🔹 Envoi des données à GoPhish :", data)  # DEBUG
    response = requests.post(f"{Config.GOPHISH_API_URL}/api/campaigns", json=data, headers=HEADERS, verify=False)

    print("🔹 Réponse GoPhish :", response.status_code, response.text)  # DEBUG

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}

# ---------------------------
#  Fonctions pour les Groupes
# ---------------------------

def get_groups():
    """Récupère la liste des groupes GoPhish"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/groups/", headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }

def create_group(data):
    print("🔹 create_group() data:", data)
    url = f"{Config.GOPHISH_API_URL}/api/groups/"
    print("🔹 URL:", url)

    response = requests.post(url, json=data, headers=HEADERS, verify=False)

    print("🔹 Status code:", response.status_code)
    print("🔹 Response text:", response.text)

    try:
        return response.json()  # On renvoie le JSON décodé
    except requests.exceptions.JSONDecodeError:
        # En cas de JSON invalide, on renvoie un dict d'erreur
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }


def update_group(group_id, data):
    """Met à jour un groupe existant sur Gophish"""
    url = f"{Config.GOPHISH_API_URL}/api/groups/{group_id}"
    response = requests.put(url, json=data, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }

def delete_group(group_id):
    """Supprime un groupe existant sur Gophish"""
    url = f"{Config.GOPHISH_API_URL}/api/groups/{group_id}"
    response = requests.delete(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }