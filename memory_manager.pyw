import json
import os
from typing import List, Dict

class MemoryManager:
    def __init__(self, memory_path: str = "C:/MesScripts/links.txt"):
        self.memory_path = memory_path
        self.memory_data = []
        self.load_memory()
        
    def load_memory(self) -> List[Dict]:
        """Charger la mémoire depuis le fichier"""
        try:
            with open(self.memory_path, "r", encoding='utf-8') as f:
                self.memory_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memory_data = []
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        return self.memory_data
        
    def save_memory(self):
        """Sauvegarder la mémoire dans le fichier"""
        try:
            with open(self.memory_path, "w", encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            
    def add_item(self, title: str, url: str, duration: str) -> bool:
        """Ajouter un élément à la mémoire"""
        try:
            item = {
                "title": title,
                "url": url,
                "duration": duration
            }
            self.memory_data.append(item)
            self.save_memory()
            return True
        except Exception as e:
            print(f"Erreur lors de l'ajout: {e}")
            return False
            
    def remove_item(self, index: int) -> bool:
        """Supprimer un élément de la mémoire"""
        try:
            if 0 <= index < len(self.memory_data):
                del self.memory_data[index]
                self.save_memory()
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
            
    def get_memory(self) -> List[Dict]:
        """Obtenir toute la mémoire"""
        return self.memory_data
        
    def clear_memory(self):
        """Vider la mémoire"""
        self.memory_data = []
        self.save_memory()
        
    def get_item(self, index: int) -> Dict:
        """Obtenir un élément spécifique"""
        if 0 <= index < len(self.memory_data):
            return self.memory_data[index]
        return None
        
    def get_urls(self) -> List[str]:
        """Obtenir toutes les URLs de la mémoire"""
        return [item['url'] for item in self.memory_data]
        
    def size(self) -> int:
        """Obtenir la taille de la mémoire"""
        return len(self.memory_data)