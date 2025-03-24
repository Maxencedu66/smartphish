import ollama
from ollama import ListResponse, ProcessResponse
from pydantic import BaseModel
from src.routes.auth_routes import get_db_connection
from datetime import datetime
from src.lib.goreport import Goreport
from gophish import Gophish
from src.config import Config


class EmailInfo(BaseModel):
  objet_mail: str
  contenu_mail: str

def generate_prompt(user_data):
    """Génère un prompt adapté au scénario sélectionné."""
    scenario = user_data["scénario"]

    prompts = {
        "Départ à la retraite": f"""
        Rédige un email informel annonçant le départ à la retraite d'un collègue. Ne specifie pas son nom.
        Le mail doit être **court, direct et sans fioritures**. 
        Il doit inciter les destinataires à **répondre rapidement** en fournissant leurs coordonnées (RIB et numéro de téléphone).
        Ne **PAS** mettre de champs à remplir (ex: nom du destinataire [Destinataire]), le mail doit être **prêt à être envoyé** sans **AUCUN** changement.
        
        - **But** : Organiser un repas de départ et demander subtilement un RIB et des coordonnées.
        - **Ton** : Amical et détendu.
        - **Signature** : {user_data['expéditeur']}.
        - **Langue** : Français.

        Exemple : 
        ---
        Salut à tous, 
        On organise un dîner pour le départ à la retraite d'un collègue. J'aurai besoin de savoir qui est dispo et de récupérer un acompte pour réserver. 
        Merci d'envoyer votre RIB et numéro de téléphone pour qu'on puisse s'organiser. 
        À bientôt !
        ---
        """,

        "Erreur de paiement - RIB nécessaire": f"""
        Rédige un email **sérieux et court**, annonçant une erreur de versement de salaire. 
        Il doit **rassurer** le destinataire et l'inciter à envoyer son **RIB** rapidement.
        Ne donnes pas le numéro de téléphone de l'expéditeur, seulement son email.
        Ne **PAS** mettre de champs à remplir (ex: nom du destinataire [Destinataire]), le mail doit être **prêt à être envoyé** sans **AUCUN** changement.

        - **But** : Obtenir un RIB sous prétexte d'une correction de paiement.
        - **Ton** : Professionnel et bienveillant.
        - **Signature** : {user_data['expéditeur']}.
        - **Langue** : Français.

        Exemple : 
        ---
        Bonjour, 
        Une erreur a été détectée dans votre paiement ce mois-ci. Afin de procéder rapidement au virement, merci de renvoyer votre RIB à cette adresse : {user_data['email_expediteur']}. 
        Désolé pour ce désagrément, nous faisons le nécessaire au plus vite.
        ---
        """,

        "Invitation à un événement exclusif": f"""
        Rédige un email **dynamique et engageant** tout en restant formel pour des employés, invitant à un événement professionnel restreint. 
        L'email doit **être convaincant** et inciter l'employé à répondre au mail avec ses **coordonnées personnelles**.
        Ne **PAS** mettre de champs à remplir (ex: nom du destinataire [Destinataire]), le mail doit être **prêt à être envoyé** sans **AUCUN** changement.

        - **But** : Récupérer des informations personnelles (nom, téléphone, RIB) sous couvert d'une invitation à un événement exclusif.
        - **Ton** : Enthousiaste et exclusif mais professionel et formel.
        - **Signature** : {user_data['expéditeur']}.
        - **Destinataire** : Inconnu.
        - **Entreprise** : '{user_data['entreprise']}'.
        - **Langue** : Français.

        Exemple : 
        ---
        🎉 L'entreprise '{user_data['entreprise']}' organise un événement exclusif pour ses collaborateurs ! 
        Nombre de places limité, **inscrivez-vous vite** en répondant à ce mail avec vos noms, numéro de téléphone et RIB. 
        Ne manquez pas cette opportunité unique !
        ---
        
        Rappel : **Ne pas mettre de champs à remplir**. NE PAS METTRE DE choses avec des crochets [Nom], [Téléphone], etc sinon je me tire une balle et je suis sérieux OK ?
        Si tu ne sais pas une information, n'en parle pas.
        """,

        "Mise à jour de sécurité urgente": f"""
        Rédige un **email officiel** annonçant une **mise à jour de sécurité obligatoire**. 
        Il doit inciter le destinataire à **répondre au mail** avec **ses identifiants** pour "mettre à jour" ses accès.
        Ne **PAS** mettre de champs à remplir (ex: nom du destinataire [Destinataire]), le mail doit être **prêt à être envoyé** sans **AUCUN** changement.

        - **But** : Faire croire à une mise à jour système pour obtenir des identifiants.
        - **Ton** : Sérieux et impersonnel.
        - **Signature** : {user_data['expéditeur']}.
        - **Langue** : Français.

        Exemple : 
        ---
        Bonjour cher collaborateur, 
        Dans le cadre de l'amélioration de la sécurité informatique de {user_data['entreprise']}, une **mise à jour de vos accès** est nécessaire.  
        **Merci de répondre à ce mail avec vos identifiants** pour procéder à la mise à jour.
        ---
        """,
    }

    return prompts.get(scenario, "Scénario non trouvé.")

