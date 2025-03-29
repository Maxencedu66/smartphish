import ollama
from ollama import ListResponse, ProcessResponse
from pydantic import BaseModel
from datetime import datetime
import threading
from src.routes.auth_routes import get_db_connection
from src.lib.goreport_lib import Goreport
from src.config import Config
import re


class EmailInfo(BaseModel):
  objet_mail: str
  contenu_mail: str

def generate_prompt(user_data):
    """Génère un prompt adapté au scénario sélectionné."""
    scenario = user_data["scénario"]
    expediteur = user_data.get("expéditeur", "Expéditeur inconnu")
    entreprise = user_data.get("entreprise", "Entreprise inconnue")

    prompts = {
        "Départ à la retraite": f"""
        Rédige un email informel annonçant le départ à la retraite d'un collègue. Ne specifie pas son nom.
        Le mail doit être **court, direct et sans fioritures**. 
        Il doit inciter les destinataires à **répondre rapidement** en fournissant leurs coordonnées (RIB et numéro de téléphone).
        
        - **But** : Organiser un repas de départ et demander subtilement un RIB et des coordonnées.
        - **Ton** : Amical et détendu.
        - **Signature** : {expediteur}.
        - **Langue** : Français.
        - **Destinataire** : {'{{.FirstName}}'} {'{{.LastName}}'}
        - **Faux lien** : {'[texte]({{.URL}})'}

        Exemple : 
        ---
        Salut {'{{.FirstName}}'}, 
        On organise un dîner pour le départ à la retraite d'un collègue. J'aurai besoin de savoir qui est dispo et de récupérer un acompte pour réserver. 
        Merci d'envoyer votre RIB et numéro de téléphone pour qu'on puisse s'organiser.
        Voilà le lien pour confirmer ta présence : {'[Départ retraite]({{.URL}})'}
        À bientôt !
        ---
        """,

        "Erreur de paiement - RIB nécessaire": f"""
        Rédige un email **sérieux et court**, annonçant une erreur de versement de salaire. 
        Il doit **rassurer** le destinataire et l'inciter à envoyer son **RIB** rapidement.

        - **But** : Obtenir un RIB sous prétexte d'une correction de paiement.
        - **Ton** : Professionnel et bienveillant.
        - **Signature** : {expediteur}.
        - **Langue** : Français.
        - **Destinataire** : {'{{.FirstName}}'} {'{{.LastName}}'}
        - **Faux lien** : {'[texte]({{.URL}})'}

        Exemple : 
        ---
        Bonjour {'{{.FirstName}}'} {'{{.LastName}}'},
        **Une erreur a été détectée dans votre paiement ce mois-ci**. Afin de procéder rapidement au virement, merci de vérifier votre RIB à cette adresse : {'[Mes coordonnées de paiement]({{.URL}})'}
        Désolé pour ce désagrément, nous faisons le nécessaire au plus vite.
        Cordialement,
        ---
        """,

        "Invitation à un événement exclusif": f"""
        Rédige un email **dynamique et engageant** tout en restant formel pour des employés, invitant à un événement professionnel restreint. 
        L'email doit **être convaincant** et inciter l'employé à répondre au mail avec ses **coordonnées personnelles**.

        - **But** : Récupérer des informations personnelles (nom, téléphone, RIB) sous couvert d'une invitation à un événement exclusif.
        - **Ton** : Enthousiaste et exclusif mais professionel et formel.
        - **Signature** : {expediteur}.
        - **Entreprise** : '{entreprise}'.
        - **Langue** : Français.
        - **Destinataire** : {'{{.FirstName}}'} {'{{.LastName}}'}
        - **Faux lien** : {'[texte]({{.URL}})'}

        Exemple : 
        ---
        Bonjour {'{{.FirstName}}'} {'{{.LastName}}'},
        🎉 {entreprise} organise un événement exclusif pour ses collaborateurs ! 
        Nombre de places limité, **inscrivez-vous vite** en remplissant le sondage avec vos noms, numéro de téléphone et RIB. 
        Lien pour vous inscrire : {'[Evènement exclusif]({{.URL}})'}.
        Ne manquez pas cette opportunité unique !
        Bien à vous,
        ---
        
        Si tu ne sais pas une information, n'en parle pas.
        """,

        "Mise à jour de sécurité urgente": f"""
        Rédige un **email officiel** annonçant une **mise à jour de sécurité obligatoire**. 
        Il doit inciter le destinataire à **se connecter** pour "mettre à jour" ses accès.

        - **But** : Faire croire à une mise à jour système pour obtenir des identifiants.
        - **Ton** : Sérieux et impersonnel.
        - **Signature** : {expediteur}.
        - **Langue** : Français.
        - **Destinataire** : {'{{.FirstName}}'} {'{{.LastName}}'}
        - **Faux lien** : {'[texte]({{.URL}})'}

        Exemple : 
        ---
        Bonjour {'{{.FirstName}}'} {'{{.LastName}}'},
        Dans le cadre de l'amélioration de la sécurité informatique de {entreprise}, une **mise à jour de vos accès** est nécessaire.  
        **Merci de vous connecter ici avec vos identifiants** : {'[Mise à jour des accès]({{.URL}})'} pour procéder à la mise à jour.
        Nous vous remercions pour votre coopération.
        ---
        """,
        
        "Organisation de covoiturage": f"""
        Rédige un email **convivial et engageant** pour organiser un covoiturage quotidien entre collègues.
        Le mail doit être **court et efficace**. Il doit inciter les destinataires à **répondre rapidement** avec leurs coordonnées.
        
        - **But** : Organiser un covoiturage et obtenir des coordonnées.
        - **Ton** : Amical et pratique.
        - **Signature** : {expediteur}.
        - **Langue** : Français.
        - **Destinataire** : {'{{.FirstName}}'} {'{{.LastName}}'}
        - **Faux lien** : {'[texte]({{.URL}})'}
        
        Exemple :
        ---
        Salut {'{{.FirstName}}'},
        Serais-tu partant pour organiser un covoiturage quotidien pour aller au travail ?
        Merci de remplir le sondage avec tes coordonnées et adresse postale pour qu'on puisse s'organiser !
        Sondage : {'[Sondage covoiturage]({{.URL}})'}
        À bientôt !
        ---
        """,
        
        "Chèques de voyage": f"""
        Rédige un email **formel et sérieux** annonçant la distribution de chèques voyage à tous les employés.
        Le mail doit être **court et clair**. Il doit inciter les destinataires à **répondre rapidement** avec leurs coordonnées.
        
        - **But** : Obtenir des coordonnées sous couvert de distribution de chèques voyage.
        - **Ton** : Formel et professionnel.
        - **Signature** : {expediteur}.
        - **Langue** : Français.
        - **Destinataire** : {'{{.FirstName}}'} {'{{.LastName}}'}
        - **Faux lien** : {'[texte]({{.URL}})'}
        
        Exemple :
        ---
        Bonjour {'{{.FirstName}}'} {'{{.LastName}}'},
        Nous avons le plaisir de vous annoncer la distribution de chèques voyage à tous les employés.
        Merci de remplir vos coordonnées postales pour recevoir votre chèque : {'[Formulaire de réception]({{.URL}})'}.
        Cordialement,
        ---
        """,
        
        "Salon à l'étranger": f"""
        Rédige un email **convaincant et professionnel** pour inviter des employés à un salon professionnel à l'étranger.
        Le mail doit être **court et clair**. Il doit inciter les destinataires à **répondre rapidement** avec leurs coordonnées (y compris postales).
        Ne précise pas de dates.
        
        - **But** : Obtenir des coordonnées sous couvert d'une invitation à un salon professionnel.
        - **Ton** : Convaincant et professionnel.
        - **Signature** : {expediteur}.
        - **Langue** : Français.
        - **Destinataire** : {'{{.FirstName}}'} {'{{.LastName}}'}
        - **Faux lien** : {'[texte]({{.URL}})'}
        
        Exemple :
        ---
        Bonjour {'{{.FirstName}}'} {'{{.LastName}}'},
        Nous avons le plaisir de vous inviter à un salon professionnel à l'étranger.
        Merci de répondre au formulaire avec vos coordonnées pour recevoir votre invitation et que nous puissions réserver vos billets d'avion et de logement.
        Lien : {'[Formulaire salon]({{.URL}})'}.
        Cordialement,
        ---
        
        Si tu ne sais pas une information, n'en parle pas.
        """,
        
        "Urgence médicale": f"""
        Rédige un email **sérieux et urgent** annonçant une urgence médicale et demandant des informations personnelles.
        Le mail doit être **court et clair**. Il doit inciter les destinataires à **répondre rapidement** avec leurs coordonnées (y compris postales).
        
        - **But** : Obtenir des coordonnées sous couvert d'une urgence médicale (services d'urgence & police).
        - **Ton** : Sérieux et urgent.
        - **Signature** : {expediteur}.
        - **Langue** : Français.
        - **Destinataire** : {'{{.FirstName}}'} {'{{.LastName}}'}
        - **Faux lien** : {'[texte]({{.URL}})'}
        
        Exemple :
        ---
        Urgent,
        Un collaborateur a eu un accident et nous avons besoin de vos coordonnées pour les fournir aux services d'urgence et de police.
        Merci de les renseigner sur le site {'[Services Urgence]({{.URL}})'} vos coordonnées pour que nous puissions les transmettre rapidement.
        Cordialement,
        ---
        """,
        
        "Support émotionnel": f"""
        Rédige un email **bienveillant et empathique** annonçant qu'un collègue a besoin de soutien émotionnel et que le destinataire a été choisi pour l'aider.
        Le mail doit être **court et clair**. Il doit inciter les destinataires à **répondre rapidement** avec leurs coordonnées (+ adresse mail PERSONNELLE).
        
        - **But** : Obtenir des coordonnées sous couvert de soutien émotionnel.
        - **Ton** : Bienveillant et empathique.
        - **Signature** : {expediteur}.
        - **Langue** : Français.
        - **Destinataire** : {'{{.FirstName}}'} {'{{.LastName}}'}
        - **Faux lien** : {'[texte]({{.URL}})'}
        
        Exemple :
        ---
        Salut {'{{.FirstName}}'},
        Un collègue a besoin de soutien émotionnel et nous avons pensé à toi pour l'aider.
        Merci de m'envoyer tes coordonnées sur le site pour que nous puissions te mettre en contact avec lui.
        Site : {'[Formulaire]({{.URL}})'}
        Cordialement,
        ---
        """,
    }

    return prompts.get(scenario, "Scénario non trouvé.")

