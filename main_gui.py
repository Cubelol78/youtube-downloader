# main_gui.py
import os
import sys
import glob
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import webbrowser # Pour ouvrir le lien de téléchargement

from config_manager import ConfigManager
from youtube_api import YouTubeAPI, GOOGLE_API_AVAILABLE
from downloader import Downloader
from memory_manager import MemoryManager
from dialogs import APIKeyDialog
# Pas besoin d'importer styles et gui_elements ici si vous les avez déjà en fichiers séparés et importez comme ci-dessous
# from styles import apply_styles # Pas besoin d'importer styles ici car c'est déjà appliqué dans le fichier styles.py
# import gui_elements # Pas besoin d'importer gui_elements ici car les fonctions sont appelées directement

class MusicDLGUI:
    def __init__(self):
        # Initialiser les gestionnaires
        self.config = ConfigManager()
        self.log_display = None
        self.youtube_api = YouTubeAPI(self.config.api_key)
        # Le downloader a besoin d'une fonction de log, qu'il va trouver via self.log après setup_gui
        # On passe None initialement, et on s'assurera que self.log_display est prêt avant l'appel à downloader.log
        self.downloader = Downloader(self.config.download_path, self.log)
        self.memory = MemoryManager()

        # Données temporaires pour les recherches
        self.search_results = []

        # NOTE IMPORTANTE : self.download_format_var sera initialisé dans setup_gui, après tk.Tk()
        self.download_format_var = None # Initialiser à None ici

        self.setup_gui() # setup_gui va créer self.root et self.download_format_var

        # Vérifications initiales après le démarrage de l'interface graphique
        self.root.after(100, self.check_and_offer_yt_dlp_install)
        self.root.after(200, self.check_and_offer_ffmpeg_install)
        self.root.after(300, self.check_google_api_client)

    def setup_gui(self):
        # Fenêtre principale
        self.root = tk.Tk()
        self.root.title("MusicDL - Téléchargeur de Musique YouTube")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b') # Fond de la fenêtre principale

        # Initialisation de la variable Tkinter après la création de self.root
        self.download_format_var = tk.StringVar(value="MP4") # Valeur par défaut

        # --- Styles pour les widgets TTK ---
        style = ttk.Style()
        style.theme_use('clam') # Thème de base

        # Couleurs de base pour le thème sombre
        BG_DARK = '#2b2b2b' # Fond principal
        BG_MEDIUM = '#3c3c3c' # Fond des cadres intérieurs, éléments de surface
        BG_LIGHT = '#4c4c4c' # Fond des entrées, zones de log
        FG_PRIMARY = 'white' # Couleur du texte principal
        FG_SECONDARY = '#cccccc' # Couleur du texte secondaire/labels
        ACCENT_COLOR = '#007bff' # Bleu pour les boutons d'action (ex: télécharger)
        DANGER_COLOR = '#dc3545' # Rouge pour les actions destructives (ex: supprimer)
        HOVER_COLOR = '#5a87b3' # Bleu clair pour le survol
        BUTTON_BG = '#404040' # Fond des boutons standards
        BUTTON_ACTIVE_BG = '#505050' # Fond des boutons au survol

        # Styles pour les Frames
        style.configure('Custom.TFrame', background=BG_DARK)
        style.configure('Custom.TLabelframe', background=BG_MEDIUM, foreground=FG_PRIMARY,
                        relief='flat', borderwidth=2)
        style.configure('Custom.TLabelframe.Label', background=BG_MEDIUM, foreground=FG_PRIMARY,
                        font=('Arial', 11, 'bold'))

        # Styles pour les Labels
        style.configure('Custom.TLabel', background=BG_DARK, foreground=FG_PRIMARY, font=('Arial', 10))
        style.configure('Heading.TLabel', background=BG_DARK, foreground=FG_PRIMARY, font=('Arial', 12, 'bold'))


        # Styles pour les Boutons
        style.configure('Custom.TButton',
                        background=BUTTON_BG, foreground=FG_PRIMARY, font=('Arial', 10),
                        relief='flat', borderwidth=0, padding=(8, 4))
        style.map('Custom.TButton',
                  background=[('active', BUTTON_ACTIVE_BG)],
                  foreground=[('active', FG_PRIMARY)])

        # Boutons d'action (Télécharger)
        style.configure('Accent.TButton',
                        background=ACCENT_COLOR, foreground='white', font=('Arial', 10, 'bold'),
                        relief='flat', borderwidth=0, padding=(8, 4))
        style.map('Accent.TButton',
                  background=[('active', HOVER_COLOR)])

        # Boutons de suppression (Danger)
        style.configure('Danger.TButton',
                        background=DANGER_COLOR, foreground='white', font=('Arial', 10),
                        relief='flat', borderwidth=0, padding=(8, 4))
        style.map('Danger.TButton',
                  background=[('active', '#e65c69')]) # Rouge un peu plus clair au survol


        # Styles pour les Entry (champs de texte)
        style.configure('TEntry', fieldbackground=BG_LIGHT, foreground=FG_PRIMARY,
                        insertbackground=FG_PRIMARY, borderwidth=1, relief='flat', padding=5)

        # Styles pour les Combobox
        style.configure('TCombobox',
                        fieldbackground=BG_LIGHT, background=BUTTON_BG,
                        foreground=FG_PRIMARY, selectbackground=ACCENT_COLOR,
                        selectforeground='white', borderwidth=1, relief='flat')
        style.map('TCombobox',
                  fieldbackground=[('readonly', BG_LIGHT)],
                  selectbackground=[('readonly', ACCENT_COLOR)],
                  selectforeground=[('readonly', 'white')],
                  background=[('active', BUTTON_ACTIVE_BG)]) # Fond de la liste déroulante au survol

        # Styles pour les Treeview
        style.configure('Treeview',
                        background=BG_LIGHT, foreground=FG_PRIMARY,
                        fieldbackground=BG_LIGHT, borderwidth=0, relief='flat',
                        rowheight=25) # Hauteur des lignes
        style.map('Treeview',
                  background=[('selected', ACCENT_COLOR)], # Couleur de sélection
                  foreground=[('selected', 'white')])

        style.configure('Treeview.Heading',
                        background=BG_MEDIUM, foreground=FG_PRIMARY,
                        font=('Arial', 10, 'bold'), relief='flat', padding=(5, 5))
        style.map('Treeview.Heading',
                  background=[('active', BUTTON_ACTIVE_BG)])

        # Styles pour les Scrollbars
        style.configure('Vertical.TScrollbar',
                        background=BG_MEDIUM, troughcolor=BG_DARK,
                        bordercolor=BG_DARK, arrowcolor=FG_PRIMARY,
                        relief='flat', borderwidth=0)
        style.map('Vertical.TScrollbar',
                  background=[('active', ACCENT_COLOR)])

        # --- Layout principal ---
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=BG_DARK, bd=0, relief='flat')
        main_pane.pack(fill='both', expand=True, padx=10, pady=10)

        # Panneau gauche (Recherche YouTube)
        left_frame = ttk.Frame(main_pane, style='Custom.TFrame')
        main_pane.add(left_frame, width=450, minsize=350) # minsize pour redimensionnement

        # Panneau droit (Téléchargement et Logs)
        right_frame = ttk.Frame(main_pane, style='Custom.TFrame')
        main_pane.add(right_frame, minsize=350)

        # --- Composants du panneau gauche ---
        # Section Recherche
        search_frame = ttk.LabelFrame(left_frame, text="Recherche YouTube", style='Custom.TLabelframe',
                                      padding=(15, 10, 15, 15)) # padding(left, top, right, bottom)
        search_frame.pack(fill='x', pady=(0, 10), padx=10) # No top padding for first element

        ttk.Label(search_frame, text="Rechercher:", style='Custom.TLabel').pack(pady=(0, 5), anchor='w')
        self.search_entry = ttk.Entry(search_frame, width=50, style='TEntry')
        self.search_entry.pack(fill='x', pady=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.perform_Youtube())

        search_btn = ttk.Button(search_frame, text="Rechercher", command=self.perform_Youtube,
                                style='Accent.TButton') # Utilise le style Accent
        search_btn.pack(pady=(0, 0), side='right') # Aligné à droite

        # --- NOUVELLE SECTION : Téléchargement direct par URL ---
        url_frame = ttk.LabelFrame(left_frame, text="Téléchargement Direct", style='Custom.TLabelframe',
                                   padding=(15, 10, 15, 15))
        url_frame.pack(fill='x', pady=(0, 10), padx=10)

        ttk.Label(url_frame, text="URL YouTube:", style='Custom.TLabel').pack(pady=(0, 5), anchor='w')
        self.url_entry = ttk.Entry(url_frame, width=50, style='TEntry')
        self.url_entry.pack(fill='x', pady=(0, 10))
        self.url_entry.bind('<Return>', lambda e: self.download_from_url())

        # Frame pour les boutons de téléchargement direct
        url_btn_frame = ttk.Frame(url_frame, style='Custom.TFrame')
        url_btn_frame.pack(fill='x')

        # Sélecteur de format pour URL directe
        format_selector_url_frame = ttk.Frame(url_btn_frame, style='Custom.TFrame')
        format_selector_url_frame.pack(side='left', padx=(0, 15))

        ttk.Label(format_selector_url_frame, text="Format:", style='Custom.TLabel').pack(side='left', padx=(0, 5))
        self.format_combobox_url = ttk.Combobox(format_selector_url_frame,
                                               textvariable=self.download_format_var,
                                               values=["MP3", "MP4", "WAV", "FLAC", "WEBM", "MKV", "M4A", "OPUS", "MOV", "AVI"], # OGG et AAC retirés
                                               state="readonly", width=5, style='TCombobox')
        self.format_combobox_url.pack(side='left')
        self.format_combobox_url.set("MP4") # Valeur par défaut

        download_url_btn = ttk.Button(url_btn_frame, text="Télécharger",
                                     command=self.download_from_url, style='Accent.TButton')
        download_url_btn.pack(side='right')

        add_url_to_memory_btn = ttk.Button(url_btn_frame, text="Ajouter à la Mémoire",
                                          command=self.add_url_to_memory, style='Custom.TButton')
        add_url_to_memory_btn.pack(side='right', padx=(0, 10))

        # Section Résultats de recherche
        results_frame = ttk.LabelFrame(left_frame, text="Résultats de Recherche", style='Custom.TLabelframe',
                                       padding=(15, 10, 15, 15))
        results_frame.pack(fill='both', expand=True, pady=10, padx=10)

        self.results_tree = ttk.Treeview(results_frame, columns=("ID", "Titre", "Durée"), show="headings", style='Treeview')
        self.results_tree.heading("ID", text="ID", anchor=tk.CENTER)
        self.results_tree.heading("Titre", text="Titre", anchor=tk.W)
        self.results_tree.heading("Durée", text="Durée", anchor=tk.CENTER)

        self.results_tree.column("ID", width=30, minwidth=30, anchor=tk.CENTER, stretch=False)
        self.results_tree.column("Titre", width=300, minwidth=150, anchor=tk.W)
        self.results_tree.column("Durée", width=80, minwidth=80, anchor=tk.CENTER, stretch=False)

        self.results_tree.pack(side='left', fill='both', expand=True, padx=(0, 5), pady=(0, 5))

        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview, style='Vertical.TScrollbar')
        results_scrollbar.pack(side='right', fill='y', padx=(0, 0), pady=(0, 5))
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        # Boutons d'action pour les résultats + Sélecteur de format
        results_btn_frame = ttk.Frame(left_frame, style='Custom.TFrame')
        results_btn_frame.pack(fill='x', pady=5, padx=10)

        add_to_memory_btn = ttk.Button(results_btn_frame, text="Ajouter à la Mémoire",
                                       command=self.add_selected_to_memory, style='Custom.TButton')
        add_to_memory_btn.pack(side='left', padx=(0, 5)) # Retire expand=True

        # Sélecteur de format pour les résultats
        format_selector_results_frame = ttk.Frame(results_btn_frame, style='Custom.TFrame')
        format_selector_results_frame.pack(side='left', padx=(5, 15)) # Plus d'espace à droite

        ttk.Label(format_selector_results_frame, text="Format:", style='Custom.TLabel').pack(side='left', padx=(0, 5))
        self.format_combobox_results = ttk.Combobox(format_selector_results_frame,
                                                 textvariable=self.download_format_var,
                                                 values=["MP3", "MP4", "WAV", "FLAC", "WEBM", "MKV", "M4A", "OPUS", "MOV", "AVI"], # OGG et AAC retirés
                                                 state="readonly", width=5, style='TCombobox')
        self.format_combobox_results.pack(side='left')
        self.format_combobox_results.set("MP4") # Valeur par défaut

        download_selected_btn = ttk.Button(results_btn_frame, text="Télécharger Sélection",
                                           command=self.download_selected_from_results, style='Accent.TButton')
        download_selected_btn.pack(side='right', padx=(5, 0)) # Retire expand=True

        # --- Composants du panneau droit ---
        # Section Mémoire/Playlist
        memory_frame = ttk.LabelFrame(right_frame, text="Mémoire (Playlist)", style='Custom.TLabelframe',
                                      padding=(15, 10, 15, 15))
        memory_frame.pack(fill='x', pady=(0, 10), padx=10)

        self.memory_tree = ttk.Treeview(memory_frame, columns=("ID", "Titre", "Durée"), show="headings", style='Treeview')
        self.memory_tree.heading("ID", text="ID", anchor=tk.CENTER)
        self.memory_tree.heading("Titre", text="Titre", anchor=tk.W)
        self.memory_tree.heading("Durée", text="Durée", anchor=tk.CENTER)

        self.memory_tree.column("ID", width=30, minwidth=30, anchor=tk.CENTER, stretch=False)
        self.memory_tree.column("Titre", width=300, minwidth=150, anchor=tk.W)
        self.memory_tree.column("Durée", width=80, minwidth=80, anchor=tk.CENTER, stretch=False)

        self.memory_tree.pack(side='left', fill='x', expand=True, padx=(0, 5), pady=(0, 5))

        memory_scrollbar = ttk.Scrollbar(memory_frame, orient="vertical", command=self.memory_tree.yview, style='Vertical.TScrollbar')
        memory_scrollbar.pack(side='right', fill='y', padx=(0, 0), pady=(0, 5))
        self.memory_tree.configure(yscrollcommand=memory_scrollbar.set)

        # Boutons d'action pour la mémoire + Sélecteur de format
        memory_btn_frame = ttk.Frame(right_frame, style='Custom.TFrame')
        memory_btn_frame.pack(fill='x', pady=5, padx=10)

        # Sélecteur de format pour la mémoire
        format_selector_memory_frame = ttk.Frame(memory_btn_frame, style='Custom.TFrame')
        format_selector_memory_frame.pack(side='left', padx=(0, 15)) # Plus d'espace à droite

        ttk.Label(format_selector_memory_frame, text="Format:", style='Custom.TLabel').pack(side='left', padx=(0, 5))
        self.format_combobox_memory = ttk.Combobox(format_selector_memory_frame,
                                                 textvariable=self.download_format_var, # Partage la même variable
                                                 values=["MP3", "MP4", "WAV", "FLAC", "WEBM", "MKV", "M4A", "OPUS", "MOV", "AVI"], # OGG et AAC retirés
                                                 state="readonly", width=5, style='TCombobox')
        self.format_combobox_memory.pack(side='left')
        self.format_combobox_memory.set("MP4") # Valeur par défaut

        download_memory_btn = ttk.Button(memory_btn_frame, text="Télécharger Tout",
                                         command=self.download_all_from_memory, style='Accent.TButton')
        download_memory_btn.pack(side='left', expand=True, padx=(5, 5)) # Garde expand pour prendre l'espace restant

        remove_from_memory_btn = ttk.Button(memory_btn_frame, text="Supprimer Sélection",
                                            command=self.remove_selected_from_memory, style='Danger.TButton')
        remove_from_memory_btn.pack(side='right', padx=(5, 0))

        clear_memory_btn = ttk.Button(memory_btn_frame, text="Vider la Mémoire",
                                      command=self.clear_all_memory, style='Danger.TButton')
        clear_memory_btn.pack(side='right', padx=(5, 5)) # Ajuster le padx

        # Section Logs
        log_frame = ttk.LabelFrame(right_frame, text="Logs", style='Custom.TLabelframe',
                                   padding=(15, 10, 15, 15))
        log_frame.pack(fill='both', expand=True, pady=10, padx=10)

        self.log_display = scrolledtext.ScrolledText(log_frame, wrap='word', height=10,
                                                     bg=BG_LIGHT, fg=FG_PRIMARY, font=('Consolas', 9),
                                                     state='disabled', relief='flat', borderwidth=0) # Désactiver l'édition
        self.log_display.pack(fill='both', expand=True, padx=5, pady=5) # Ajout de padding

        # --- Menu principal ---
        menubar = tk.Menu(self.root, bg=BG_MEDIUM, fg=FG_PRIMARY, relief='flat', borderwidth=0)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, bg=BG_MEDIUM, fg=FG_PRIMARY,
                             activebackground=ACCENT_COLOR, activeforeground='white')
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Définir le dossier de téléchargement", command=self.set_download_folder)
        file_menu.add_separator(background=BG_DARK)
        file_menu.add_command(label="Quitter", command=self.root.quit)

        config_menu = tk.Menu(menubar, tearoff=0, bg=BG_MEDIUM, fg=FG_PRIMARY,
                             activebackground=ACCENT_COLOR, activeforeground='white')
        menubar.add_cascade(label="Configuration", menu=config_menu)
        config_menu.add_command(label="Configurer la clé API YouTube", command=self.configure_api_key)

        help_menu = tk.Menu(menubar, tearoff=0, bg=BG_MEDIUM, fg=FG_PRIMARY,
                             activebackground=ACCENT_COLOR, activeforeground='white')
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Vérifier Google API Client", command=self.check_google_api_client)
        help_menu.add_command(label="Vérifier yt-dlp", command=self.check_yt_dlp)
        help_menu.add_command(label="Installer yt-dlp", command=self.install_yt_dlp)
        help_menu.add_separator(background=BG_DARK)
        help_menu.add_command(label="Vérifier FFmpeg", command=self.check_ffmpeg_status)
        help_menu.add_command(label="Installer FFmpeg", command=self.offer_ffmpeg_install)

        self.update_memory_display() # Afficher les éléments de la mémoire au démarrage

    def log(self, message: str):
        """Affiche un message dans la zone de log de l'interface graphique."""
        if self.log_display:
            self.root.after(0, lambda: self._update_log_display(message))

    def _update_log_display(self, message: str):
        """Méthode interne pour mettre à jour le widget de log en toute sécurité depuis n'importe quel thread."""
        self.log_display.configure(state='normal')
        self.log_display.insert(tk.END, message + "\n")
        self.log_display.see(tk.END)
        self.log_display.configure(state='disabled')

    def _validate_youtube_url(self, url: str) -> bool:
        """Valide si l'URL fournie est une URL YouTube/YouTube Music valide (vidéos individuelles ou playlists)."""
        youtube_patterns = [
            # Vidéos YouTube classiques
            r'https?://(www\.)?youtube\.com/watch\?v=',
            r'https?://(www\.)?youtu\.be/',
            r'https?://(www\.)?youtube\.com/embed/',
            r'https?://(www\.)?youtube\.com/v/',
            r'https?://m\.youtube\.com/watch\?v=',
            # Playlists YouTube
            r'https?://(www\.)?youtube\.com/playlist\?list=',
            r'https?://(www\.)?youtube\.com/watch\?.*&list=',
            # YouTube Music
            r'https?://music\.youtube\.com/watch\?v=',
            r'https?://music\.youtube\.com/playlist\?list=',
            # YouTube Shorts
            r'https?://(www\.)?youtube\.com/shorts/',
        ]
        import re
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True
        return False

    def _extract_video_info_from_url(self, url: str) -> dict:
        """Extrait les informations de base depuis une URL YouTube/YouTube Music."""
        import re
        # Pour les playlists
        playlist_patterns = [
            r'[&?]list=([^&]+)',
        ]
        # Pour les vidéos individuelles
        video_patterns = [
            r'[?&]v=([^&]+)',
            r'youtu\.be\/([a-zA-Z0-9_-]{11})', # Pour youtu.be/VIDEO_ID
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
        ]

        # Essayer d'extraire le titre et la durée en utilisant youtube-dlp (sans téléchargement)
        try:
            # Utilisez stdout=subprocess.PIPE pour ne pas afficher la sortie de la console
            # Utilisez CREATE_NO_WINDOW sur Windows pour éviter l'ouverture d'une fenêtre de console
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            process = subprocess.run(
                [self.downloader.yt_dlp_path, "--get-title", "--get-duration", "--restrict-filenames", url],
                check=True,
                capture_output=True,
                text=True,
                creationflags=creationflags
            )
            output_lines = process.stdout.strip().split('\n')
            if len(output_lines) >= 2:
                title = output_lines[0].strip()
                duration_str = output_lines[1].strip()

                # yt-dlp retourne la durée en secondes pour --get-duration
                # Convertir les secondes en HH:MM:SS
                try:
                    total_seconds = int(duration_str)
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    duration = f"{hours:02}:{minutes:02}:{seconds:02}"
                except ValueError:
                    duration = "00:00:00" # Fallback si la conversion échoue

                self.log(f"Informations extraites: Titre='{title}', Durée='{duration}'")
                return {"title": title, "url": url, "duration": duration}
            else:
                self.log(f"Impossible d'extraire les informations pour l'URL: {url}. Sortie: {process.stdout.strip()}")
                return {"title": "Titre inconnu", "url": url, "duration": "00:00:00"}
        except FileNotFoundError:
            self.log("Erreur: yt-dlp n'est pas trouvé. Impossible d'extraire les informations.")
            return {"title": "Titre inconnu (yt-dlp non trouvé)", "url": url, "duration": "00:00:00"}
        except subprocess.CalledProcessError as e:
            self.log(f"Erreur lors de l'exécution de yt-dlp pour extraire les infos: {e.stderr}")
            return {"title": "Titre inconnu (erreur yt-dlp)", "url": url, "duration": "00:00:00"}
        except Exception as e:
            self.log(f"Erreur inattendue lors de l'extraction des informations: {e}")
            return {"title": "Titre inconnu (erreur)", "url": url, "duration": "00:00:00"}

    def add_url_to_memory(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Ajouter à la Mémoire", "Veuillez entrer une URL.")
            return

        if not self._validate_youtube_url(url):
            messagebox.showwarning("URL Invalide", "L'URL fournie n'est pas une URL YouTube/YouTube Music valide.")
            return

        self.log(f"Tentative d'extraction des informations pour: {url}")
        # Exécuter l'extraction dans un thread pour ne pas bloquer l'UI
        threading.Thread(target=self._add_url_to_memory_task, args=(url,)).start()

    def _add_url_to_memory_task(self, url: str):
        try:
            info = self._extract_video_info_from_url(url)
            if info and info["title"] != "Titre inconnu" and info["duration"] != "00:00:00":
                if self.memory.add_item(info["title"], info["url"], info["duration"]):
                    self.log(f"Ajouté à la mémoire: {info['title']}")
                    self.root.after(0, self.update_memory_display)
                else:
                    self.log(f"Échec de l'ajout à la mémoire: {info['title']}")
            else:
                self.log(f"Impossible d'obtenir des informations valides pour l'URL: {url}. Non ajouté.")
                self.root.after(0, lambda: messagebox.showerror("Erreur d'extraction", "Impossible d'extraire les informations de la vidéo pour l'URL fournie. Veuillez vérifier l'URL ou votre connexion Internet."))
        except Exception as e:
            self.log(f"Erreur lors de l'ajout de l'URL à la mémoire: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", f"Une erreur est survenue: {e}"))


    def perform_Youtube(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Recherche YouTube", "Veuillez entrer un terme de recherche.")
            return

        if not self.youtube_api.is_available():
            messagebox.showwarning("API YouTube", "La clé API YouTube n'est pas configurée ou est invalide. La recherche ne fonctionnera pas.")
            self.log("Erreur: Clé API YouTube manquante ou invalide.")
            return

        self.log(f"Recherche de '{query}' sur YouTube...")
        # Exécuter la recherche dans un thread pour ne pas bloquer l'UI
        threading.Thread(target=self._perform_Youtube_task, args=(query,)).start()

    def _perform_Youtube_task(self, query: str):
        try:
            results = self.youtube_api.search_videos(query)
            self.search_results = results # Stocker les résultats pour référence
            self.root.after(0, lambda: self.update_results_display(results))
            self.log(f"Recherche terminée. {len(results)} résultats trouvés.")
        except Exception as e:
            self.log(f"Erreur lors de la recherche YouTube: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erreur de Recherche", f"Une erreur est survenue lors de la recherche: {e}"))

    def update_results_display(self, results: list):
        # Effacer les résultats précédents
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Afficher les nouveaux résultats
        for item in results:
            self.results_tree.insert("", "end", values=(item['id'], item['title'], item['duration']), tags=('clickable_row',))
        self.results_tree.tag_bind('clickable_row', '<Double-1>', self.on_results_double_click)


    def update_memory_display(self):
        # Effacer les éléments précédents
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)

        # Afficher les nouveaux éléments de la mémoire
        memory_items = self.memory.get_memory()
        for i, item in enumerate(memory_items):
            self.memory_tree.insert("", "end", iid=str(i), values=(i + 1, item['title'], item['duration']), tags=('clickable_row',))
        self.memory_tree.tag_bind('clickable_row', '<Double-1>', self.on_memory_double_click)

    def on_results_double_click(self, event):
        item_id = self.results_tree.selection()[0]
        item_values = self.results_tree.item(item_id, 'values')
        # L'ID affiché est item_values[0], mais l'index réel est item_values[0] - 1
        selected_result_index = int(item_values[0]) - 1
        
        if 0 <= selected_result_index < len(self.search_results):
            selected_item = self.search_results[selected_result_index]
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, selected_item['url'])
            messagebox.showinfo("Sélection", f"URL copiée: {selected_item['title']}")
        else:
            self.log(f"Erreur: Index de résultat de recherche invalide: {selected_result_index}")


    def on_memory_double_click(self, event):
        item_id = self.memory_tree.selection()[0]
        # L'item_id de la mémoire correspond directement à l'index si inséré avec iid=str(i)
        selected_memory_index = int(item_id)
        
        if 0 <= selected_memory_index < len(self.memory.get_memory()):
            selected_item = self.memory.get_item(selected_memory_index)
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, selected_item['url'])
            messagebox.showinfo("Sélection", f"URL copiée: {selected_item['title']}")
        else:
            self.log(f"Erreur: Index de mémoire invalide: {selected_memory_index}")


    def download_from_url(self):
        url = self.url_entry.get().strip()
        selected_format = self.download_format_var.get().lower()

        if not url:
            messagebox.showwarning("Téléchargement", "Veuillez entrer une URL.")
            return

        if not self._validate_youtube_url(url):
            messagebox.showwarning("URL Invalide", "L'URL fournie n'est pas une URL YouTube/YouTube Music valide.")
            return

        if not self.downloader.yt_dlp_path:
            messagebox.showwarning("yt-dlp introuvable", "yt-dlp n'est pas configuré. Impossible de télécharger. Veuillez l'installer via le menu Aide.")
            return
        
        if (selected_format == "mp3" or selected_format == "wav") and not self.downloader.ffmpeg_path:
            messagebox.showwarning("FFmpeg introuvable", "FFmpeg n'est pas configuré. Impossible de convertir en MP3/WAV. Veuillez l'installer via le menu Aide.")
            return

        self.log(f"Préparation du téléchargement de l'URL: {url} au format {selected_format}...")
        # Lancer le téléchargement dans un thread séparé
        threading.Thread(target=lambda: self._download_single_url_task(url, selected_format)).start()

    def _download_single_url_task(self, url: str, selected_format: str):
        success = self.downloader._download_single_item(url, selected_format)
        self.root.after(0, lambda: self.on_download_complete(success))


    def add_selected_to_memory(self):
        selected_items = self.results_tree.selection()
        if not selected_items:
            messagebox.showwarning("Ajouter à la Mémoire", "Veuillez sélectionner au moins un élément dans les résultats de recherche.")
            return

        success_count = 0
        for item_id in selected_items:
            item_values = self.results_tree.item(item_id, 'values')
            selected_result_index = int(item_values[0]) - 1 # Récupérer l'index original
            
            if 0 <= selected_result_index < len(self.search_results):
                item_data = self.search_results[selected_result_index]
                if self.memory.add_item(item_data['title'], item_data['url'], item_data['duration']):
                    success_count += 1
                else:
                    self.log(f"Échec de l'ajout à la mémoire (doublon ou erreur): {item_data['title']}")
            else:
                self.log(f"Erreur: Index de résultat de recherche invalide lors de l'ajout à la mémoire: {selected_result_index}")

        if success_count > 0:
            messagebox.showinfo("Ajouter à la Mémoire", f"{success_count} élément(s) ajouté(s) à la mémoire.")
            self.update_memory_display()
        else:
            messagebox.showwarning("Ajouter à la Mémoire", "Aucun élément n'a été ajouté (peut-être déjà présent ou erreur).")


    def download_selected_from_results(self):
        selected_items = self.results_tree.selection()
        if not selected_items:
            messagebox.showwarning("Téléchargement", "Veuillez sélectionner au moins un élément dans les résultats de recherche.")
            return

        selected_format = self.download_format_var.get().lower()

        if not self.downloader.yt_dlp_path:
            messagebox.showwarning("yt-dlp introuvable", "yt-dlp n'est pas configuré. Impossible de télécharger. Veuillez l'installer via le menu Aide.")
            return
        
        if (selected_format == "mp3" or selected_format == "wav") and not self.downloader.ffmpeg_path:
            messagebox.showwarning("FFmpeg introuvable", "FFmpeg n'est pas configuré. Impossible de convertir en MP3/WAV. Veuillez l'installer via le menu Aide.")
            return

        urls_to_download = []
        for item_id in selected_items:
            item_values = self.results_tree.item(item_id, 'values')
            selected_result_index = int(item_values[0]) - 1
            if 0 <= selected_result_index < len(self.search_results):
                urls_to_download.append(self.search_results[selected_result_index]['url'])

        if urls_to_download:
            self.log(f"Préparation du téléchargement de {len(urls_to_download)} éléments sélectionnés...")
            self.downloader.download_items_in_bulk(urls_to_download, selected_format, self.on_multiple_download_complete)
        else:
            messagebox.showwarning("Téléchargement", "Aucune URL valide sélectionnée pour le téléchargement.")


    def remove_selected_from_memory(self):
        selected_items = self.memory_tree.selection()
        if not selected_items:
            messagebox.showwarning("Supprimer de la Mémoire", "Veuillez sélectionner au moins un élément à supprimer.")
            return

        # Supprimer en ordre décroissant pour éviter les problèmes d'index
        indices_to_remove = sorted([int(self.memory_tree.item(item_id)['iid']) for item_id in selected_items], reverse=True)
        
        success_count = 0
        for index in indices_to_remove:
            if self.memory.remove_item(index):
                success_count += 1
            else:
                self.log(f"Échec de la suppression de l'élément à l'index {index}.")

        if success_count > 0:
            messagebox.showinfo("Supprimer de la Mémoire", f"{success_count} élément(s) supprimé(s) de la mémoire.")
            self.update_memory_display()
        else:
            messagebox.showwarning("Supprimer de la Mémoire", "Aucun élément n'a pu être supprimé.")

    def clear_all_memory(self):
        if messagebox.askyesno("Vider la Mémoire", "Êtes-vous sûr de vouloir vider toute la mémoire ? Cette action est irréversible."):
            self.memory.clear_memory()
            self.update_memory_display()
            self.log("Toute la mémoire a été vidée.")
            messagebox.showinfo("Vider la Mémoire", "La mémoire a été entièrement vidée.")

    def download_all_from_memory(self):
        urls_to_download = self.memory.get_urls()
        if not urls_to_download:
            messagebox.showwarning("Téléchargement", "La mémoire est vide. Aucun élément à télécharger.")
            return

        selected_format = self.download_format_var.get().lower()

        if not self.downloader.yt_dlp_path:
            messagebox.showwarning("yt-dlp introuvable", "yt-dlp n'est pas configuré. Impossible de télécharger. Veuillez l'installer via le menu Aide.")
            return
        
        if (selected_format == "mp3" or selected_format == "wav") and not self.downloader.ffmpeg_path:
            messagebox.showwarning("FFmpeg introuvable", "FFmpeg n'est pas configuré. Impossible de convertir en MP3/WAV. Veuillez l'installer via le menu Aide.")
            return

        self.log(f"Préparation du téléchargement de tous les {len(urls_to_download)} éléments de la mémoire...")
        self.downloader.download_items_in_bulk(urls_to_download, selected_format, self.on_multiple_download_complete)


    def configure_api_key(self):
        current_key = self.config.api_key
        dialog = APIKeyDialog(self.root, current_key)
        self.root.wait_window(dialog.dialog)
        if dialog.result is not None:
            new_key = dialog.result
            self.config.set_api_key(new_key)
            self.config.save_config()
            self.youtube_api.set_api_key(new_key) # Mettre à jour l'API YouTube
            self.log("Clé API YouTube sauvegardée.")
            if self.youtube_api.is_available():
                messagebox.showinfo("Configuration API", "Clé API YouTube sauvegardée et validée.")
            else:
                messagebox.showwarning("Configuration API", "Clé API sauvegardée, mais la connexion à l'API a échoué. Vérifiez votre clé ou votre connexion internet.")

    def check_google_api_client(self):
        if GOOGLE_API_AVAILABLE:
            if self.youtube_api.is_available():
                messagebox.showinfo("Vérification API", "google-api-python-client est installé et la clé API YouTube est configurée correctement.")
                self.log("API Google YouTube: Disponible et configurée.")
            else:
                messagebox.showwarning("Vérification API", "google-api-python-client est installé, mais la clé API YouTube n'est pas configurée ou est invalide. Veuillez la configurer.")
                self.log("API Google YouTube: Installée mais non configurée/valide.")
        else:
            messagebox.showerror("Vérification API", "google-api-python-client n'est pas installé. La recherche YouTube ne fonctionnera pas.\n\nVeuillez l'installer avec : pip install google-api-python-client")
            self.log("API Google YouTube: Non installée.")


    def check_yt_dlp(self):
        """Vérifie si yt-dlp est installé et met à jour son chemin."""
        yt_dlp_location = self.downloader.find_yt_dlp_location()
        if yt_dlp_location:
            messagebox.showinfo("Vérification yt-dlp", f"yt-dlp est trouvé à : {yt_dlp_location}")
        else:
            messagebox.showwarning("Vérification yt-dlp", "yt-dlp n'est pas trouvé. La fonctionnalité de téléchargement pourrait être limitée.")


    def install_yt_dlp(self):
        response = messagebox.askyesno(
            "Installer yt-dlp",
            "yt-dlp est nécessaire pour le téléchargement. Voulez-vous télécharger yt-dlp.exe (pour Windows) ou ouvrir la page de téléchargement officielle ?"
        )
        if response:
            if sys.platform == "win32":
                try:
                    # Téléchargement via le navigateur
                    webbrowser.open("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe")
                    messagebox.showinfo("Téléchargement yt-dlp", "Le téléchargement de yt-dlp.exe devrait commencer dans votre navigateur. Placez le fichier téléchargé dans le même dossier que l'exécutable de cette application.")
                    self.log("Ouverture du lien de téléchargement de yt-dlp.exe.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible d'ouvrir le navigateur : {e}")
            else: # Pour Linux/macOS, ouvrir la page GitHub
                webbrowser.open("https://github.com/yt-dlp/yt-dlp#installation")
                messagebox.showinfo("Installation yt-dlp", "La page d'installation de yt-dlp s'est ouverte dans votre navigateur. Suivez les instructions pour votre système.")
                self.log("Ouverture de la page d'installation de yt-dlp.")
        # Après l'installation supposée, vérifier à nouveau la localisation
        self.root.after(1000, self.check_yt_dlp)


    def check_ffmpeg_status(self):
        """Vérifie si FFmpeg est installé et met à jour son chemin."""
        ffmpeg_location = self.downloader.find_ffmpeg_location()
        if ffmpeg_location:
            messagebox.showinfo("Vérification FFmpeg", f"FFmpeg est trouvé à : {ffmpeg_location}")
        else:
            messagebox.showwarning("Vérification FFmpeg", "FFmpeg n'est pas trouvé. La conversion en MP3/WAV pourrait ne pas fonctionner. Veuillez l'installer.")


    def offer_ffmpeg_install(self):
        response = messagebox.askyesno(
            "Installer FFmpeg",
            "FFmpeg est nécessaire pour convertir les vidéos en MP3/WAV. Voulez-vous ouvrir la page de téléchargement officielle ?"
        )
        if response:
            webbrowser.open("https://ffmpeg.org/download.html")
            messagebox.showinfo("Téléchargement FFmpeg", "La page de téléchargement de FFmpeg s'est ouverte dans votre navigateur. Téléchargez la version adaptée à votre système et placez les exécutables (ffmpeg, ffprobe, ffplay) dans le même dossier que cette application, ou ajoutez-les à votre PATH système.")
            self.log("Ouverture du lien de téléchargement de FFmpeg.")
        # Après l'installation supposée, vérifier à nouveau la localisation
        self.root.after(1000, self.check_ffmpeg_status)


    def check_and_offer_yt_dlp_install(self):
        """Vérifie yt-dlp au démarrage et propose l'installation si non trouvé."""
        if not self.downloader.find_yt_dlp_location():
            # Donner un court délai pour que l'interface soit visible avant le popup
            self.root.after(500, lambda: messagebox.showwarning(
                "yt-dlp Manquant",
                "yt-dlp (le téléchargeur) n'a pas été trouvé sur votre système. "
                "Sans lui, les fonctionnalités de téléchargement ne fonctionneront pas.\n\n"
                "Veuillez l'installer via le menu 'Aide' -> 'Installer yt-dlp'."
            ))
            self.log("Avertissement: yt-dlp n'a pas été trouvé au démarrage.")

    def check_and_offer_ffmpeg_install(self):
        """Vérifie FFmpeg au démarrage et propose l'installation si non trouvé."""
        if not self.downloader.find_ffmpeg_location():
            # Donner un court délai pour que l'interface soit visible avant le popup
            self.root.after(600, lambda: messagebox.showwarning(
                "FFmpeg Manquant",
                "FFmpeg (le convertisseur audio/vidéo) n'a pas été trouvé sur votre système. "
                "Sans lui, la conversion en MP3, WAV, etc. ne fonctionnera pas.\n\n"
                "Veuillez l'installer via le menu 'Aide' -> 'Installer FFmpeg'."
            ))
            self.log("Avertissement: FFmpeg n'a pas été trouvé au démarrage.")

    def set_download_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.config.download_path)
        if folder_selected:
            self.config.set_download_path(folder_selected)
            self.downloader.set_download_path(folder_selected)
            self.log(f"Dossier de téléchargement défini sur: {self.config.download_path}")

    def on_download_complete(self, success: bool):
        """Callback après un téléchargement unique. (Peut être supprimé si tout passe par download_items_in_bulk)"""
        if success:
            self.log("Téléchargement de vidéo terminé avec succès.")
        else:
            self.log("Échec du téléchargement de la vidéo.")

    def on_multiple_download_complete(self, success_count: int, total_count: int):
        """Callback après un téléchargement multiple."""
        self.log(f"Téléchargement multiple terminé: {success_count} sur {total_count} réussis.")
        if success_count == total_count:
            messagebox.showinfo("Téléchargement Terminé", f"Tous les {total_count} éléments ont été téléchargés avec succès!")
        elif success_count > 0:
            messagebox.showwarning("Téléchargement Partiel", f"{success_count} sur {total_count} éléments ont été téléchargés. Voir les logs pour les détails.")
        else:
            messagebox.showerror("Échec du Téléchargement", "Aucun élément n'a pu être téléchargé. Voir les logs pour les détails.")

    def run(self):
        """Lancer l'application."""
        self.root.mainloop()