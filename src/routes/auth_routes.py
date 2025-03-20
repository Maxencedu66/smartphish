from flask import Blueprint, request, jsonify, session

auth_bp = Blueprint("auth", __name__)

USER_DATA = {
    "username": "admin",
    "password": "password123"
}

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == USER_DATA["username"] and password == USER_DATA["password"]:
        session["user"] = username

        return jsonify({"message": "Connexion réussie"}), 200

    return jsonify({"error": "Identifiants invalides"}), 401
