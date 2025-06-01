import os
import json

class ConfigManager:
    def __init__(self, config_path="C:/MesScripts/config.json"):
        self.config_path = config_path
        self.api_key = ''
        self.download_path = os.getcwd()
        self.concurrent_downloads_limit = 2 # Nouvelle option: limite de téléchargements simultanés, valeur par défaut
        self.load_config()
        
    def load_config(self):
        """Charger la configuration depuis le fichier"""
        try:
            with open(self.config_path, "r", encoding='utf-8') as f:
                config = json.load(f)
                self.api_key = config.get('youtube_api_key', '')
                self.download_path = config.get('download_path', os.getcwd())
                # Charger la nouvelle option, avec une valeur par défaut si elle n'existe pas
                self.concurrent_downloads_limit = config.get('concurrent_downloads_limit', 2)
                # S'assurer que la valeur est dans les limites acceptables
                if not (1 <= self.concurrent_downloads_limit <= 15):
                    self.concurrent_downloads_limit = 2 # Réinitialiser si hors limites
        except (FileNotFoundError, json.JSONDecodeError):
            self.api_key = ''
            self.download_path = os.getcwd()
            self.concurrent_downloads_limit = 2
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
    def save_config(self):
        """Sauvegarder la configuration dans le fichier"""
        try:
            config = {
                'youtube_api_key': self.api_key,
                'download_path': self.download_path,
                'concurrent_downloads_limit': self.concurrent_downloads_limit # Sauvegarder la nouvelle option
            }
            with open(self.config_path, "w", encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            
    def set_api_key(self, api_key: str):
        """Définir la clé API"""
        self.api_key = api_key
        self.save_config() # Sauvegarder immédiatement après modification

    def get_api_key(self) -> str:
        """Obtenir la clé API"""
        return self.api_key

    def set_download_path(self, path: str):
        """Définir le chemin de téléchargement"""
        self.download_path = path
        self.save_config() # Sauvegarder immédiatement après modification

    def get_download_path(self) -> str:
        """Obtenir le chemin de téléchargement"""
        return self.download_path

    def set_concurrent_downloads_limit(self, limit: int):
        """Définir la limite de téléchargements simultanés"""
        if 1 <= limit <= 15: # S'assurer que la limite est dans les bornes
            self.concurrent_downloads_limit = limit
            self.save_config()
        else:
            print(f"Avertissement: La limite de téléchargements simultanés doit être entre 1 et 15. Valeur fournie: {limit}")

    def get_concurrent_downloads_limit(self) -> int:
        """Obtenir la limite de téléchargements simultanés"""
        return self.concurrent_downloads_limit

