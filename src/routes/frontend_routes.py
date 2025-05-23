# Routes pour afficher les pages HTML, évite de tout mélanger dans le fichier principal app.py
import os
from flask import Blueprint, render_template, Flask, render_template, request, jsonify, redirect, url_for, session, send_file, abort
from src.services.llm_service import *
from src.services.smartphish_service import *
from src.services.report_service import *
import json
from io import BytesIO
from fpdf import FPDF
import subprocess
import tempfile
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from src.services.smartphish_service import get_templates
from src.services.report_service import *
from functools import wraps
from src.lib.custom_cve import search_user_agent_vulnerable

bp = Blueprint('frontend', __name__, static_folder='../static', template_folder='../templates')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Middleware pour vérifier l'authentification
@bp.before_request
def check_auth():
    allowed_routes = ["frontend.login_page", "auth.login"]

    if "user" not in session and request.endpoint not in allowed_routes:
        return redirect(url_for("frontend.login_page"))

@bp.route("/login")
def login_page():
    return render_template("login.html")

@bp.route("/register")
@admin_required
def register_page():
    # Appel GoPhish pour récupérer les utilisateurs
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/users/", headers=HEADERS, verify=False)
    users = []
    if response.status_code == 200:
        for u in response.json():
            if u["username"] == "admin":
                continue 
            role_obj = u.get("role", {})
            slug = role_obj.get("slug", "")
            role_label = "Administrateur" if slug == "admin" else "Utilisateur"
            users.append({
                "username": u["username"],
                "role": role_label
            })

    return render_template("register.html", users=users, current_user=session.get("user"))

@bp.route("/logout")
def logout():
    # session.pop("user", None)  # Supprime l'utilisateur de la session
    session.clear()
    return redirect(url_for("frontend.login_page"))



# Routes pour afficher les pages HTML

@bp.route('/')
def index():
    campaigns = get_campaigns()  # Récupérer les campagnes de la BD
    campaigns = [c for c in campaigns if c["status"] == "In progress"]
    return render_template('home.html', active_campaigns_length=len(campaigns))

@bp.route('/configuration')
def configuration():
    return render_template('configuration.html')



# ---------------------------
# Routes pour la page de création de campagne
# --------------------------- 

@bp.route('/new-campaign', methods=['GET'])
def new_campaign_page():
    """Affiche la page de création de campagne avec les éléments disponibles."""
    groups = get_groups()
    templates = get_templates()
    pages = get_landing_pages() 
    sending_profiles = get_sending_profiles()

    return render_template('new-campaign.html', 
                           groups=groups, 
                           templates=templates, 
                           pages=pages, 
                           sending_profiles=sending_profiles)

@bp.route('/new-campaign', methods=['POST'])
def create_new_campaign():
    """Reçoit les données du formulaire et envoie la requête à GoPhish."""
    data = request.get_json()
    return jsonify(create_campaign(data))


@bp.route('/follow-campaign')
def follow_campaign():
    campaigns = get_campaigns() 
    
    return render_template('follow-campaign.html', campaigns=campaigns)

@bp.route("/details_campaign/<int:campaign_id>")
def details_campaign(campaign_id):
    campaign = get_campaign(campaign_id)

    # Récupération Data
    summary = get_campaign_summary(campaign_id)

    if not campaign or "error" in campaign or not summary:
        return "Campagne non trouvée ou erreur", 404

    stats_api = summary.get("stats", {})
    stats = {
        "Emails envoyés": stats_api.get("sent", 0),
        "Emails ouverts": stats_api.get("opened", 0),
        "Liens cliqués": stats_api.get("clicked", 0),
        "Données soumises": stats_api.get("submitted_data", 0),
        "Emails signalés": stats_api.get("email_reported", 0)
    }

    # Payload pour les données soumises
    timeline = campaign.get("timeline", [])
    submissions = {}
    for event in timeline:
        if event.get("message") == "Submitted Data":
            email = event.get("email")
            try:
                details = json.loads(event.get("details", "{}"))
                payload = details.get("payload", {})
                submissions[email] = payload
            except json.JSONDecodeError:
                continue

    return render_template("details-campaign.html", campaign=campaign, stats=stats, submissions=submissions)


