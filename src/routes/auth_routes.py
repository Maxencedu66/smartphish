import requests
import sqlite3
import bcrypt
from flask import Blueprint, request, jsonify, session
from src.config import Config 

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_bp = Blueprint("auth", __name__)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Config.GOPHISH_API_KEY}"
}

# Fonction pour se connecter à la base de données SQLite
def get_db_connection():
    conn = sqlite3.connect("./src/data/smartphish.db")
    conn.row_factory = sqlite3.Row  
    return conn

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Champs requis"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 401

    stored_hash = user["hash"]  # Récupération du hash depuis SQLite

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        session["user"] = username  # Stocker l'utilisateur dans la session Flask
        session["role"] = "admin" if user["role_id"] == 1 else "user"
        return jsonify({"message": "Connexion réussie"}), 200
    else:
        return jsonify({"error": "Mot de passe incorrect"}), 401


@auth_bp.route("/register", methods=["POST"])
def create_user():
    """Inscription d'un utilisateur via l'API Smartphish"""
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")
    role_id = 1 if role == "admin" else 2

    # Vérifier si l'utilisateur existe déjà dans smartphish
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/users/", headers=HEADERS, verify=False)
    
    if response.status_code == 200:
        users = response.json()
        existing_user = next((u for u in users if u["username"] == username), None)
        if existing_user:
            return jsonify({"error": "Ce nom d'utilisateur est déjà pris"}), 400
    else:
        return jsonify({"error": "Impossible de vérifier les utilisateurs existants"}), 500

    new_user = {
        "username": username,
        "password": password,
        "role": role
    }

    create_response = requests.post(f"{Config.GOPHISH_API_URL}/api/users/", json=new_user, headers=HEADERS, verify=False)
    
    if create_response.status_code == 200:
        return jsonify({"message": "Inscription réussie"}), 201
    else:
        return jsonify({"error": "Erreur lors de l'inscription", "details": create_response.text}), 500


@auth_bp.route("/users", methods=["GET"])
def list_users():
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/users/", headers=HEADERS, verify=False)
    if response.status_code == 200:
        users = []
        for u in response.json():
            role_obj = u.get("role", {})
            slug = role_obj.get("slug", "")
            role_label = "Administrateur" if slug == "admin" else "Utilisateur"
            print(f"🔹 Utilisateur : {u['username']} | Rôle slug : {slug}")

            users.append({
                "id": u["id"],
                "username": u["username"],
                "role": role_label
            })
        return jsonify(users)
    return jsonify({"error": "Erreur lors de la récupération des utilisateurs"}), 500


@auth_bp.route("/users/<username>", methods=["PUT"])
def update_user(username):
    data = request.json
    new_username = data.get("username")
    role_slug = data.get("role", "user")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    print("Payload reçu :", data)

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "Utilisateur introuvable"}), 404

    if old_password and new_password:
        stored_hash = user["hash"]
        if not bcrypt.checkpw(old_password.encode("utf-8"), stored_hash.encode("utf-8")):
            conn.close()
            return jsonify({"error": "Ancien mot de passe incorrect"}), 401

        import re
        regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(regex, new_password):
            conn.close()
            return jsonify({"error": "Nouveau mot de passe non valide"}), 400

        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn.execute(
            "UPDATE users SET hash = ?, role_id = ? WHERE username = ?",
            (hashed_pw, 1 if role_slug == "admin" else 2, username)
        )
        conn.commit()
    else:
        conn.execute(
            "UPDATE users SET role_id = ? WHERE username = ?",
            (1 if role_slug == "admin" else 2, username)
        )
        conn.commit()

    conn.close()

    # Update GoPhish
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/users/", headers=HEADERS, verify=False)
    if response.status_code != 200:
        return jsonify({"error": "Erreur récupération GoPhish"}), 500

    users = response.json()
    gophish_user = next((u for u in users if u["username"] == username), None)
    if not gophish_user:
        return jsonify({"error": "Utilisateur introuvable dans GoPhish"}), 404

    payload = {
        "username": new_username,
        "role": role_slug
    }

    if old_password and new_password:
        payload["password"] = new_password

    update_response = requests.put(
        f"{Config.GOPHISH_API_URL}/api/users/{gophish_user['id']}",
        json=payload,
        headers=HEADERS,
        verify=False
    )

    print("Réponse GoPhish :", update_response.status_code, update_response.text)

    if update_response.status_code != 200:
        return jsonify({"error": f"Erreur API GoPhish: {update_response.text}"}), 500

    return jsonify({"message": "Utilisateur modifié avec succès"}), 200






@auth_bp.route("/users/<username>", methods=["DELETE"])
def delete_user(username):
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/users/", headers=HEADERS, verify=False)
    if response.status_code == 200:
        users = response.json()
        user = next((u for u in users if u["username"] == username), None)
        # if user:
        #     delete_response = requests.delete(f"{Config.GOPHISH_API_URL}/api/users/{user['id']}", headers=HEADERS, verify=False)
        #     return jsonify(delete_response.json()), delete_response.status_code
        if user:
            delete_response = requests.delete(f"{Config.GOPHISH_API_URL}/api/users/{user['id']}", headers=HEADERS, verify=False)
            
            if delete_response.status_code == 200 or delete_response.status_code == 204:
                return jsonify({"message": f"Utilisateur {username} supprimé avec succès"}), 200
            else:
                return jsonify({"error": "Erreur lors de la suppression", "details": delete_response.text}), 500

    
    return jsonify({"error": "Utilisateur introuvable"}), 404