def generate_phishing_email(user_data):
    """Génère un email de phishing à l'aide de Mistral via Ollama."""
    prompt = generate_prompt(user_data)
    # print(prompt)

    valid = False
    while not valid:
        response: EmailInfo = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}], format=EmailInfo.model_json_schema())
        response_obj = EmailInfo.model_validate_json(response.message.content)
        
        # Strip the email content
        lines = response_obj.contenu_mail.split("\n")
        response_obj.contenu_mail = "\n".join([line.strip() for line in lines])
        valid = '[dest' not in response_obj.contenu_mail.lower() and len(lines) > 1 and 'Dear ' not in response_obj.contenu_mail
        
        if not valid:
            print("Email not valid, retrying...")
            # print(response_obj.contenu_mail)
    
    return {"object": response_obj.objet_mail, "content": response_obj.contenu_mail}

def get_ollama_status():
    """Récupère les informations sur les modèles téléchargés et/ou en mémoire via Ollama."""
    
    # Modèles en mémoire
    response_memory: ProcessResponse = ollama.ps()
    
    # Modèles téléchargés
    response: ListResponse = ollama.list()
    
    info_dicts = list()
    for model in response.models:
        info_dicts.append({
            'name': model.model,
            'size_mb': f'{(model.size.real / 1024 / 1024):.2f}',
            'family': model.details.family if model.details else None,
            'parameter_size': model.details.parameter_size if model.details else None,
            'modified_at': model.modified_at.strftime('%Y-%m-%d %H:%M:%S') if model.modified_at else None,
            'expires_at': None,
            'size_vram': None
        })
        
    for model in response_memory.models:
        for i in range(len(info_dicts)):
            if model.model == info_dicts[i]['name']:
                info_dicts[i]['expires_at'] = model.expires_at.strftime('%Y-%m-%d %H:%M:%S')
                info_dicts[i]['size_vram'] = model.size_vram
                break
    
    return info_dicts


def generate_ai_analysis(campaign_id):
    """
    Génère les 4 sections d'analyse (générale, détaillée, recommandations, conclusion) en se basant sur les stats de la campagne.
    Cette fonction s'inspire de la logique de generate_and_save_report_to_db sans sauvegarder en BDD.
    """
    # Instancier et configurer GoReport pour récupérer les infos de la campagne
    goreport = Goreport(report_format="word", config_file=None, google=False, verbose=False)
    goreport.api = Gophish(Config.GOPHISH_API_KEY, host=Config.GOPHISH_API_URL, verify=False)
    # Récupération des données de campagne
    campaign_data = goreport.api.campaigns.get(campaign_id=campaign_id)
    goreport.campaign = campaign_data
    goreport.collect_all_campaign_info(combine_reports=False)
    goreport.process_timeline_events(combine_reports=False)
    goreport.process_results(combine_reports=False)

    # Extraction des statistiques
    opened = goreport.total_unique_opened
    clicked = goreport.total_unique_clicked
    submitted = goreport.total_unique_submitted
    reported = goreport.total_unique_reported
    total = goreport.total_targets
    cam_name = goreport.cam_name
    cam_date = goreport.launch_date.split("T")[0] if goreport.launch_date else "inconnue"


    # Construction du prompt pour l'IA
    prompt = f"""Tu es un expert en cybersécurité. Rédige les 4 sections suivantes en te basant sur les résultats réels de la campagne de phishing suivante :

- Nom de la campagne : {cam_name}
- Date : {cam_date}

- Nombre de destinataires : {total}
- Emails ouverts : {opened}
- Clics sur les liens : {clicked}
- Données soumises : {submitted}
- Emails signalés : {reported}

1. Analyse des résultats généraux : Donne un résumé clair de l'efficacité de la campagne et des statistiques observées.
2. Analyse détaillée : Donne une analyse plus poussée des comportements à risque, navigateurs/OS, géolocalisations, etc.
3. Recommandations : 3 conseils précis pour mieux se protéger.
4. Conclusion : Message final de sensibilisation.

⚠️ Règles :
- Pas de format Markdown, HTML ou balises.
- Texte professionnel, clair et en français uniquement.
- Bien structuré avec des titres reconnaissables.

Rends le texte fluide, facile à lire, et professionnel.
"""
    # Appel à l'IA via Ollama (ici modèle "mistral")
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    texte = response.message.content.strip()
    return texte


