# downloader.py
import os
import sys
import subprocess
import threading
from typing import Callable, Optional

class Downloader:
    def __init__(self, download_path: str, log_callback: Optional[Callable] = None):
        self.download_path = download_path
        self.log_callback = log_callback or print
        self.yt_dlp_path = None # Initialisé à None, sera trouvé par _find_yt_dlp()
        self.ffmpeg_path = None # Initialisé à None, sera trouvé par _find_ffmpeg_location()

        # Ces méthodes doivent être appelées après l'initialisation complète de l'objet
        # Pour s'assurer que self.log est disponible.
        # Elles seront appelées par main_gui après l'initialisation.

    def log(self, message: str):
        """Enregistrer un message de log"""
        self.log_callback(message)

    def set_download_path(self, path: str):
        """Définir le chemin de téléchargement"""
        self.download_path = path

    def _run_command_check(self, command: list) -> bool:
        """Exécute une commande pour vérifier si un exécutable est disponible."""
        try:
            # Utilisez stdout=subprocess.PIPE pour ne pas imprimer la sortie à la console directement
            subprocess.run(command, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_yt_dlp_installed(self) -> bool:
        """Vérifier si yt-dlp est installé et disponible"""
        self.log("Vérification de yt-dlp...")
        # Vérifier si yt-dlp est dans le PATH
        if self._run_command_check(["yt-dlp", "--version"]):
            self.yt_dlp_path = "yt-dlp"
            self.log("yt-dlp trouvé dans le PATH.")
            return True

        # Vérifier si yt-dlp est dans le même répertoire que le script principal
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        local_yt_dlp_path = os.path.join(base_path, "yt-dlp")
        if sys.platform == "win32":
            local_yt_dlp_path += ".exe"

        if os.path.exists(local_yt_dlp_path) and self._run_command_check([local_yt_dlp_path, "--version"]):
            self.yt_dlp_path = local_yt_dlp_path
            self.log(f"yt-dlp trouvé localement: {self.yt_dlp_path}")
            return True

        self.log("yt-dlp non trouvé.")
        self.yt_dlp_path = None
        return False

    def _find_ffmpeg_location(self) -> Optional[str]:
        """Tente de trouver l'emplacement de FFmpeg."""
        self.log("Recherche de FFmpeg...")

        # 1. Vérifier si FFmpeg est dans le PATH système
        if self._run_command_check(["ffmpeg", "-version"]):
            self.log("FFmpeg trouvé dans le PATH système.")
            return "ffmpeg" # yt-dlp le trouvera si il est dans le PATH

        # 2. Vérifier dans le répertoire relatif "./ffmpeg/bin"
        # sys._MEIPASS est utilisé quand l'application est packagée avec PyInstaller
        # os.path.dirname(os.path.abspath(__file__)) est pour le mode de développement
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        ffmpeg_bin_path = os.path.join(base_path, "ffmpeg", "bin")
        ffmpeg_executable = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
        full_ffmpeg_path = os.path.join(ffmpeg_bin_path, ffmpeg_executable)

        if os.path.exists(full_ffmpeg_path) and self._run_command_check([full_ffmpeg_path, "-version"]):
            self.log(f"FFmpeg trouvé localement à: {full_ffmpeg_path}")
            return full_ffmpeg_path

        self.log("FFmpeg non trouvé.")
        return None

    def check_ffmpeg_installed(self) -> bool:
        """Vérifie et définit le chemin de FFmpeg."""
        found_path = self._find_ffmpeg_location()
        if found_path:
            self.ffmpeg_path = found_path
            return True
        self.ffmpeg_path = None
        return False

    def _download_single_item(self, url: str, target_format: str) -> bool:
        """
        Télécharge une URL unique avec yt-dlp et la convertit si nécessaire
        vers le format spécifié.
        """
        if not self.yt_dlp_path:
            self.log("Erreur: yt-dlp n'est pas installé ou introuvable.")
            return False

        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path, exist_ok=True)

        # Commande de base
        cmd = [
            self.yt_dlp_path,
            "--no-playlist",
            "--no-mtime",
            "--no-write-thumbnail",
            "--no-write-sub",
            "--no-write-info-json",
            "--no-check-certificate",
            "--prefer-free-formats",
            "-o", os.path.join(self.download_path, "%(title)s.%(ext)s"),
            url
        ]

        # Logique de formatage avec yt-dlp
        audio_formats = ["MP3", "WAV", "FLAC", "AAC", "OGG"]
        video_formats = ["MP4", "WEBM", "MKV"]

        if target_format.upper() in audio_formats:
            if not self.ffmpeg_path:
                self.log(f"Erreur: FFmpeg est nécessaire pour la conversion en {target_format} et n'est pas trouvé.")
                return False
            cmd.extend(['-x']) # Activer l'extraction audio

            if target_format.upper() == "MP3":
                cmd.extend(['--audio-format', 'mp3', '--audio-quality', '0'])
            elif target_format.upper() == "WAV":
                cmd.extend(['--audio-format', 'wav'])
            elif target_format.upper() == "FLAC":
                cmd.extend(['--audio-format', 'flac'])
            elif target_format.upper() == "AAC":
                # yt-dlp tends to use m4a for AAC. This is correct.
                cmd.extend(['--audio-format', 'aac'])
            elif target_format.upper() == "OGG":
                # For OGG, yt-dlp usually prefers 'opus' or 'vorbis'
                # or you can set a post-processor to convert to ogg after extraction.
                # A common approach is to extract as best audio and then convert.
                # Or, tell yt-dlp to output to 'opus' which commonly goes into .ogg
                cmd.extend(['--audio-format', 'opus']) # yt-dlp will often put Opus in an OGG container
                self.log("Tentative de téléchargement OGG avec le codec Opus. Le fichier aura probablement une extension .ogg.")
        elif target_format.upper() == "MP4":
            cmd.extend(['-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '--merge-output-format', 'mp4'])
        elif target_format.upper() == "WEBM":
            cmd.extend(['-f', 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best', '--merge-output-format', 'webm'])
        elif target_format.upper() == "MKV":
            cmd.extend(['-f', 'bestvideo+bestaudio/best', '--merge-output-format', 'mkv'])
        else:
            self.log(f"Format de téléchargement '{target_format}' non pris en charge directement par le script. Téléchargement du format par défaut de yt-dlp.")
            # Laisser yt-dlp choisir le meilleur format par défaut si non spécifié

        # Si un chemin FFmpeg spécifique est trouvé (et n'est pas juste "ffmpeg"), l'ajouter à la commande
        if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg":
            cmd.insert(1, "--ffmpeg-location")
            cmd.insert(2, self.ffmpeg_path)

        self.log(f"Début du téléchargement en {target_format} pour: {url}")
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding='utf-8', errors='replace',
                                    cwd=self.download_path)

            for line in process.stdout:
                if line.strip():
                    self.log(line.strip())

            process.wait()

            if process.returncode == 0:
                self.log(f"Téléchargement et conversion en {target_format} réussis pour: {url}")
                return True
            else:
                self.log(f"Échec du téléchargement ou de la conversion en {target_format} pour {url}. Code d'erreur: {process.returncode}")
                return False

        except FileNotFoundError:
            self.log(f"Erreur: Le programme '{self.yt_dlp_path}' ou 'ffmpeg' n'a pas été trouvé. Vérifiez votre installation et votre PATH.")
            return False
        except Exception as e:
            self.log(f"Une erreur inattendue est survenue lors du téléchargement de {url}: {e}")
            return False

    def download_items_in_bulk(self, urls: list[str], selected_format: str, callback: Callable[[int, int], None]):
        """
        Télécharger plusieurs éléments de manière asynchrone, en utilisant le format spécifié.
        Gère aussi les playlists YouTube.
        """
        def _download_task():
            success_count = 0
            total_count = len(urls)

            for i, url in enumerate(urls):
                self.log(f"Traitement {i+1}/{total_count}: {url} en {selected_format}...")
                
                # yt-dlp gère les playlists directement, il n'est donc pas nécessaire
                # de boucler sur les vidéos d'une playlist côté Python.
                # Il suffit de passer l'URL de la playlist à _download_single_item.
                success = self._download_single_item(url, selected_format)

                if success:
                    success_count += 1
                else:
                    self.log(f"Échec du traitement pour: {url}")
            callback(success_count, total_count)

        threading.Thread(target=_download_task).start()