@bp.route("/campaign/<int:campaign_id>/cve")
def get_campaign_cve(campaign_id):
    import json
    # Récupère la campagne via ta fonction existante
    campaign = get_campaign(campaign_id)

    timeline = campaign.get("timeline", [])
    if not timeline:
        timeline = get_campaign_events(campaign_id)

    results = {}
    for event in timeline:
        email = event.get("email")
        user_agent = None
        details = event.get("details")
        if details and details.strip():
            try:
                details_obj = json.loads(details)
                user_agent = details_obj.get("browser", {}).get("user-agent")
            except Exception as e:
                print("DEBUG - Erreur de parsing des details pour l'événement:", event, e)
        
        if email and user_agent:
            vuln_info = search_user_agent_vulnerable(user_agent)
            if email not in results:
                results[email] = vuln_info
    return jsonify(results)








# ---------------------------
# Routes pour la partie LLM
# --------------------------- 

@bp.route('/generate-email', methods=['POST'])
def generate_email():
    """ Appelle LLM.py pour générer un email de phishing et le retourne en JSON. """
    data = request.json
    scenario = data.get("scenario")
    entreprise = data.get("entreprise", "")
    expediteur = data.get("expediteur", "")
    email_expediteur = data.get("email_expediteur", "")

    user_data = {
        "scénario": scenario,
        "entreprise": entreprise,
        "expéditeur": expediteur,
        "email_expediteur": email_expediteur
    }

    generated_email = generate_phishing_email(user_data)

    return jsonify({"object": generated_email['object'], "content": generated_email['content'], "html": generated_email['html']})



@bp.route('/generate-landing', methods=['POST'])
def generate_landing():
    data = request.json
    scenario = data.get("scenario")
    entreprise = data.get("entreprise", "")
    expediteur = data.get("expediteur", "")

    user_data = {
        "scénario": scenario,
        "entreprise": entreprise,
        "expéditeur": expediteur
    }

    try:
        html = generate_phishing_landing(user_data)
        return jsonify({"html": html})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/llm-status')
def llm_status():
    status = get_ollama_status()
    print(status)
    return render_template('llm-status.html', status=status)

@bp.route('/llm-status-get')
def llm_status_ge():
    status = get_ollama_status()
    return jsonify(status)

@bp.route('/llm-training')
def llm_training():
    return render_template('llm-training.html')

@bp.route('/llm-settings')
def llm_settings():
    models = get_models()
    return render_template('llm-settings.html', models=models)

@bp.route('/set-model', methods=['POST'])
def set_model_frontend():
    data = request.json
    model_name = data.get("model")
    need_pull = set_used_model(model_name)
    return jsonify({"result": "OK", "need_pull": need_pull})

@bp.route('/maj-status')
def maj_status():
    return render_template('maj-status.html')





