# Routes pour afficher les pages HTML, évite de tout mélanger dans le fichier principal app.py

from flask import Blueprint, render_template

bp = Blueprint('frontend', __name__, static_folder='../static', template_folder='../templates')

@bp.route('/')
def index():
    return render_template('index.html')


#@bp.route('/dashboard')
#def dashboard():
#    return render_template('dashboard.html')

