import os
import json

class ConfigManager:
    def __init__(self, config_path="C:/MesScripts/config.json"):
        self.config_path = config_path
        self.api_key = ''
        self.download_path = os.getcwd()
        self.load_config()
        
    def load_config(self):
        """Charger la configuration depuis le fichier"""
        try:
            with open(self.config_path, "r", encoding='utf-8') as f:
                config = json.load(f)
                self.api_key = config.get('youtube_api_key', '')
                self.download_path = config.get('download_path', os.getcwd())
        except (FileNotFoundError, json.JSONDecodeError):
            self.api_key = ''
            self.download_path = os.getcwd()
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
    def save_config(self):
        """Sauvegarder la configuration dans le fichier"""
        try:
            config = {
                'youtube_api_key': self.api_key,
                'download_path': self.download_path
            }
            with open(self.config_path, "w", encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            
    def set_api_key(self, api_key):
        """Définir la clé API"""
        self.api_key = api_key
        self.save_config()
        
    def set_download_path(self, download_path):
        """Définir le chemin de téléchargement"""
        self.download_path = download_path
        self.save_config()