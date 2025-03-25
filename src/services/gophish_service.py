# Gestion de GoPhish via l'API de Smartphish

import requests
import bcrypt
from src.config import Config


HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Config.GOPHISH_API_KEY}"
}

# ---------------------------
#  Fonctions pour la gestion des Campagnes
# ---------------------------

def get_campaigns():
    """Récupère la liste des campagnes en HTTPS"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/campaigns", headers=HEADERS, verify=False)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse de GoPhish invalide", "status_code": response.status_code, "content": response.text}


def create_campaign(data):
    """Crée une campagne """
    url = f"{Config.GOPHISH_API_URL}/api/campaigns/"

    # Correction du format de la date si besoin :
    launch_date = data.get("launch_date")
    # Si la date est au format "YYYY-MM-DDTHH:MM" (16 caractères), on ajoute ":00+00:00"
    if launch_date and len(launch_date) == 16:
        launch_date = launch_date + ":00+00:00"

    # Si le smtp est vide, on le met à None
    smtp_name = data.get("smtp", {}).get("name")
    if smtp_name == "":
        smtp_obj = None
    else:
        smtp_obj = {"name": smtp_name}

    campaign_data = {
        "name": data.get("name", "Default Campaign"),
        "template": {"name": data["template"]["name"]} if "template" in data else None,
        "page": {"name": data["page"]["name"]} if "page" in data else None,
        "smtp": smtp_obj,
        "groups": [{"name": group["name"]} for group in data.get("groups", [])],
        "url": data.get("url", "http://localhost"),
        "launch_date": launch_date,
        "send_by_date": data.get("send_by_date", None)
    }

    #print(" Données envoyées à GoPhish :", campaign_data)
    response = requests.post(url, json=campaign_data, headers=HEADERS, verify=False)
    #print(" Réponse brute de GoPhish :", response.status_code, response.text)

    try:
        result = response.json()
        if response.status_code == 201:
            return {"success": True, "message": "Campaign created successfully", "campaign": result}
        else:
            return {"error": "Failed to create campaign", "status_code": response.status_code, "response": result}
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Invalid response from GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }


def get_campaign(campaign_id):
    """Récupère les détails d'une campagne spécifique."""
    url = f"{Config.GOPHISH_API_URL}/api/campaigns/{campaign_id}"
    response = requests.get(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide", "status_code": response.status_code, "content": response.text}


def get_campaign_events(campaign_id):
    """Récupère les événements d'une campagne."""
    url = f"{Config.GOPHISH_API_URL}/api/campaigns/{campaign_id}/timeline"
    response = requests.get(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide", "status_code": response.status_code, "content": response.text}


def get_campaign_results(campaign_id):
    """Récupère les résultats d'une campagne."""
    url = f"{Config.GOPHISH_API_URL}/api/campaigns/{campaign_id}/results"
    response = requests.get(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide", "status_code": response.status_code, "content": response.text}


def get_campaign_summary(campaign_id):
    """Récupère le résumé d'une campagne."""
    url = f"{Config.GOPHISH_API_URL}/api/campaigns/{campaign_id}/summary"
    response = requests.get(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide", "status_code": response.status_code, "content": response.text}


def delete_campaign(campaign_id):
    """Supprime une campagne."""
    url = f"{Config.GOPHISH_API_URL}/api/campaigns/{campaign_id}"
    response = requests.delete(url, headers=HEADERS, verify=False)
    try:
        if response.status_code in [200, 204]:
            return {"success": True, "message": "Campagne supprimée"}
        else:
            return {"error": "Échec de la suppression", "status_code": response.status_code, "response": response.json()}
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide", "status_code": response.status_code, "content": response.text}


def complete_campaign(campaign_id):
    """Marque une campagne comme terminée."""
    url = f"{Config.GOPHISH_API_URL}/api/campaigns/{campaign_id}/complete"
    response = requests.get(url, headers=HEADERS, verify=False)
    
    if response.status_code == 200:
        try:
            data = response.json() if response.text.strip() != "" else None
            return {"success": True, "message": "Campaign completed successfully!", "data": data}
        except requests.exceptions.JSONDecodeError:
            return {"success": True, "message": "Campaign completed successfully!", "data": None}
    else:
        try:
            return {"error": "Failed to complete campaign", "status_code": response.status_code, "response": response.json()}
        except requests.exceptions.JSONDecodeError:
            return {"error": "Failed to complete campaign", "status_code": response.status_code, "content": response.text}




# ---------------------------
#  Fonctions pour les Groupes
# ---------------------------

def get_groups():
    """Récupère la liste de tous les groupes GoPhish"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/groups/", headers=HEADERS, verify=False)
    return response.json() 

def get_groupsid(group_id):
    """Récupère un groupe GoPhish par son ID"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/groups/{group_id}", headers=HEADERS, verify=False)
    return response.json() 


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
    """Supprime un groupe existant """
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
    Récupère la liste des templates
    """
    url = f"{Config.GOPHISH_API_URL}/api/templates"
    response = requests.get(url, headers=HEADERS, verify=False)
    try:
        return response.json()  
    except requests.exceptions.JSONDecodeError:
        return {
            "error": "Réponse invalide de GoPhish",
            "status_code": response.status_code,
            "content": response.text
        }


def create_template(data):
    """
    Crée un nouveau template GoPhish
    """
    url = f"{Config.GOPHISH_API_URL}/api/templates/"
    response = requests.post(url, json=data, headers=HEADERS, verify=False)
    try:
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
    Modifie un template existant.
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
    Supprime un template à partir de son ID.
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

        
        
# ---------------------------
#  Fonctions pour les Sending Profiles (Profils SMTP)
# ---------------------------

def get_sending_profiles():
    """Récupère la liste de tous les sending profiles (profils SMTP)"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/smtp/", headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}

def get_sending_profile(profile_id):
    """Récupère un sending profile spécifique par son ID"""
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/smtp/{profile_id}", headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}

def create_sending_profile(data):
    """Crée un nouveau sending profile"""
    response = requests.post(f"{Config.GOPHISH_API_URL}/api/smtp/", json=data, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}

def update_sending_profile(profile_id, data):
    """Met à jour un sending profile existant"""
    url = f"{Config.GOPHISH_API_URL}/api/smtp/{profile_id}"
    response = requests.put(url, json=data, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}

def delete_sending_profile(profile_id):
    """Supprime un sending profile existant"""
    url = f"{Config.GOPHISH_API_URL}/api/smtp/{profile_id}"
    response = requests.delete(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}


# ---------------------------
#  Fonctions pour les Landing Pages
# ---------------------------

def get_landing_pages():
    """Récupère la liste des Landing Pages de GoPhish"""
    url = f"{Config.GOPHISH_API_URL}/api/pages/"
    response = requests.get(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}

def get_landing_page(landing_page_id):
    """Récupère une Landing Page spécifique"""
    url = f"{Config.GOPHISH_API_URL}/api/pages/{landing_page_id}"
    response = requests.get(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}

def create_landing_page(data):
    """Crée une nouvelle Landing Page"""
    url = f"{Config.GOPHISH_API_URL}/api/pages/"
    response = requests.post(url, json=data, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}

def update_landing_page(landing_page_id, data):
    """Met à jour une Landing Page"""
    url = f"{Config.GOPHISH_API_URL}/api/pages/{landing_page_id}"
    response = requests.put(url, json=data, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}

def delete_landing_page(landing_page_id):
    """Supprime une Landing Page"""
    url = f"{Config.GOPHISH_API_URL}/api/pages/{landing_page_id}"
    response = requests.delete(url, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}
    
def import_site(data):
    """Importe un site et retourne son HTML via l'API GoPhish"""
    url = f"{Config.GOPHISH_API_URL}/api/import/site"
    response = requests.post(url, json=data, headers=HEADERS, verify=False)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Réponse invalide de GoPhish", "status_code": response.status_code, "content": response.text}