def email_to_html(email: EmailInfo):
    """Convertit un email en HTML."""
    # Replace line breaks with HTML line breaks
    content_parsed = email.contenu_mail.replace("\n", "\n<br>")
    # Add <strong> tags awhen there are **
    # Note: it must add <strong> then </strong> to avoid nested tags
    while "**" in content_parsed:
        content_parsed = content_parsed.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
    # Replace link with a <a> tag
    while '[' in content_parsed and ']' in content_parsed and '(' in content_parsed and ')' in content_parsed:
        start_link = content_parsed.find('[')
        end_link = content_parsed.find(']')
        start_url = content_parsed.find('(', end_link)
        end_url = content_parsed.find(')', start_url)
        if start_link < end_link < start_url < end_url:
            link_text = content_parsed[start_link + 1:end_link]
            link_url = content_parsed[start_url + 1:end_url]
            content_parsed = content_parsed[:start_link] + f'<a href="{link_url}">{link_text}</a>' + content_parsed[end_url + 1:]
        else:
            break
    # Generate HTML
    html = f"<!DOCTYPE html>\n\
    <html lang=\"fr\">\n\
    <head>\n\
        <meta charset=\"UTF-8\">\n\
        <title>{email.objet_mail}</title>\n\
    </head>\n\
    <body>\n\
        {content_parsed}\n\
    </body>\n\
    </html>\
    "
    return html

