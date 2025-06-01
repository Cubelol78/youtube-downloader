# downloader.py
import os
import sys
import subprocess
import threading
from typing import Callable, Optional, Dict
import re # Importation pour les expressions régulières

class Downloader:
    def __init__(self, download_path: str, log_callback: Optional[Callable] = None, progress_callback: Optional[Callable] = None):
        self.download_path = download_path
        self.log_callback = log_callback or print
        self.progress_callback = progress_callback # Nouveau callback pour la progression
        self.yt_dlp_path = None
        self.ffmpeg_path = None
        self.active_processes: Dict[str, subprocess.Popen] = {} # Pour suivre les processus actifs et les annuler

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

    def _download_single_item(self, url: str, selected_format: str, download_id: str) -> bool:
        """
        Télécharger un seul élément (vidéo ou playlist).
        """
        try:
            if not self.yt_dlp_path:
                self.log("yt-dlp n'est pas configuré. Impossible de télécharger.")
                if self.progress_callback:
                    self.progress_callback(download_id, "failed", 0, "yt-dlp non configuré")
                return False

            if not self.download_path or not os.path.isdir(self.download_path):
                self.log(f"Erreur: Le dossier de téléchargement '{self.download_path}' n'est pas valide.")
                if self.progress_callback:
                    self.progress_callback(download_id, "failed", 0, "Dossier de téléchargement invalide")
                return False

            # Déterminer les arguments yt-dlp
            yt_dlp_args = [
                self.yt_dlp_path,
                "-P", self.download_path,
                "--ffmpeg-location", self.ffmpeg_path if self.ffmpeg_path else "ffmpeg",
                "--progress", # Activer la sortie de progression
                "--newline",  # Assurer que chaque ligne de progression est sur une nouvelle ligne
                url
            ]

            if selected_format == "mp3":
                yt_dlp_args.extend(["-x", "--audio-format", "mp3"])
            elif selected_format == "mp4":
                yt_dlp_args.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"])
            elif selected_format == "wav":
                yt_dlp_args.extend(["-x", "--audio-format", "wav"])
            elif selected_format == "flac":
                yt_dlp_args.extend(["-x", "--audio-format", "flac"])
            elif selected_format == "webm":
                yt_dlp_args.extend(["-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best"])
            elif selected_format == "mkv":
                yt_dlp_args.extend(["-f", "bestvideo[ext=mkv]+bestaudio[ext=mka]/best[ext=mkv]/best"])
            elif selected_format == "m4a":
                yt_dlp_args.extend(["-x", "--audio-format", "m4a"])
            elif selected_format == "opus":
                yt_dlp_args.extend(["-x", "--audio-format", "opus"])
            elif selected_format == "mov":
                yt_dlp_args.extend(["-f", "bestvideo[ext=mov]+bestaudio[ext=mov]/best[ext=mov]/best"])
            elif selected_format == "avi":
                yt_dlp_args.extend(["-f", "bestvideo[ext=avi]+bestaudio[ext=avi]/best[ext=avi]/best"])

            # Options pour masquer la fenêtre de console sur Windows
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            self.log(f"Lancement du téléchargement pour: {url}...")
            if self.progress_callback:
                self.progress_callback(download_id, "active", 0, "Démarrage...")

            process = subprocess.Popen(
                yt_dlp_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creationflags,
                bufsize=1 # Ligne par ligne
            )
            self.active_processes[download_id] = process

            # Lire la sortie en temps réel pour la progression
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_stripped = output.strip()
                    self.log(f"[RAW YT-DLP] {output_stripped}") # Log la sortie brute avec un préfixe distinct

                    # Tenter de parser la progression
                    progress_percent = -1.0 # Valeur par défaut pour indiquer pas de progression trouvée
                    current_status_message = output_stripped

                    if "[download]" in output_stripped:
                        percent_match = re.search(r'(\d+\.?\d*)%', output_stripped) # Capture des entiers ou décimaux
                        if percent_match:
                            try:
                                progress_percent = float(percent_match.group(1))
                                current_status_message = output_stripped # Utiliser la ligne complète comme message
                            except ValueError:
                                pass # Ignorer les erreurs de parsing, garder le message brut
                        elif "ETA" not in output_stripped: # Si pas de pourcentage et pas d'ETA, c'est peut-être une étape intermédiaire
                            if "Downloading item" in output_stripped:
                                current_status_message = "Téléchargement d'élément..."
                            elif "has already been downloaded" in output_stripped:
                                current_status_message = "Déjà téléchargé"
                                progress_percent = 100.0 # Marquer comme 100% si déjà téléchargé
                            else:
                                current_status_message = output_stripped # Message brut si non reconnu
                    elif "[ExtractAudio]" in output_stripped:
                        current_status_message = "Extraction audio..."
                        progress_percent = 90.0 # Estimer la progression pour l'extraction
                    elif "[ffmpeg]" in output_stripped:
                        current_status_message = "Conversion/Multiplexage..."
                        progress_percent = 95.0 # Estimer la progression pour ffmpeg
                    
                    # Si une progression a été trouvée ou estimée, mettre à jour le callback
                    if self.progress_callback:
                        status_to_report = "active"
                        if progress_percent >= 100.0:
                            status_to_report = "completed" # Marquer comme terminé si 100%
                        elif progress_percent == -1.0: # Si pas de pourcentage détecté, mais toujours actif
                            status_to_report = "En cours..."
                            progress_percent = 0 # Garder 0% si pas de progression spécifique

                        self.progress_callback(download_id, status_to_report, max(0.0, progress_percent), current_status_message)

            stderr_output = process.stderr.read()
            if stderr_output:
                for line in stderr_output.splitlines():
                    if line.strip():
                        self.log(f"yt-dlp Erreur: {line}")

            process.wait() # Attendre la fin du processus
            
            # Supprimer le processus de la liste des actifs après qu'il soit terminé
            if download_id in self.active_processes:
                del self.active_processes[download_id] 

            if process.returncode == 0:
                self.log(f"Téléchargement terminé pour {url}.")
                if self.progress_callback:
                    self.progress_callback(download_id, "completed", 100, "Terminé")
                return True
            else:
                self.log(f"Échec du téléchargement pour {url}. Code de retour: {process.returncode}")
                if self.progress_callback:
                    self.progress_callback(download_id, "failed", 0, f"Échec (Code: {process.returncode})")
                return False

        except FileNotFoundError:
            self.log(f"Erreur: Le programme '{self.yt_dlp_path}' ou 'ffmpeg' n'a pas été trouvé. Vérifiez votre installation et votre PATH.")
            if self.progress_callback:
                self.progress_callback(download_id, "failed", 0, "yt-dlp/ffmpeg non trouvé")
            return False
        except Exception as e:
            self.log(f"Une erreur inattendue est survenue lors du téléchargement de {url}: {e}")
            if self.progress_callback:
                self.progress_callback(download_id, "failed", 0, f"Erreur inattendue: {e}")
            return False

    # La méthode download_items_in_bulk n'est plus utilisée directement par main_gui.py
    # Elle est remplacée par la gestion de la queue dans main_gui.py
    # Je la laisse ici au cas où elle serait appelée dans d'autres contextes, mais elle n'est plus le point d'entrée pour les téléchargements multiples.
    def download_items_in_bulk(self, urls: list[str], selected_format: str, callback: Callable[[int, int], None], download_ids: list[str]):
        """
        Télécharger plusieurs éléments de manière asynchrone.
        Cette méthode est maintenant dépréciée pour l'usage direct par MusicDLGUI,
        la gestion des téléchargements multiples se fait via la file d'attente.
        """
        self.log("Attention: download_items_in_bulk est appelée directement. La gestion des téléchargements parallèles est maintenant gérée par la file d'attente de l'interface graphique.")
        def _download_task_deprecated():
            success_count = 0
            total_count = len(urls)

            for i, url in enumerate(urls):
                download_id = download_ids[i]
                self.log(f"Traitement {i+1}/{total_count}: {url} en {selected_format}...")
                
                success = self._download_single_item(url, selected_format, download_id)

                if success:
                    success_count += 1
                else:
                    self.log(f"Échec du traitement pour: {url}")
            callback(success_count, total_count)

        download_thread = threading.Thread(target=_download_task_deprecated)
        download_thread.start()

    def cancel_download(self, download_id: str):
        """Tente d'annuler un téléchargement en cours."""
        if download_id in self.active_processes:
            process = self.active_processes[download_id]
            try:
                process.terminate() # Tente d'arrêter le processus en douceur
                self.log(f"Tentative d'annulation du téléchargement {download_id}.")
                if self.progress_callback:
                    self.progress_callback(download_id, "cancelled", 0, "Annulé")
                # Optionnel: attendre un court instant et tuer si non terminé
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill() # Tuer le processus si terminate ne fonctionne pas
                self.log(f"Processus de téléchargement {download_id} tué (forcé).")
                if self.progress_callback:
                    self.progress_callback(download_id, "cancelled", 0, "Annulé (forcé)")
            except Exception as e:
                self.log(f"Erreur lors de l'annulation du téléchargement {download_id}: {e}")
                if self.progress_callback:
                    self.progress_callback(download_id, "failed", 0, "Erreur d'annulation")
            finally:
                if download_id in self.active_processes:
                    del self.active_processes[download_id]
        else:
            self.log(f"Aucun téléchargement actif trouvé pour l'ID: {download_id}")

