import re
from typing import List, Dict, Optional

# Vérification et import de l'API Google
try:
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("[!] google-api-python-client n'est pas installé.")

class YouTubeAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.youtube = None
        
        if GOOGLE_API_AVAILABLE and self.api_key:
            try:
                self.youtube = build("youtube", "v3", developerKey=self.api_key)
            except Exception as e:
                print(f"Erreur lors de l'initialisation de l'API YouTube: {e}")
                self.youtube = None
                
    def is_available(self) -> bool:
        """Vérifier si l'API est disponible et configurée"""
        return GOOGLE_API_AVAILABLE and self.youtube is not None
        
    def set_api_key(self, api_key: str):
        """Définir une nouvelle clé API"""
        self.api_key = api_key
        if GOOGLE_API_AVAILABLE and self.api_key:
            try:
                self.youtube = build("youtube", "v3", developerKey=self.api_key)
            except Exception as e:
                print(f"Erreur avec la clé API: {e}")
                self.youtube = None
                
    def search_videos(self, query: str, max_results: int = 30) -> List[Dict]:
        """Rechercher des vidéos sur YouTube"""
        if not self.is_available():
            raise Exception("API YouTube non disponible ou non configurée")
            
        try:
            # Recherche des vidéos
            search_request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results
            )
            search_response = search_request.execute()

            results = []
            video_ids = []

            # Collecter les IDs des vidéos
            for item in search_response.get('items', []):
                video_id = item.get('id', {}).get('videoId')
                if video_id:
                    video_ids.append(video_id)

            if not video_ids:
                return results

            # Obtenir les détails des vidéos (durée)
            details_request = self.youtube.videos().list(
                part="contentDetails",
                id=",".join(video_ids)
            )
            details_response = details_request.execute()

            # Créer un dictionnaire des durées
            durations = {}
            for item in details_response.get('items', []):
                video_id = item['id']
                duration = item['contentDetails']['duration']
                durations[video_id] = duration

            # Construire les résultats finaux
            for i, item in enumerate(search_response.get('items', [])):
                video_id = item.get('id', {}).get('videoId')
                if not video_id:
                    continue
                    
                title = item['snippet']['title']
                url = f"https://www.youtube.com/watch?v={video_id}"
                duration = durations.get(video_id, "PT0S")

                result = {
                    "id": i + 1,
                    "title": title,
                    "url": url,
                    "duration": self.parse_duration(duration)
                }
                results.append(result)
                
            return results
            
        except Exception as e:
            raise Exception(f"Erreur lors de la recherche: {e}")
            
    def parse_duration(self, duration: str) -> str:
        """Parser la durée YouTube en format HH:MM:SS"""
        if not duration:
            return "00:00:00"

        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return "00:00:00"

        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0

        return f"{hours:02}:{minutes:02}:{seconds:02}"