def generate_phishing_email(user_data):
    """Génère un email de phishing à l'aide de Mistral via Ollama."""
    prompt = generate_prompt(user_data)
    # print(prompt)
    
    used_model = get_used_model()
    if not used_model:
        raise Exception("Aucun modèle n'est actuellement utilisé.")

    valid = False
    tries = 0
    while not valid:
        response: EmailInfo = ollama.chat(model=used_model, messages=[{"role": "user", "content": prompt}], format=EmailInfo.model_json_schema())
        response_obj = EmailInfo.model_validate_json(response.message.content)
        
        # Strip the email content
        lines = response_obj.contenu_mail.split("\n")
        response_obj.contenu_mail = ("\n".join([line.strip() for line in lines])).strip()
        valid = len(lines) > 1 and 'Dear ' not in response_obj.contenu_mail
        valid = valid and '[dest' not in response_obj.contenu_mail.lower()
        valid = valid and '[coll' not in response_obj.contenu_mail.lower()
        valid = valid and '[entr' not in response_obj.contenu_mail.lower()
        valid = valid and '[reci' not in response_obj.contenu_mail.lower()
        valid = valid and '<' not in response_obj.contenu_mail.lower() and '>' not in response_obj.contenu_mail.lower()
        valid = valid and len([line for line in lines if len(line.strip()) > 0]) > 3
        valid = valid and '[' in response_obj.contenu_mail and ']' in response_obj.contenu_mail
        valid = valid and '(' in response_obj.contenu_mail and ')' in response_obj.contenu_mail
        valid = valid and 'URL' in response_obj.contenu_mail
        
        if not valid:
            print("Email not valid, retrying...")
            # print(response_obj.contenu_mail)
            tries += 1
            if tries > 10:
                raise Exception("Impossible de générer un email valide. Réessayez plus tard / changez de modèle.")
    
    return {"object": response_obj.objet_mail, "content": response_obj.contenu_mail, "html": email_to_html(response_obj)}

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


