import ollama
from ollama import ListResponse, ProcessResponse
from pydantic import BaseModel

# Define the schema for the response
class EmailInfo(BaseModel):
  objet_mail: str
  contenu_mail: str

def generate_prompt(user_data):
    """Génère un prompt adapté au scénario sélectionné."""
    scenario = user_data["scénario"]

    prompts = {
        "Départ à la retraite": f"""
        Rédige un email informel annonçant le départ à la retraite d'un collègue. 
        Le mail doit être **court, direct et sans fioritures**. 
        Il doit inciter les destinataires à **répondre rapidement** en fournissant leurs coordonnées (RIB et numéro de téléphone).
        Ne pas laisser des informations à compléter.
        
        - **But** : Organiser un repas de départ et demander subtilement un RIB et des coordonnées.
        - **Ton** : Amical et détendu.
        - **Signature** : {user_data['expéditeur']}.

        Exemple : 
        ---
        Salut à tous, 
        On organise un dîner pour le départ à la retraite d’un collègue. J’aurai besoin de savoir qui est dispo et de récupérer un acompte pour réserver. 
        Merci d’envoyer votre RIB ou de faire un virement directement. 
        À bientôt !
        ---
        """,

        "Erreur de paiement - RIB nécessaire": f"""
        Rédige un email **sérieux et court**, annonçant une erreur de versement de salaire. 
        Il doit **rassurer** le destinataire et l’inciter à envoyer son **RIB** rapidement.

        - **But** : Obtenir un RIB sous prétexte d'une correction de paiement.
        - **Ton** : Professionnel et bienveillant.
        - **Signature** : {user_data['expéditeur']}.

        Exemple : 
        ---
        Bonjour, 
        Une erreur a été détectée dans votre paiement ce mois-ci. Afin de procéder rapidement au virement, merci de renvoyer votre RIB à cette adresse : {user_data['email_expediteur']}. 
        Désolé pour ce désagrément, nous faisons le nécessaire au plus vite.
        ---
        """,

        "Alerte de sécurité - Connexion suspecte": f"""
        Rédige un **email d’alerte de sécurité**, court et urgent, indiquant une **tentative de connexion suspecte**. 
        L’email doit **pousser** le destinataire à **cliquer immédiatement sur un faux lien** pour réinitialiser son mot de passe.

        - **But** : Piéger la cible en lui faisant croire à un accès non autorisé.
        - **Ton** : Urgent, formel.
        - **Signature** : {user_data['expéditeur']}.

        Exemple : 
        ---
        ⚠️ Alerte de sécurité ! 
        Une connexion inhabituelle a été détectée sur plusieurs comptes {user_data['entreprise']}. 
        Si vous ne reconnaissez pas cette activité, **réinitialisez immédiatement votre mot de passe** via ce lien sécurisé : [LIEN FAUX].  
        ---
        """,

        "Invitation à un événement exclusif": f"""
        Rédige un email **dynamique et engageant**, invitant à un événement professionnel restreint. 
        L'email doit **être convaincant** et inciter la cible à **remplir un formulaire** avec ses coordonnées personnelles.

        - **But** : Récupérer des informations personnelles via un faux formulaire.
        - **Ton** : Enthousiaste et exclusif.
        - **Signature** : {user_data['expéditeur']}.

        Exemple : 
        ---
        🎉 {user_data['entreprise']} organise un événement exclusif pour ses collaborateurs ! 
        Nombre de places limité, **inscrivez-vous vite** en remplissant ce formulaire : [LIEN FAUX]. 
        Ne manquez pas cette opportunité unique !
        ---
        """,

        "Mise à jour de sécurité urgente": f"""
        Rédige un **email officiel** annonçant une **mise à jour de sécurité obligatoire**. 
        Il doit inciter le destinataire à **se connecter sur un faux site** pour "mettre à jour" ses accès.

        - **But** : Faire croire à une mise à jour système pour obtenir des identifiants.
        - **Ton** : Sérieux et impersonnel.
        - **Signature** : {user_data['expéditeur']}.

        Exemple : 
        ---
        Bonjour, 
        Dans le cadre de l’amélioration de la sécurité informatique de {user_data['entreprise']}, une **mise à jour de vos accès** est nécessaire.  
        **Connectez-vous immédiatement** via ce lien sécurisé : [LIEN FAUX]. 
        ---
        """,

        "Réinitialisation de mot de passe": f"""
        Rédige un **email urgent**, indiquant un **problème avec le mot de passe** du destinataire. 
        Il doit être **sobre, direct et efficace** pour inciter la personne à **entrer ses identifiants sur un faux site**.

        - **But** : Amener la cible à se connecter sur un faux site de réinitialisation.
        - **Ton** : Sobre et direct.
        - **Signature** : {user_data['expéditeur']}.

        Exemple : 
        ---
        Bonjour,  
        Votre mot de passe expire aujourd’hui. Pour éviter toute interruption de service, **réinitialisez-le dès maintenant** via ce lien sécurisé : [LIEN FAUX].  
        ---
        """
    }

    return prompts.get(scenario, "Scénario non trouvé.")

def generate_phishing_email(user_data):
    """Génère un email de phishing à l'aide de Mistral via Ollama."""
    prompt = generate_prompt(user_data)

    response: EmailInfo = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}], format=EmailInfo.model_json_schema())
    response_obj = EmailInfo.model_validate_json(response.message.content)
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