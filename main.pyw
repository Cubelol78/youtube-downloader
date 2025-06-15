#!/usr/bin/env python3
"""
MusicDL - Téléchargeur de Musique YouTube
Point d'entrée principal de l'application
"""

import sys
import os
import subprocess
import importlib.util

def check_and_install_package(package_name, import_name=None):
    """
    Vérifie si un paquet est installé, et l'installe avec pip si ce n'est pas le cas.
    L'installation se fait en silence.
    """
    if import_name is None:
        import_name = package_name.replace('-', '_').split('==')[0]

    # Vérifie si le module peut être importé
    spec = importlib.util.find_spec(import_name)
    if spec is None:
        print(f"Le paquet '{package_name}' n'est pas trouvé. Installation en cours...")
        try:
            # Utilise python -m pip pour garantir l'utilisation du bon interpréteur
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"'{package_name}' a été installé avec succès.")
            # Notifie importlib que de nouveaux modules sont disponibles
            importlib.invalidate_caches()
        except subprocess.CalledProcessError as e:
            print(f"ERREUR: Impossible d'installer le paquet '{package_name}'.")
            print(f"Veuillez l'installer manuellement en utilisant: pip install {package_name}")
            print(f"Erreur: {e}")
            sys.exit(1) # Quitte l'application si une dépendance cruciale ne peut être installée

def main():
    """Fonction principale de l'application."""
    # Vérifie et installe les dépendances nécessaires au démarrage
    check_and_install_package('google-api-python-client', 'googleapiclient')

    # Ajoute le répertoire courant au path pour les imports locaux.
    # C'est fait ici pour s'assurer que les modules locaux sont trouvés après l'installation des paquets.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Les imports des modules de l'application sont faits APRÈS la vérification des dépendances
    # pour éviter les ImportError si les paquets n'étaient pas encore installés.
    try:
        from main_gui import MusicDLGUI
    except ImportError as e:
        print(f"Erreur lors de l'importation des modules de l'application: {e}")
        print("Veuillez vous assurer que tous les fichiers (.py) de l'application sont dans le même répertoire.")
        sys.exit(1)

    # Lancement de l'interface graphique
    try:
        app = MusicDLGUI()
        app.run()
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors de l'exécution de l'application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
