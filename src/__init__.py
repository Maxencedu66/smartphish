# Initialisation du module Flask
from flask import Flask
from src.routes.frontend_routes import bp as frontend_bp

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Enregistrer les routes
    app.register_blueprint(frontend_bp)

    return app

