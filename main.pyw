#!/usr/bin/env python3
"""
MusicDL - Téléchargeur de Musique YouTube
Point d'entrée principal de l'application
"""

import sys
import os

# Ajouter le répertoire courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_gui import MusicDLGUI

def main():
    """Fonction principale"""
    try:
        app = MusicDLGUI()
        app.run()
    except Exception as e:
        print(f"Erreur lors du lancement de l'application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()