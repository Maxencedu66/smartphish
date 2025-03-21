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
        return jsonify({"message": "Connexion réussie"}), 200
    else:
        return jsonify({"error": "Mot de passe incorrect"}), 401


@auth_bp.route("/register", methods=["POST"])
def register():
    """Inscription d'un utilisateur via l'API GoPhish"""
    data = request.json
    username = data.get("username")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if not username or not password or not confirm_password:
        return jsonify({"error": "Tous les champs sont requis"}), 400

    if password != confirm_password:
        return jsonify({"error": "Les mots de passe ne correspondent pas"}), 400

    # Vérifier si l'utilisateur existe déjà dans GoPhish
    response = requests.get(f"{Config.GOPHISH_API_URL}/api/users/", headers=HEADERS, verify=False)
    print("🔹 Réponse utilisateurs GoPhish:", response.status_code, response.text)
    
    if response.status_code == 200:
        users = response.json()
        existing_user = next((u for u in users if u["username"] == username), None)
        if existing_user:
            return jsonify({"error": "Ce nom d'utilisateur est déjà pris"}), 400
    else:
        return jsonify({"error": "Impossible de vérifier les utilisateurs existants"}), 500

    # Création du nouvel utilisateur via GoPhish
    new_user = {
        "username": username,
        "password": password,
        "role": "user"
    }

    create_response = requests.post(f"{Config.GOPHISH_API_URL}/api/users/", json=new_user, headers=HEADERS, verify=False)
    
    print("🔹 Réponse création utilisateur GoPhish:", create_response.status_code, create_response.text)

    if create_response.status_code == 200:
        return jsonify({"message": "Inscription réussie"}), 201
    else:
        return jsonify({"error": "Erreur lors de l'inscription", "details": create_response.text}), 500
