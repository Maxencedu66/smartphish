# SmartPhish - Génération de campagnes de phishing personnalisées par IA

SmartPhish est une solution innovante qui utilise l'intelligence artificielle pour générer des campagnes de phishing personnalisées. Ce projet repose sur **Flask** pour le backend, **GoPhish** pour la gestion des campagnes et **Ollama** pour l'exécution locale d'un modèle de langage (*LLM*).

---

## 🚀 Installation et Lancement

### 📌 Prérequis

Avant de lancer l'application, assurez-vous d'avoir installé les éléments suivants :
- **Python 3.8+** installé sur votre machine
- **Docker** (optionnel, recommandé pour GoPhish)
- **Ollama** installé pour l’exécution locale du modèle de langage
- **Git** (pour cloner le projet)

---

### 🔧 Étapes d'installation

1. Cloner le projet et accéder au répertoire.
2. Créer et activer un environnement virtuel.
```bash
    python -m venv venv
    source venv/bin/activate   # Sur macOS/Linux
    venv\Scripts\activate      # Sur Windows
   ```
3. Installer les dépendances du projet.
```bash
    pip install -r requirements.txt
   ```
4. Installer et exécuter Ollama avec Mistral.
```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ollama run mistral #A retirer une fois automatiser dnas le code
   ```
5. Lancer l’application.
```bash
    python app.py
   ```
---

## 🌍 Accéder à SmartPhish

Une fois l’application démarrée, ouvrez votre navigateur et accédez à l’URL suivante :

🔗 **http://127.0.0.1:5000/** *(ou une autre adresse si spécifiée dans `app.py`)*

L'interface utilisateur vous permettra de créer et gérer vos campagnes de phishing personnalisées.

---

## ⚙️ Fonctionnalités principales

- Création et gestion des campagnes de phishing via **GoPhish**.
- Génération automatique des emails grâce à un modèle **LLM** (*Mistral via Ollama*).
- Personnalisation avancée des messages pour une meilleure simulation des attaques.
- Tableau de bord interactif pour suivre les résultats et performances des campagnes.
- Déploiement simplifié grâce à Docker.

---

# 📂 Arborescence du projet SmartPhish

## 🏗️ Structure des fichiers

```plaintext
smartphish/
│-- app.py                    # Point d’entrée de l’application Flask
│-- requirements.txt           # Liste des dépendances Python
│-- Dockerfile                 # Fichier Docker (optionnel)
│-- README.md                  # Documentation du projet
│-- LICENSE                    # Licence du projet
│
│-- src/                       # Dossier contenant les modules principaux
│   ├── routes/                # Routes Flask pour GoPhish, LLM et UI
│   │   ├── gophish_routes.py  # Routes liées à GoPhish
│   │   ├── llm_routes.py      # Routes liées à l'IA (LLM)
│   │   ├── frontend_routes.py # Routes pour le frontend
│   │
│   ├── services/              # Logique métier et interaction avec les API
│   │   ├── gophish_service.py # Gestion des interactions avec GoPhish
│   │   ├── llm_service.py     # Intégration avec Ollama et le LLM
│   │
│   ├── templates/             # Fichiers HTML pour le frontend
│   │   ├── index.html         # Page d’accueil de l'application
│   │   ├── dashboard.html     # Interface de gestion des campagnes
│   │
│   ├── static/                # Fichiers CSS, JavaScript et assets
│   │   ├── css/               # Feuilles de style CSS
│   │   ├── js/                # Scripts JavaScript
│   │   ├── images/            # Images et logos
│   │
│   ├── database/              # Scripts et fichiers liés à la base de données
│   │   ├── db.sqlite          # Base de données SQLite (si utilisée)
│   │   ├── models.py          # Définition des modèles de données
│   │
│   ├── config.py              # Configuration de l'application
│
│-- tests/                     # Tests unitaires et fonctionnels
│   ├── test_api.py            # Tests pour l'API
│   ├── test_services.py       # Tests pour les services
│
│-- logs/                      # Dossier contenant les logs d'exécution (optionnel)
│-- docker-compose.yml         # Fichier Docker Compose pour le déploiement
```

---

## 🛠 Dépannage

### Problème de connexion avec Ollama ?
Assurez-vous que **Ollama** est bien actif avant de démarrer l’application.

### Erreur de dépendances Python ?
Essayez de mettre à jour pip et de réinstaller les dépendances.

### Problème avec GoPhish ?
Si vous utilisez Docker, vérifiez que le conteneur est bien lancé. Sinon, assurez-vous que **GoPhish** est bien configuré et accessible.

---

## 🏆 Contributeurs

- **Maxence Bouchadel** (Chef de projet)
- **Thomas Jeanjacquot** (Secrétaire, API & Backend)
- **Maël Cainjo Regeard** (Intégration IA)
- **Dylan Fournier** (Frontend et liaison backend)
- **Valentin Choquet** (Frontend)


---

## 📜 Licence

Ce projet est sous licence **MIT** – voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