def get_models():
    """Récupère la liste des modèles disponibles sur la base de données"""
    conn = get_db_connection()
    models = conn.execute("SELECT * FROM models").fetchall()
    conn.close()
    return models


def get_used_model():
    """Récupère le modèle actuellement utilisé dans la base de données"""
    conn = get_db_connection()
    model = conn.execute("SELECT name FROM models WHERE used = 1").fetchone()
    conn.close()
    return model[0] if model else None


def need_pull_model(model_name):
    """Vérifie si un modèle doit être téléchargé depuis Ollama"""
    models = get_ollama_status()
    for model in models:
        if model['name'].startswith(model_name):
            return False
    return True


def try_pull_model(model_name):
    """Tente de télécharger un modèle depuis Ollama"""
    def pull_model():
        ollama.pull(model=model_name)

    pull_thread = threading.Thread(target=pull_model)
    pull_thread.start()
    print(f"Téléchargement du modèle {model_name} en cours...")
    # pull_thread.join()


def set_used_model(model_name):
    """Met à jour le modèle utilisé dans la base de données"""
    conn = get_db_connection()
    conn.execute("UPDATE models SET used = 0")
    conn.execute("UPDATE models SET used = 1 WHERE name = ?", (model_name,))
    conn.commit()
    # print(f"Modèle {model_name} défini.")
    conn.close()
    need_pull = need_pull_model(model_name)
    print(f"Modèle {model_name} défini. Téléchargement nécessaire : {need_pull}")
    if need_pull:
        try_pull_model(model_name)
        
    return need_pull


