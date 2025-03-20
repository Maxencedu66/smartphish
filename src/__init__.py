import os
from flask import Flask
from flask_session import Session
from src.routes.frontend_routes import bp as frontend_bp
from src.routes.llm_routes import llm_bp
from src.routes.gophish_routes import gophish_bp
from src.routes.auth_routes import auth_bp
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement depuis .env


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Configurer les sessions
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "changeme")
    app.config["SESSION_TYPE"] = "filesystem"  # Stocke la session dans un fichier local
    Session(app)  # Initialise la gestion de session

    # Enregistrement des blueprints
    app.register_blueprint(frontend_bp)
    app.register_blueprint(llm_bp, url_prefix="/api")
    app.register_blueprint(gophish_bp, url_prefix="/api/gophish")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app
