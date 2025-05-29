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
        self.yt_dlp_path = None
        self.ffmpeg_path = None

    def log(self, message: str):
        self.log_callback(message)

    def set_download_path(self, path: str):
        self.download_path = path

    def _run_command_check(self, command: list) -> bool:
        """Exécute une commande pour vérifier si un exécutable est disponible."""
        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            subprocess.run(command, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, creationflags=creationflags)
            return True
        except FileNotFoundError:
            return False
        except subprocess.CalledProcessError:
            return True # La commande a échoué mais le programme existe
        except Exception as e:
            self.log(f"Erreur inattendue lors de la vérification de la commande {command}: {e}")
            return False

    def find_yt_dlp_location(self) -> str:
        """
        Trouve le chemin de l'exécutable yt-dlp.
        Cherche dans le dossier courant, puis dans le PATH.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        exec_name = "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp"

        # 1. Vérifier le dossier de l'exécutable (ou le dossier du script si c'est un script)
        candidate_path = os.path.join(script_dir, exec_name)
        if os.path.exists(candidate_path) and self._run_command_check([candidate_path, "--version"]):
            self.yt_dlp_path = candidate_path
            self.log(f"yt-dlp trouvé à: {self.yt_dlp_path}")
            return candidate_path

        # 2. Chercher dans le PATH système
        try:
            path_env = os.environ.get("PATH", "").split(os.pathsep)
            for path_dir in path_env:
                full_path = os.path.join(path_dir, exec_name)
                if os.path.exists(full_path) and self._run_command_check([full_path, "--version"]):
                    self.yt_dlp_path = full_path
                    self.log(f"yt-dlp trouvé dans le PATH: {self.yt_dlp_path}")
                    return full_path
        except Exception as e:
            self.log(f"Erreur lors de la recherche de yt-dlp dans le PATH: {e}")

        self.log("yt-dlp n'a pas été trouvé. Assurez-vous qu'il est dans le même dossier que l'exécutable ou dans votre PATH.")
        self.yt_dlp_path = None
        return ""

    def find_ffmpeg_location(self) -> str:
        """
        Trouve le chemin de l'exécutable ffmpeg.
        Cherche d'abord dans le dossier spécifié './ffmpeg/bin/', puis le dossier courant, puis le PATH.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        exec_name = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"

        # 1. Vérifier le chemin spécifique ./ffmpeg/bin/
        ffmpeg_bin_path = os.path.join(script_dir, "ffmpeg", "bin", exec_name)
        if os.path.exists(ffmpeg_bin_path) and self._run_command_check([ffmpeg_bin_path, "-version"]):
            self.ffmpeg_path = ffmpeg_bin_path
            self.log(f"ffmpeg trouvé à l'emplacement spécifié: {self.ffmpeg_path}")
            return ffmpeg_bin_path

        # 2. Vérifier le dossier de l'exécutable (ou le dossier du script si c'est un script)
        candidate_path = os.path.join(script_dir, exec_name)
        if os.path.exists(candidate_path) and self._run_command_check([candidate_path, "-version"]):
            self.ffmpeg_path = candidate_path
            self.log(f"ffmpeg trouvé à: {self.ffmpeg_path}")
            return candidate_path

        # 3. Chercher dans le PATH système (en dernier recours)
        try:
            path_env = os.environ.get("PATH", "").split(os.pathsep)
            for path_dir in path_env:
                full_path = os.path.join(path_dir, exec_name)
                if os.path.exists(full_path) and self._run_command_check([full_path, "-version"]):
                    self.ffmpeg_path = full_path
                    self.log(f"ffmpeg trouvé dans le PATH: {self.ffmpeg_path}")
                    return full_path
        except Exception as e:
            self.log(f"Erreur lors de la recherche de ffmpeg dans le PATH: {e}")

        self.log("ffmpeg n'a pas été trouvé. Assurez-vous qu'il est dans './ffmpeg/bin/', le même dossier que l'exécutable ou dans votre PATH. Il est nécessaire pour convertir en MP3/WAV.")
        self.ffmpeg_path = None
        return ""

    def _download_single_item(self, url: str, selected_format: str) -> bool:
        """
        Télécharger un seul élément (vidéo ou playlist).
        """
        try:
            if not self.yt_dlp_path:
                self.log("yt-dlp n'est pas configuré. Impossible de télécharger.")
                return False

            if not self.download_path or not os.path.isdir(self.download_path):
                self.log(f"Erreur: Le dossier de téléchargement '{self.download_path}' n'est pas valide.")
                return False

            # Déterminer les arguments yt-dlp
            yt_dlp_args = [
                self.yt_dlp_path,
                "-P", self.download_path,
                # Utilisez self.ffmpeg_path si trouvé, sinon laissez yt-dlp chercher "ffmpeg" dans le PATH
                "--ffmpeg-location", self.ffmpeg_path if self.ffmpeg_path else "ffmpeg",
                url
            ]

            if selected_format == "mp3":
                yt_dlp_args.extend(["-x", "--audio-format", "mp3"])
            elif selected_format == "mp4":
                yt_dlp_args.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"])
            elif selected_format == "wav":
                yt_dlp_args.extend(["-x", "--audio-format", "wav"])

            # Options pour masquer la fenêtre de console sur Windows
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            self.log(f"Lancement du téléchargement pour: {url}...")

            process = subprocess.run(
                yt_dlp_args,
                check=True,
                capture_output=True,  # Capture stdout et stderr
                text=True,            # Traiter la sortie comme du texte
                creationflags=creationflags # Appliquer les drapeaux de création
            )

            # Log la sortie de yt-dlp pour le débogage si nécessaire
            if process.stdout:
                for line in process.stdout.splitlines():
                    if line.strip(): # Éviter les lignes vides
                        self.log(f"yt-dlp: {line}")
            if process.stderr:
                for line in process.stderr.splitlines():
                    if line.strip():
                        self.log(f"yt-dlp Erreur: {line}")

            self.log(f"Téléchargement terminé pour {url}.")
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"Échec du téléchargement pour {url}: {e}")
            self.log(f"Sortie standard: {e.stdout}")
            self.log(f"Erreur standard: {e.stderr}")
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
                
                success = self._download_single_item(url, selected_format)

                if success:
                    success_count += 1
                else:
                    self.log(f"Échec du traitement pour: {url}")
            callback(success_count, total_count)

        download_thread = threading.Thread(target=_download_task)
        download_thread.start()