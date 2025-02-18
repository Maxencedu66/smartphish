# Initialisation du module Flask
from flask import Flask
from src.routes.frontend_routes import bp as frontend_bp
from src.routes.llm_routes import bp as llm_bp  # Ajout du blueprint LLM

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Enregistrer les routes
    app.register_blueprint(frontend_bp)
    app.register_blueprint(llm_bp, url_prefix="/api")  # Préfixe /api pour organiser les routes backend

    return app
