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
    password = data.get("password")
    role_slug = data.get("role", "user")

    try:
        # 🔍 Récupération de tous les utilisateurs
        response = requests.get(f"{Config.GOPHISH_API_URL}/api/users/", headers=HEADERS, verify=False)
        if response.status_code != 200:
            return jsonify({"error": "Impossible de récupérer les utilisateurs"}), 500

        users = response.json()
        user = next((u for u in users if u["username"] == username), None)
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        user_id = user["id"]  # ✅ c’est cet ID qu’il faut utiliser dans l’URL
        payload = {
            "username": new_username,
            "password": password,
            "role": role_slug
        }

        print(f"🔧 Modification utilisateur ID={user_id} ➜ {payload}")

        update_response = requests.put(
            f"{Config.GOPHISH_API_URL}/api/users/{user_id}",
            json=payload,
            headers=HEADERS,
            verify=False
        )

        if update_response.status_code == 200:
            return jsonify({"message": "Utilisateur modifié avec succès"}), 200
        else:
            return jsonify({"error": "Erreur lors de la mise à jour", "details": update_response.text}), 500

    except Exception as e:
        return jsonify({"error": "Erreur interne", "details": str(e)}), 500




@auth_bp.route("/users/<username>", methods=["DELETE"])
def delete_user(username):
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/users/", headers=HEADERS, verify=False)
    if response.status_code == 200:
        users = response.json()
        user = next((u for u in users if u["username"] == username), None)
        if user:
            delete_response = requests.delete(f"{Config.GOPHISH_API_URL}/api/users/{user['id']}", headers=HEADERS, verify=False)
            return jsonify(delete_response.json()), delete_response.status_code
    return jsonify({"error": "Utilisateur introuvable"}), 404
