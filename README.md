# SmartPhish - Génération de campagnes de phishing personnalisées par IA

SmartPhish est une solution innovante qui utilise l'intelligence artificielle pour générer des campagnes de phishing personnalisées. Ce projet repose sur **Flask** pour le backend, **GoPhish** pour la gestion des campagnes et **Ollama** pour l'exécution locale d'un modèle de langage (*LLM*).

---

## 🚀 Installation et Lancement

### 📌 Prérequis

Avant de lancer l'application, assurez-vous d'avoir installé les éléments suivants :

- **Python 3.8+** installé sur votre machine  
- **Docker**  
- **Ollama** installé pour l’exécution locale du modèle de langage :  

  - **Linux** :  
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
  - **Windows** : [Télécharger Ollama](https://ollama.com/download/windows)  
  - **Mac** : [Télécharger Ollama](https://ollama.com/download/mac)  
    - Ou avec Homebrew :  
      ```bash
      brew install --cask ollama
      ```

- **Git** pour cloner le projet (sinon, téléchargez-le en ZIP)

---

### 🔧 Étapes d'installation

1. **Cloner le projet et accéder au répertoire** :
   ```bash
   git clone https://github.com/Maxencedu66/smartphish.git
   cd smartphish
   ```

2. Créer et activer un environnement virtuel :
```bash
    python -m venv venv
    source venv/bin/activate   # Sur macOS/Linux
    venv\Scripts\activate      # Sur Windows
   ```
3. Installer les dépendances du projet :
```bash
    pip install -r requirements.txt
   ```
4. Installer Mistral en local (4Go requis) :
```bash
    ollama pull mistral 
   ```
5. Sur macOS et Windows, assurez-vous que Docker Desktop est bien lancé afin d'activer le moteur Docker.

6. Lancer l’application.
```bash
    python app.py
   ```
---

## 🌍 Accéder à SmartPhish

Une fois l’application démarrée, ouvrez votre navigateur et accédez à l’adresse suivante :

🔗 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)** *(ou une autre adresse si spécifiée dans `app.py`)*

Pour vous connecter à l'interface administrateur, utilisez les identifiants suivants :

| 🔑 Identifiant administrateur |              |
| ----------------------------- | ------------ |
| **Nom d'utilisateur :**       | `admin`      |
| **Mot de passe :**            | `CyberProjet`|

> **Remarque :** En contexte de production (version SaaS), ces identifiants seraient transmis via un canal sécurisé séparé pour garantir leur confidentialité.

Après connexion, vous pourrez accéder à toutes les fonctionnalités de l'application, notamment la création d'autres comptes utilisateurs et la gestion complète de vos campagnes de phishing personnalisées.

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
│   │   ├── smartphish.db      # Base de données SQLite
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
Assurez-vous que **Ollama** est bien actif avant de démarrer l’application et que vous avez bien téléchargé le modèle Mistral.

### Problème avec le lancement ?
Pensez bien à démarrer docker avant de lancer l'application et lors de la fermeture de SmartPhish, faire Ctrl + C dans le terminal pour arrêter proprement le docker et SmartPhish.

---

## 🏆 Contributeurs

- **Maxence Bouchadel** (Chef de projet, Backend, IA)
- **Thomas Jeanjacquot** (Secrétaire, API & Backend)
- **Maël Cainjo Regeard** (Intégration IA)
- **Dylan Fournier** (Frontend et liaison backend)
- **Valentin Choquet** (Frontend)


---

## 📜 Licence

### 🔹 Licence de GoPhish
Le logiciel **GoPhish** est sous licence **MIT**, ce qui signifie qu'il peut être utilisé, modifié et distribué librement, y compris pour des **usages commerciaux**. Son code source étant open-source, nous avons pu l'intégrer à **SmartPhish** sans restriction.

Source : [GoPhish GitHub](https://github.com/gophish/gophish)

### 🔹 Licence du modèle **Mistral** (Modèle léger)
Le modèle **Mistral 7B** est publié sous **licence Apache 2.0**, une licence permissive qui autorise l'utilisation, la modification et la distribution du modèle, y compris à des fins commerciales. Cela nous permet d'exécuter **Mistral 7B** localement via **Ollama** sans contraintes de licence.

Source : [Mistral AI](https://mistral.ai/news/announcing-mistral-7b/)

---

En intégrant ces technologies, nous nous assurons que **SmartPhish** respecte pleinement les droits d'utilisation des outils et modèles utilisés.

---

