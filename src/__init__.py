# Initialisation du module Flask
from flask import Flask
from src.routes.frontend_routes import bp as frontend_bp
from src.routes.llm_routes import llm_bp  # Ajout du blueprint LLM
from src.routes.gophish_routes import gophish_bp  # Ajout du blueprint GoPhish

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Enregistrer les routes
    app.register_blueprint(frontend_bp)
    app.register_blueprint(llm_bp, url_prefix="/api")  # Préfixe /api pour organiser les routes backend
    app.register_blueprint(gophish_bp, url_prefix='/api/gophish') # Enregistrer les routes GoPhish

    return app
