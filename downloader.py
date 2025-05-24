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

    def download_audio(self, url: str) -> bool:
        """Télécharger l'audio d'une vidéo YouTube."""
        if not self.yt_dlp_path:
            self.log("yt-dlp n'est pas configuré. Impossible de télécharger.")
            return False

        self.log(f"Téléchargement audio de: {url} vers {self.download_path}")
        try:
            # Commande de base pour le téléchargement audio
            cmd = [
                self.yt_dlp_path,
                "-x", # Extraire l'audio
                "--audio-format", "mp3", # Convertir en mp3
                "--audio-quality", "0", # Meilleure qualité audio
                "--no-playlist", # Ne pas télécharger de playlist
                "--no-mtime", # Ne pas modifier la date de modification du fichier
                "--no-write-thumbnail", # Ne pas écrire de miniature
                "--no-write-sub", # Ne pas écrire de sous-titres
                "--no-write-info-json", # Ne pas écrire de fichier info JSON
                "--no-check-certificate", # Ignorer la vérification du certificat SSL
                "--prefer-free-formats", # Préférer les formats gratuits (ex: webm)
                "-o", os.path.join(self.download_path, "%(title)s.%(ext)s"), # Chemin de sortie
                url
            ]

            # Si un chemin FFmpeg spécifique est trouvé, l'ajouter à la commande
            if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg":
                cmd.insert(1, "--ffmpeg-location")
                cmd.insert(2, self.ffmpeg_path)

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, encoding='utf-8', errors='replace',
                                     cwd=self.download_path)

            for line in process.stdout:
                if line.strip():
                    self.log(line.strip())

            process.wait()
            return process.returncode == 0

        except Exception as e:
            self.log(f"Erreur lors du téléchargement audio: {e}")
            return False

    def download_video(self, url: str) -> bool:
        """Télécharger une vidéo YouTube."""
        if not self.yt_dlp_path:
            self.log("yt-dlp n'est pas configuré. Impossible de télécharger.")
            return False

        self.log(f"Téléchargement vidéo de: {url} vers {self.download_path}")
        try:
            cmd = [
                self.yt_dlp_path,
                "--format", "bestvideo+bestaudio/best", # Meilleure qualité vidéo et audio
                "--merge-output-format", "mp4", # Fusionner en mp4
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
            if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg":
                cmd.insert(1, "--ffmpeg-location")
                cmd.insert(2, self.ffmpeg_path)

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, encoding='utf-8', errors='replace',
                                     cwd=self.download_path)

            for line in process.stdout:
                if line.strip():
                    self.log(line.strip())

            process.wait()
            return process.returncode == 0

        except Exception as e:
            self.log(f"Erreur: {e}")
            return False

    def download_items_in_bulk(self, urls: list[str], is_audio_only: bool, callback: Callable[[int, int], None]):
        """Télécharger plusieurs éléments de manière asynchrone."""
        def _download_task():
            success_count = 0
            total_count = len(urls)
            for i, url in enumerate(urls):
                self.log(f"Début du téléchargement {i+1}/{total_count}: {url}")
                if is_audio_only:
                    success = self.download_audio(url)
                else:
                    success = self.download_video(url)

                if success:
                    success_count += 1
                else:
                    self.log(f"Échec du téléchargement pour: {url}")
            callback(success_count, total_count)

        threading.Thread(target=_download_task).start()