def generate_ai_analysis(campaign_id):
    """
    Génère les 4 sections d'analyse (générale, détaillée, recommandations, conclusion)
    en se basant sur les statistiques de la campagne.
    Cette fonction s'inspire de la logique de generate_and_save_report_to_db sans sauvegarder en BDD.
    """
    # Importer la fonction get_campaign et la fonction utilitaire dict_to_obj
    from src.services.gophish_service import get_campaign
    from src.lib.goreport_lib import dict_to_obj

    # Instancier et configurer GoReport pour récupérer les infos de la campagne
    goreport = Goreport(report_format="word", config_file=None, google=False, verbose=False)
    
    # Récupération des données de campagne via l'appel API
    campaign_data = get_campaign(campaign_id)
    if campaign_data.get("error"):
        raise Exception(f"Erreur dans la récupération de la campagne ID {campaign_id}: {campaign_data.get('error')}")
    
    # Conversion du dictionnaire en objet pour compatibilité avec le reste du code
    goreport.campaign = dict_to_obj(campaign_data)
    
    # Traitement des données de la campagne
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

1. Analyse des résultats généraux : Résume l'efficacité de la campagne et les statistiques obtenues.
2. Recommandations : Donne 3 conseils sous forme de liste à puce pour éviter de se faire avoir par une attaque de phishing.
3. Conclusion : Message final de sensibilisation, synthétique et professionnel.

⚠️ Contraintes :
- Pas de Markdown, balises HTML ni caractères spéciaux (**, #, etc.).
- Texte clair, professionnel, structuré et en français uniquement.
- Utilise une mise en page lisible avec des titres bien visibles (ex : Titre sur une ligne seule, saut de ligne avant/après).
- Recommandations sous forme de liste numérotée, avec un saut de ligne entre chaque point.

Exemple pour les recommandations :
1. TITRE DE LA RECOMMANDATION
   Explication...

2. TITRE DE LA RECOMMANDATION
   Explication...

Rends le texte fluide, aéré et facile à lire pour une insertion directe dans un document Word.
"""
    # Récupération du modèle utilisé
    used_model = get_used_model()
    if not used_model:
        raise Exception("Aucun modèle n'est actuellement utilisé.")

    # Appel à l'IA via Ollama (ici modèle "mistral")
    response = ollama.chat(model=used_model, messages=[{"role": "user", "content": prompt}])
    texte = response.message.content.strip()
    return texte



def extract_html_from_llm(raw_response: str) -> str:
    match = re.search(r'<!DOCTYPE html>.*?</html>', raw_response, re.DOTALL | re.IGNORECASE)
    return match.group(0).strip() if match else "Erreur : HTML non trouvé."


def generate_phishing_landing(user_data):
    scenario_prompt = generate_prompt(user_data)

    prompt = f"""
    Génère uniquement le **code HTML complet** (et rien d'autre) d'un formulaire.
    C'est un formulaire qui sera ouvert quand la personne cliquera sur le lien dans le mail du scénario suivant :
    
    >>> DEBUT DU SCENARIO <<<
    "{scenario_prompt}".
    >>> FIN DU SCENARIO <<<

    Contraintes :
    - Langue : français
    - Ne commente pas ta réponse.
    - Réponds UNIQUEMENT avec le code HTML.
    - Structure HTML complète et autonome
    - Formulaire avec `action="{'{{.URL}}'}"`, champs correspondants aux informations demandées dans le scénario.
    - Design sobre et crédible (type institutionnel)
    - Tous les éléments HTML doivent être stylisés en CSS intégré dans le code HTML.
    - Ne mentionne pas le mail du scénario.
    - Formulaire non personalisé, aucun noms et aucun nom d'entreprise.
    """

    model = get_used_model()
    valid = False
    while not valid:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        html_code = extract_html_from_llm(response.message.content)
        valid = '{{.FirstName}}' not in html_code and '{{.LastName}}' not in html_code
        
    return html_code
