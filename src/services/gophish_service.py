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
    """Récupère la liste de tous les groupes GoPhish"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/groups/", headers=HEADERS, verify=False)
    return response.json()  # ou gestion d'erreur

def get_groupsid(group_id):
    """Récupère un groupe GoPhish par son ID"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/groups/{group_id}", headers=HEADERS, verify=False)
    return response.json()  # ou gestion d'erreur


def create_group(data):
    """Crée un nouveau groupe GoPhish"""
    url = f"{Config.GOPHISH_API_URL}/api/groups/"
    response = requests.post(url, json=data, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }

def update_group(group_id, data):
    """
    Met à jour un groupe existant sur Gophish.
    Selon la doc, data doit inclure : { "id": group_id, "name": "...", "targets": [...] }
    """
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

# ---------------------------
#  Fonctions pour les Templates de Mail
# ---------------------------

def get_templates():
    """
    Récupère la liste des templates GoPhish
    via GET /api/templates
    """
    url = f"{Config.GOPHISH_API_URL}/api/templates"
    response = requests.get(url, headers=HEADERS, verify=False)
    try:
        return response.json()  # renvoie un tableau de templates
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }


def create_template(data):
    """
    Crée un nouveau template GoPhish
    via POST /api/templates/
    """
    url = f"{Config.GOPHISH_API_URL}/api/templates/"
    response = requests.post(url, json=data, headers=HEADERS, verify=False)
    try:
        # L'API renvoie le template créé
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }

def get_template(template_id):
    """
    Récupère un template précis via GET /api/templates/<id>
    """
    url = f"{Config.GOPHISH_API_URL}/api/templates/{template_id}"
    response = requests.get(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }

def update_template(template_id, data):
    """
    Modifie un template existant via PUT /api/templates/<id>.
    Vous devez fournir tout le JSON du template (id, name, subject, text/html).
    """
    url = f"{Config.GOPHISH_API_URL}/api/templates/{template_id}"
    response = requests.put(url, json=data, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }

def delete_template(template_id):
    """
    Supprime un template via DELETE /api/templates/<id>
    """
    url = f"{Config.GOPHISH_API_URL}/api/templates/{template_id}"
    response = requests.delete(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }
