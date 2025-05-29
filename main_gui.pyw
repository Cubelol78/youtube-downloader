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

    # --- NOUVELLES MÉTHODES POUR LE TÉLÉCHARGEMENT PAR URL ---
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
            r'youtu\.be/([^?]+)',
            r'/embed/([^?]+)',
            r'/v/([^?]+)',
            r'/shorts/([^?]+)',
        ]

        # Vérifier si c'est une playlist
        for pattern in playlist_patterns:
            match = re.search(pattern, url)
            if match:
                playlist_id = match.group(1)
                # Vérifier si c'est aussi une vidéo spécifique dans la playlist
                video_id = None
                for video_pattern in video_patterns:
                    video_match = re.search(video_pattern, url)
                    if video_match:
                        video_id = video_match.group(1)
                        break

                if video_id:
                    return {
                        'type': 'video_in_playlist',
                        'video_id': video_id,
                        'playlist_id': playlist_id,
                        'title': f'Vidéo {video_id} (Playlist {playlist_id})'
                    }
                else:
                    return {
                        'type': 'playlist',
                        'playlist_id': playlist_id,
                        'title': f'Playlist YouTube - {playlist_id}'
                    }

        # Vérifier si c'est une vidéo individuelle
        for pattern in video_patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                # Déterminer la source
                source = "YouTube Music" if "music.youtube.com" in url else "YouTube" # Correction pour identifier YouTube Music
                return {
                    'type': 'video',
                    'video_id': video_id,
                    'title': f'Vidéo {source} - {video_id}'
                }

        # Fallback
        return {
            'type': 'unknown',
            'title': 'Contenu YouTube (URL directe)'
        }

    def download_from_url(self):
        """Télécharge directement depuis une URL fournie (vidéos, playlists, YouTube Music)."""
        url = self.url_entry.get().strip()
        if not url:
            self.log("Veuillez entrer une URL YouTube.")
            messagebox.showwarning("URL manquante", "Veuillez entrer une URL YouTube à télécharger.")
            return

        if not self._validate_youtube_url(url):
            self.log("URL YouTube invalide.")
            messagebox.showerror("URL invalide", "L'URL fournie ne semble pas être une URL YouTube/YouTube Music valide.")
            return

        # Extraire les informations de l'URL
        url_info = self._extract_video_info_from_url(url)

        download_format = self.download_format_var.get()
        # Plus besoin de is_audio_only, le format est passé directement

        # Messages différents selon le type de contenu
        if url_info['type'] == 'playlist':
            self.log(f"Téléchargement de playlist en format {download_format}: {url}")
            messagebox.showinfo("Playlist détectée",
                            f"Une playlist a été détectée. Le téléchargement peut prendre du temps selon le nombre de vidéos.\n"
                            f"Format: {download_format}")
        elif url_info['type'] == 'video_in_playlist':
            self.log(f"Téléchargement de vidéo spécifique dans playlist en format {download_format}: {url}")
        else:
            self.log(f"Téléchargement direct en format {download_format} de: {url}")

        def download_callback(success_count, total_count):
            if success_count > 0:
                if url_info['type'] == 'playlist':
                    self.log(f"Téléchargement de playlist terminé: {success_count}/{total_count} vidéos réussies.")
                    messagebox.showinfo("Téléchargement Terminé",
                                    f"Playlist téléchargée: {success_count}/{total_count} vidéos réussies!")
                else:
                    self.log("Téléchargement direct terminé avec succès.")
                    messagebox.showinfo("Téléchargement Terminé", "Le téléchargement a été effectué avec succès!")
                # Vider le champ URL après un téléchargement réussi
                self.url_entry.delete(0, tk.END)
            else:
                self.log("Échec du téléchargement direct.")
                messagebox.showerror("Échec du Téléchargement", "Le téléchargement a échoué. Vérifiez les logs pour plus de détails.")

        self.downloader.download_items_in_bulk([url], download_format, callback=download_callback) # Passer le format

    def add_url_to_memory(self):
        """Ajoute l'URL directement à la mémoire avec un titre informatif."""
        url = self.url_entry.get().strip()
        if not url:
            self.log("Veuillez entrer une URL YouTube.")
            messagebox.showwarning("URL manquante", "Veuillez entrer une URL YouTube à ajouter à la mémoire.")
            return

        if not self._validate_youtube_url(url):
            self.log("URL YouTube invalide.")
            messagebox.showerror("URL invalide", "L'URL fournie ne semble pas être une URL YouTube/YouTube Music valide.")
            return

        # Extraire les informations de l'URL
        url_info = self._extract_video_info_from_url(url)
        title = url_info['title']

        # Message d'avertissement pour les playlists
        if url_info['type'] == 'playlist':
            if not messagebox.askyesno("Playlist détectée",
                                    "Vous ajoutez une playlist entière à la mémoire. "
                                    "Cela téléchargera toutes les vidéos de la playlist lors du téléchargement.\n\n"
                                    "Voulez-vous continuer ?"):
                return
            title = f"🎵 {title}"  # Icône pour identifier les playlists
        elif url_info['type'] == 'video_in_playlist':
            title = f"📹 {title}"  # Icône pour vidéo dans playlist
        elif "music.youtube.com" in url: # Vérification correcte pour YouTube Music
            title = f"🎶 {title}"  # Icône pour YouTube Music

        if self.memory.add_item(title, url, "Inconnue"):
            self.log(f"URL ajoutée à la mémoire: {url}")
            self.update_memory_display()
            # Vider le champ URL après ajout réussi
            self.url_entry.delete(0, tk.END)
            messagebox.showinfo("Ajout Réussi", "L'URL a été ajoutée à la mémoire avec succès!")
        else:
            self.log(f"Échec de l'ajout de l'URL à la mémoire: {url}")
            messagebox.showerror("Échec de l'Ajout", "Impossible d'ajouter l'URL à la mémoire.")

    def check_and_offer_yt_dlp_install(self):
        """Vérifie si yt-dlp est installé et le propose d'installer si non."""
        self.log("Vérification de yt-dlp...")
        if not self.downloader.check_yt_dlp_installed():
            self.log("yt-dlp n'est pas installé ou introuvable. Installation recommandée.")
            if messagebox.askyesno("Installation de yt-dlp", "yt-dlp n'est pas trouvé. Voulez-vous l'installer maintenant ?"):
                self.log("La fonctionnalité d'installation automatique de yt-dlp n'est pas implémentée.")
                messagebox.showwarning("Installation manuelle", "Veuillez télécharger yt-dlp manuellement depuis leur GitHub et l'ajouter à votre PATH.")
            else:
                self.log("L'installation de yt-dlp a été annulée. Certaines fonctionnalités pourraient ne pas fonctionner.")
        else:
            self.log("yt-dlp est déjà installé et accessible.")

    def check_yt_dlp(self):
        """Vérifie et affiche le statut de yt-dlp."""
        self.log("Vérification du statut de yt-dlp...")
        if self.downloader.check_yt_dlp_installed():
            self.log("yt-dlp est installé et accessible.")
        else:
            self.log("yt-dlp n'est pas installé ou n'a pas pu être trouvé.")

    def install_yt_dlp(self):
        """Lance l'installation de yt-dlp dans un thread séparé."""
        self.log("Cette fonction n'est pas implémentée pour l'installation automatique de yt-dlp.")
        messagebox.showwarning("Installation manuelle", "Veuillez télécharger yt-dlp manuellement depuis leur GitHub et l'ajouter à votre PATH.")

    def on_yt_dlp_install_complete(self, success: bool):
        """Callback après l'installation de yt-dlp."""
        if success:
            self.log("yt-dlp a été installé avec succès.")
            messagebox.showinfo("Installation réussie", "yt-dlp a été installé avec succès!")
            self.root.after(0, self.check_and_offer_ffmpeg_install)
        else:
            self.log("Échec de l'installation de yt-dlp.")
            messagebox.showerror("Erreur d'installation", "Échec de l'installation de yt-dlp. Veuillez vérifier les logs.")

    def check_and_offer_ffmpeg_install(self):
        """Vérifie si FFmpeg est installé et le propose d'installer si non."""
        self.log("Vérification de FFmpeg...")
        if not self.downloader.check_ffmpeg_installed():
            self.log("FFmpeg n'est pas installé ou introuvable. Nécessaire pour la conversion MP3.")
            if messagebox.askyesno("Installation de FFmpeg",
                                   "FFmpeg n'est pas trouvé sur votre système, ce qui est nécessaire pour convertir les vidéos en MP3.\nVoulez-vous ouvrir la page de téléchargement de FFmpeg maintenant ?\nVous devrez télécharger FFmpeg et le placer manuellement dans le dossier './ffmpeg/bin' à côté de l'exécutable de l'application."
                                   ):
                self.offer_ffmpeg_install()
            else:
                self.log("L'installation de FFmpeg a été annulée. Les téléchargements seront effectués au format d'origine (ex: WebM) si possible.")
        else:
            self.log("FFmpeg est déjà installé et accessible.")

    def check_ffmpeg_status(self):
        """Affiche le statut de FFmpeg."""
        self.log("Vérification du statut de FFmpeg...")
        if self.downloader.check_ffmpeg_installed():
            self.log("FFmpeg est installé et accessible.")
        else:
            self.log("FFmpeg n'est pas installé ou n'a pas pu être trouvé.")
            messagebox.showwarning("FFmpeg manquant", "FFmpeg n'est pas installé ou introuvable.\nLa conversion en MP3 ne fonctionnera pas sans lui.")
            self.offer_ffmpeg_install()

    def offer_ffmpeg_install(self):
        """Ouvre le navigateur sur la page de téléchargement de FFmpeg."""
        self.log("Ouverture de la page de téléchargement de FFmpeg...")
        webbrowser.open("https://ffmpeg.org/download.html")
        messagebox.showinfo("Instructions FFmpeg",
                            "Veuillez télécharger FFmpeg depuis la page qui s'est ouverte dans votre navigateur.\n\n"
                            "Après le téléchargement, vous devrez l'extraire et placer le contenu du dossier 'bin' de FFmpeg dans le dossier './ffmpeg/bin' à côté du fichier 'main.py' ou de l'exécutable de l'application."
                           )

    def check_google_api_client(self):
        """Vérifie si google-api-python-client est installé."""
        self.log("Vérification de google-api-python-client...")
        if GOOGLE_API_AVAILABLE:
            self.log("google-api-python-client est déjà installé.")
            if not self.youtube_api.is_available():
                self.log("Clé API YouTube non configurée ou invalide. La recherche YouTube ne fonctionnera pas.")
        else:
            self.log("google-api-python-client n'est pas installé. La recherche YouTube ne fonctionnera pas.")
            if messagebox.askyesno("Installation Google API", "Le client Google API n'est pas trouvé. Voulez-vous l'installer ?"):
                self.install_google_api_client()

    def install_google_api_client(self):
        """Installe google-api-python-client."""
        self.log("Tentative d'installation de Google API...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "google-api-python-client"])
            self.log("google-api-python-client installé avec succès!")
            self.root.after(0, lambda: messagebox.showinfo("Installation réussie",
                "Google API Python Client installé!\nRedémarrez l'application pour activer la recherche YouTube."))
        except subprocess.CalledProcessError:
            self.log("Erreur lors de l'installation de google-api-python-client")
            self.root.after(0, lambda: messagebox.showerror("Erreur d'installation",
                "Impossible d'installer google-api-python-client automatiquement.\nVeuillez l'installer manuellement avec:\npip install google-api-python-client"))

    def configure_api_key(self):
        """Configurer la clé API YouTube"""
        dialog = APIKeyDialog(self.root, self.config.api_key)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.config.set_api_key(dialog.result)
            self.youtube_api.set_api_key(dialog.result)

            if self.youtube_api.is_available():
                self.log("Clé API YouTube configurée avec succès!")
            else:
                self.log("Erreur avec la clé API fournie")

    def perform_Youtube(self):
        """Lance une recherche YouTube."""
        query = self.search_entry.get().strip()
        if not query:
            self.log("Veuillez entrer un terme de recherche.")
            return

        if not self.youtube_api.is_available():
            self.log("L'API YouTube n'est pas configurée ou accessible. Veuillez vérifier votre clé API et l'installation du client Google API.")
            messagebox.showerror("API YouTube non disponible", "L'API YouTube n'est pas configurée ou accessible.")
            return

        self.log(f"Recherche YouTube pour: '{query}'...")
        # Effacer les résultats précédents
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.search_results = []

        def search_thread():
            try:
                results = self.youtube_api.search_videos(query)
                self.root.after(0, lambda: self.display_search_results(results))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Erreur lors de la recherche: {e}"))
                self.root.after(0, lambda: messagebox.showerror("Erreur de recherche", f"Erreur lors de la recherche: {e}"))

        threading.Thread(target=search_thread, daemon=True).start()

    def display_search_results(self, results: list):
        """Affiche les résultats de la recherche dans le Treeview."""
        self.search_results = results
        for i, item in enumerate(self.search_results):
            self.results_tree.insert("", "end", iid=str(i),
                                     values=(item['id'], item['title'], item['duration']))
        self.log(f"Recherche terminée. {len(results)} résultats trouvés.")

    def add_selected_to_memory(self):
        """Ajoute les éléments sélectionnés des résultats de recherche à la mémoire."""
        selected_items = self.results_tree.selection()
        if not selected_items:
            self.log("Aucun élément sélectionné dans les résultats de recherche.")
            return

        for item_id in selected_items:
            index = int(item_id)
            if 0 <= index < len(self.search_results):
                item_data = self.search_results[index]
                if self.memory.add_item(item_data['title'], item_data['url'], item_data['duration']):
                    self.log(f"Ajouté à la mémoire: {item_data['title']}")
                else:
                    self.log(f"Échec de l'ajout à la mémoire: {item_data['title']}")
        self.update_memory_display()

    def download_selected_from_results(self):
        """Télécharge les éléments sélectionnés des résultats de recherche."""
        selected_items = self.results_tree.selection()
        if not selected_items:
            self.log("Aucun élément sélectionné pour le téléchargement.")
            return

        urls_to_download = []
        for item_id in selected_items:
            index = int(item_id)
            if 0 <= index < len(self.search_results):
                urls_to_download.append(self.search_results[index]['url'])

        if urls_to_download:
            download_format = self.download_format_var.get()
            # Plus besoin de is_audio_only, le format est passé directement

            self.log(f"Préparation au téléchargement de {len(urls_to_download)} éléments en format {download_format}...")
            self.downloader.download_items_in_bulk(urls_to_download, download_format, callback=self.on_multiple_download_complete) # Passer le format

    def update_memory_display(self):
        """Met à jour l'affichage de la mémoire."""
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)

        memory_data = self.memory.get_memory()
        for i, item in enumerate(memory_data):
            self.memory_tree.insert("", "end", iid=str(i),
                                    values=(i+1, item['title'], item['duration']))

    def download_all_from_memory(self):
        """Télécharge toutes les URLs de la mémoire (gère les playlists)."""
        urls = self.memory.get_urls()
        if not urls:
            self.log("La mémoire est vide. Rien à télécharger.")
            return

        # Compter les playlists pour avertir l'utilisateur
        playlist_count = 0
        for url in urls:
            url_info = self._extract_video_info_from_url(url)
            if url_info['type'] == 'playlist':
                playlist_count += 1

        if playlist_count > 0:
            if not messagebox.askyesno("Playlists détectées",
                                    f"Votre mémoire contient {playlist_count} playlist(s). "
                                    f"Le téléchargement peut prendre beaucoup de temps.\n\n"
                                    f"Total d'éléments en mémoire: {len(urls)}\n"
                                    f"Voulez-vous continuer ?"):
                return

        download_format = self.download_format_var.get()
        # Plus besoin de is_audio_only, le format est passé directement

        self.log(f"Téléchargement de tous les {len(urls)} éléments de la mémoire en format {download_format}...")
        if playlist_count > 0:
            self.log(f"Attention: {playlist_count} playlist(s) détectée(s), le téléchargement peut être long.")

        self.downloader.download_items_in_bulk(urls, download_format, callback=self.on_multiple_download_complete) # Passer le format

    def remove_selected_from_memory(self):
        """Supprime les éléments sélectionnés de la mémoire."""
        selected_items = self.memory_tree.selection()
        if not selected_items:
            self.log("Aucun élément sélectionné dans la mémoire à supprimer.")
            return

        # Supprimer en ordre inverse pour éviter les problèmes d'index
        # L'iid est déjà l'item_id lui-même. Nous devons le convertir en int car il a été inséré comme str(i).
        indices_to_remove = sorted([int(item_id) for item_id in selected_items], reverse=True)

        for index in indices_to_remove:
            if self.memory.remove_item(index):
                self.log(f"Élément supprimé de la mémoire (index: {index+1}).")
            else:
                self.log(f"Échec de la suppression de l'élément à l'index {index+1}.")
        self.update_memory_display()

    def clear_all_memory(self):
        """Vide toute la mémoire."""
        if messagebox.askyesno("Vider la mémoire", "Êtes-vous sûr de vouloir vider toute la mémoire ? Cette action est irréversible."):
            self.memory.clear_memory()
            self.update_memory_display()
            self.log("Toute la mémoire a été vidée.")

    def set_download_folder(self):
        """Ouvre une boîte de dialogue pour définir le dossier de téléchargement."""
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
        """Lancer l'application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MusicDLGUI()
    app.run()