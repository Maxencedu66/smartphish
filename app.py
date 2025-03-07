import subprocess
import signal
import sys
import os
from src import create_app

# Définir le chemin du fichier `docker-compose.yml`
DOCKER_COMPOSE_PATH = os.path.join(os.path.dirname(__file__), "docker/docker-compose.yml")

app = create_app()

def start_docker():
    """Démarre Docker et le conteneur GoPhish si ce n'est pas déjà fait."""
    try:
        print("🔹 Vérification si Docker tourne...")
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("✅ Docker est actif.")
    except subprocess.CalledProcessError:
        print("❌ Docker n'est pas démarré. Démarrage en cours...")
        subprocess.run(["sudo", "systemctl", "start", "docker"], check=True)

    print("🚀 Lancement de GoPhish via Docker Compose...")
    subprocess.run(["docker-compose", "-f", DOCKER_COMPOSE_PATH, "up", "-d"], check=True)

def stop_docker():
    """Arrête proprement Docker à la fermeture de l'application Flask."""
    print("\n🛑 Fermeture de l'application, arrêt de Docker...")
    subprocess.run(["docker-compose", "-f", DOCKER_COMPOSE_PATH, "down"], check=True)
    sys.exit(0)

# Capture des signaux pour arrêter Docker proprement quand Flask est fermé
signal.signal(signal.SIGINT, lambda sig, frame: stop_docker())  # CTRL+C
signal.signal(signal.SIGTERM, lambda sig, frame: stop_docker())  # Arrêt système

if __name__ == '__main__':
    start_docker()  # Démarrer Docker avant Flask
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        stop_docker()