# ------------------------------------------------------
# Routes pour les rapports de campagne
# ------------------------------------------------------
@bp.route('/generate-report/<int:campaign_id>', methods=['GET'])
def generate_report(campaign_id):
    force = request.args.get("force", "false").lower() == "true"

    campaigns = get_campaigns()
    campaign = next((c for c in campaigns if c["id"] == campaign_id), None)
    if not campaign:
        return jsonify({"error": "Campagne invalide"}), 400

    # Si la campagne est terminée, on force la régénération
    if campaign["status"] == "Completed":
        force = True

    try:
        path = generate_docx_with_goreport(campaign_id, force=force)
        if not path:
            return jsonify({"error": "Erreur génération fichier"}), 500
        return jsonify({
            "success": True,
            "url": f"/download-report/{campaign_id}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/report-exists/<int:campaign_id>')
def report_exists(campaign_id):

    latest_report = get_latest_goreport_docx(campaign_id)
    return jsonify({"exists": bool(latest_report)})


@bp.route('/download-report/<int:campaign_id>', methods=['GET'])
def download_report(campaign_id):

    return download_report_styled(campaign_id)






# ------------------------------------------------------
# Routes pour les groupes
# ------------------------------------------------------

@bp.route('/config-groups')
def config_groups():
    groups_data = get_groups() 
    return render_template('config-groups.html', groups=groups_data)

@bp.route('/config-groups/<int:group_id>', methods=['GET'])
def get_group_frontend(group_id):
    """
    Retourne UN groupe en JSON (pour remplir la modale "Edit Group").
    """
    group_data = get_groupsid(group_id)
    return jsonify(group_data)

@bp.route('/config-groups', methods=['POST'])
def newgroup_submit():
    """
    Crée un nouveau groupe depuis une requête JSON (Fetch API).
    Retourne une réponse JSON.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    name = data.get('name')
    targets = data.get('targets', [])

    if not name:
        return jsonify({"error": "Le champ 'name' est requis"}), 400
    
    
    response = create_group({"name": name, "targets": targets})

    if 'error' in response:
        return jsonify(response), 400

    return jsonify(response), 200

@bp.route('/config-groups/<int:group_id>', methods=['PUT'])
def update_group_frontend(group_id):
    """
    Reçoit la requête PUT du front-end, et met à jour ce groupe via GoPhish.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    
    if "id" not in data:
        data["id"] = group_id

    response = update_group(group_id, data)

    if "error" in response:
        return jsonify(response), 400

    return jsonify(response), 200

@bp.route('/config-groups/<int:group_id>', methods=['DELETE'])
def delete_group_frontend(group_id):
    """
    Supprime un groupe (DELETE) via GoPhish.
    """
    response = delete_group(group_id)
    return jsonify(response)







# ---------------------------
# Routes pour les templates de mail
# ---------------------------

@bp.route('/config-emails', methods=['GET'])
def config_emails():
    """
    Récupère la liste des email templates depuis la BD, puis rend la page config-emails.html avec ces données.
    """
    email_templates = get_templates()
    return render_template('config-emails.html', email_templates=email_templates)

@bp.route('/templates', methods=['POST'])
def create_template_frontend():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    # Extraire champs nécessaires
    name = data.get("name")
    subject = data.get("subject")
    text = data.get("text", "")
    html = data.get("html", "")

    if not name or not subject:
        return jsonify({"error": "Nom et sujet sont obligatoires"}), 400
    if not text and not html:
        return jsonify({"error": "Au moins 'text' ou 'html' est obligatoire"}), 400

    payload = {
        "name": name,
        "subject": subject,
        "text": text,
        "html": html,
        "attachments": []
    }

    response = create_template(payload)
    if "error" in response:
        return jsonify(response), 400 
    return jsonify(response), 201

@bp.route('/templates/<int:template_id>', methods=['GET'])
def get_template_frontend(template_id):
    """
    Récupère UN template en JSON pour remplir la modale d’édition (front).
    """
    data = get_template(template_id)
    return jsonify(data)

@bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template_frontend(template_id):
    """
    Reçoit le JSON pour modifier le template via GoPhish.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    # GoPhish exige un template complet : id, name, subject, text/html...
    if "id" not in data:
        data["id"] = template_id

    response = update_template(template_id, data)
    if "error" in response:
        return jsonify(response), 400

    return jsonify(response), 200

@bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template_frontend(template_id):
    """
    Supprime un template via GoPhish.
    """
    response = delete_template(template_id)
    return jsonify(response)







# ---------------------------
# Routes pour les Sending Profiles (Profils SMTP)
# ---------------------------

@bp.route('/config-smtp')
def config_smtp():
    smtp_profiles = get_sending_profiles()  
    return render_template('config-smtp.html', smtp_profiles=smtp_profiles)

@bp.route('/config-smtp/<int:profile_id>', methods=['GET'])
def get_smtp_profile(profile_id):
    return jsonify(get_sending_profile(profile_id))

@bp.route('/config-smtp', methods=['POST'])
def new_smtp_submit():
    data = request.get_json()
    return jsonify(create_sending_profile(data))

@bp.route('/config-smtp/<int:profile_id>', methods=['PUT'])
def update_smtp_submit(profile_id):
    data = request.get_json()
    return jsonify(update_sending_profile(profile_id, data))

@bp.route('/config-smtp/<int:profile_id>', methods=['DELETE'])
def delete_smtp(profile_id):
    return jsonify(delete_sending_profile(profile_id))







# ---------------------------
# Routes pour les Landing Pages
# ---------------------------

@bp.route('/config-landing-pages', methods=['GET'])
def config_landing_pages():
    """
    Récupère la liste des landing pages et rend la page de configuration.
    """
    landing_pages = get_landing_pages()
    return render_template('config-landing-pages.html', landing_pages=landing_pages)

@bp.route('/config-landing-pages/<int:landing_page_id>', methods=['GET'])
def get_landing_page_frontend(landing_page_id):
    """
    Retourne une Landing Page en JSON pour remplissage de formulaire.
    """
    data = get_landing_page(landing_page_id)
    return jsonify(data)

@bp.route('/config-landing-pages', methods=['POST'])
def create_landing_page_frontend():
    """
    Crée une nouvelle Landing Page.
    """
    data = request.get_json()
    if not data or "name" not in data or "html" not in data:
        return jsonify({"error": "Nom et HTML sont requis"}), 400

    response = create_landing_page(data)
    return jsonify(response), 201 if "error" not in response else 400

@bp.route('/config-landing-pages/<int:landing_page_id>', methods=['PUT'])
def update_landing_page_frontend(landing_page_id):
    """
    Met à jour une Landing Page.
    """
    data = request.get_json()
    if not data or "id" not in data:
        data["id"] = landing_page_id

    response = update_landing_page(landing_page_id, data)
    return jsonify(response), 200 if "error" not in response else 400

@bp.route('/config-landing-pages/<int:landing_page_id>', methods=['DELETE'])
def delete_landing_page_frontend(landing_page_id):
    """
    Supprime une Landing Page.
    """
    response = delete_landing_page(landing_page_id)
    return jsonify(response)

@bp.route('/import_site', methods=['POST'])
def import_site_frontend():
    data = request.get_json()
    response = import_site(data) 
    return jsonify(response)


# ---------------------------
@bp.route("/mon-compte")
def mon_compte_page():
    return render_template("account.html", current_user=session.get("user"))
@bp.route("/mon-compte/update", methods=["PUT"])
def update_mon_compte():
    data = request.json
    current_user = session.get("user")
    new_username = data.get("username")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not current_user:
        return jsonify({"error": "Utilisateur non connecté"}), 401

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (current_user,)).fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "Utilisateur introuvable"}), 404

    # Vérification de mot de passe uniquement si changement demandé
    if new_password:
        if not old_password:
            conn.close()
            return jsonify({"error": "Mot de passe actuel requis pour changer le mot de passe"}), 400

        if not bcrypt.checkpw(old_password.encode("utf-8"), user["hash"].encode("utf-8")):
            conn.close()
            return jsonify({"error": "Mot de passe actuel incorrect"}), 401

        import re
        regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(regex, new_password):
            conn.close()
            return jsonify({
                "error": "Mot de passe trop faible",
                "details": """
                    <h5 style='text-align:left; font-size:16px'>Mot de passe trop faible</h5>
                    <ul style='text-align:left; font-size:16px; margin-top:10px'>
                        <li>8 caractères minimum</li>
                        <li>Une majuscule, une minuscule, un chiffre, un caractère spécial</li>
                    </ul>
                """
            }), 400

        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn.execute("UPDATE users SET hash = ? WHERE username = ?", (new_hash, current_user))

    # Changement du nom d’utilisateur
    if new_username and new_username != current_user:
        conn.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, current_user))
        session["user"] = new_username  # Mise à jour de la session
        current_user = new_username

    conn.commit()
    conn.close()

    return jsonify({"message": "Mise à jour réussie"}), 200

