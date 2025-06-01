# main_gui.py
import os
import sys
import glob
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import webbrowser # Pour ouvrir le lien de téléchargement
import uuid # Pour générer des IDs uniques pour les téléchargements
import queue # Pour gérer la file d'attente des téléchargements
import json # Pour parser la sortie JSON de yt-dlp

from config_manager import ConfigManager
from youtube_api import YouTubeAPI, GOOGLE_API_AVAILABLE
from downloader import Downloader
from memory_manager import MemoryManager
from dialogs import APIKeyDialog

class MusicDLGUI:
    def __init__(self):
        # Initialiser les gestionnaires
        self.config = ConfigManager()
        self.log_display = None
        self.youtube_api = YouTubeAPI(self.config.api_key)
        
        # Initialiser le downloader avec le callback de progression
        # self.update_download_progress est appelé après setup_gui, donc self.root est créé
        self.downloader = Downloader(self.config.download_path, self.log, self.update_download_progress)
        self.memory = MemoryManager()
        
        # Initialize download counters
        self.active_downloads_count = 0

        # Données temporaires pour les recherches
        self.search_results = []

        # Liste pour suivre les téléchargements actifs, terminés et échoués
        # Chaque élément sera un dict: {'id': uuid, 'title': str, 'status': str, 'progress': float, 'url': str, 'format': str}
        self.downloads_list = []
        # Dictionnaire pour mapper download_id aux widgets Tkinter de la carte de téléchargement
        self.download_widgets = {} # {'download_id': {'card_frame': ..., 'title_label': ..., 'status_label': ..., 'progressbar': ..., 'cancel_button': ...}}

        self.download_format_var = None # Initialiser à None ici

        # --- Gestion de la file d'attente des téléchargements ---
        self.download_queue = queue.Queue()
        self.active_download_count = 0 # Compteur interne des téléchargements actifs - DOIT ÊTRE INITIALISÉ ICI
        self.concurrent_limit = self.config.get_concurrent_downloads_limit() # Récupérer la limite depuis la config
        self.download_lock = threading.Lock() # Pour synchroniser l'accès à active_download_count et la queue

        # Les variables Tkinter pour les compteurs sont maintenant créées dans setup_gui()
        self.active_downloads_count_var = None
        self.completed_downloads_count_var = None
        self.failed_downloads_count_var = None
        self.pending_downloads_count_var = None # Nouvelle variable pour les téléchargements en attente


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

        # Initialisation des variables Tkinter après la création de self.root
        self.download_format_var = tk.StringVar(value="MP4") # Valeur par défaut
        self.active_downloads_count_var = tk.IntVar(value=0)
        self.completed_downloads_count_var = tk.IntVar(value=0)
        self.failed_downloads_count_var = tk.IntVar(value=0) # Inclura les échecs et les annulations
        self.pending_downloads_count_var = tk.IntVar(value=0) # Initialisation ici


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
        
        # Style pour les cadres de téléchargement individuels
        style.configure('DownloadCard.TFrame', background=BG_MEDIUM, relief='solid', borderwidth=1,
                        padding=(10, 10))

        # Styles pour les Labels
        style.configure('Custom.TLabel', background=BG_DARK, foreground=FG_PRIMARY, font=('Arial', 10))
        style.configure('Heading.TLabel', background=BG_DARK, foreground=FG_PRIMARY, font=('Arial', 12, 'bold'))
        style.configure('DownloadTitle.TLabel', background=BG_MEDIUM, foreground=FG_PRIMARY, font=('Arial', 10, 'bold'))
        style.configure('DownloadStatus.TLabel', background=BG_MEDIUM, foreground=FG_SECONDARY, font=('Arial', 9))
        # Nouveau style pour les compteurs
        style.configure('Counter.TLabel', background=BG_DARK, foreground=FG_PRIMARY, font=('Arial', 11, 'bold'))


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

        # Styles pour les Treeview (pour Mémoire et Résultats)
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
        
        # Style pour la barre de progression (nouveau)
        style.configure("TProgressbar", thickness=15, troughcolor=BG_DARK,
                        background=ACCENT_COLOR, borderwidth=0, relief='flat')
        style.map("TProgressbar",
                  background=[('active', ACCENT_COLOR)])

        # --- NOUVEAUX STYLES POUR LES ONGLET DU NOTEBOOK ---
        style.configure('TNotebook', background=BG_DARK, borderwidth=0)
        style.configure('TNotebook.Tab',
                        background=BG_MEDIUM, foreground=FG_PRIMARY,
                        font=('Arial', 10, 'bold'), padding=[10, 5])
        style.map('TNotebook.Tab',
                  background=[('selected', BG_DARK), ('active', BUTTON_ACTIVE_BG)],
                  foreground=[('selected', ACCENT_COLOR), ('active', FG_PRIMARY)])
        style.configure('TNotebook.Tab', focuscolor=BG_DARK) # Supprime le contour en pointillé au focus


        # --- Layout principal ---
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=BG_DARK, bd=0, relief='flat')
        main_pane.pack(fill='both', expand=True, padx=10, pady=10)

        # Panneau gauche (Recherche YouTube)
        left_frame = ttk.Frame(main_pane, style='Custom.TFrame')
        main_pane.add(left_frame, width=450, minsize=350) # minsize pour redimensionnement

        # Panneau droit (Mémoire, Téléchargements et Logs)
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
                                               values=["MP3", "MP4", "WAV", "FLAC", "WEBM", "MKV", "M4A", "OPUS", "MOV", "AVI"],
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
                                                 values=["MP3", "MP4", "WAV", "FLAC", "WEBM", "MKV", "M4A", "OPUS", "MOV", "AVI"],
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
                                                 values=["MP3", "MP4", "WAV", "FLAC", "WEBM", "MKV", "M4A", "OPUS", "MOV", "AVI"],
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

        # --- Notebook pour Logs et Téléchargements ---
        self.notebook = ttk.Notebook(right_frame, style='TNotebook') # Applique le style TNotebook ici
        self.notebook.pack(fill='both', expand=True, pady=10, padx=10)

        # Tab pour les Logs
        log_tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(log_tab, text="Logs")

        log_frame = ttk.LabelFrame(log_tab, text="Logs", style='Custom.TLabelframe',
                                   padding=(15, 10, 15, 15))
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.log_display = scrolledtext.ScrolledText(log_frame, wrap='word', height=10,
                                                     bg=BG_LIGHT, fg=FG_PRIMARY, font=('Consolas', 9),
                                                     state='disabled', relief='flat', borderwidth=0)
        self.log_display.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab pour les Téléchargements (nouveau)
        downloads_tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(downloads_tab, text="Téléchargements")

        # --- Compteurs de téléchargement (dans l'onglet Téléchargements) ---
        counters_frame = ttk.Frame(downloads_tab, style='Custom.TFrame', padding=(5, 5))
        counters_frame.pack(fill='x', pady=(0, 5), padx=5)

        ttk.Label(counters_frame, text="En cours:", style='Counter.TLabel', background=BG_DARK).pack(side='left', padx=(0, 5))
        ttk.Label(counters_frame, textvariable=self.active_downloads_count_var, style='Counter.TLabel', foreground=ACCENT_COLOR, background=BG_DARK).pack(side='left', padx=(0, 15))

        ttk.Label(counters_frame, text="Terminés:", style='Counter.TLabel', background=BG_DARK).pack(side='left', padx=(0, 5))
        ttk.Label(counters_frame, textvariable=self.completed_downloads_count_var, style='Counter.TLabel', foreground="green", background=BG_DARK).pack(side='left', padx=(0, 15))
        
        ttk.Label(counters_frame, text="En attente:", style='Counter.TLabel', background=BG_DARK).pack(side='left', padx=(0, 5))
        ttk.Label(counters_frame, textvariable=self.pending_downloads_count_var, style='Counter.TLabel', foreground="orange", background=BG_DARK).pack(side='left', padx=(0, 15))


        ttk.Label(counters_frame, text="Échoués/Annulés:", style='Counter.TLabel', background=BG_DARK).pack(side='left', padx=(0, 5))
        ttk.Label(counters_frame, textvariable=self.failed_downloads_count_var, style='Counter.TLabel', foreground=DANGER_COLOR, background=BG_DARK).pack(side='left', padx=(0, 0))


        # Utiliser un Canvas pour rendre la zone de téléchargements scrollable
        self.downloads_canvas = tk.Canvas(downloads_tab, bg=BG_DARK, highlightthickness=0)
        self.downloads_canvas.pack(side='left', fill='both', expand=True)

        self.downloads_scrollbar = ttk.Scrollbar(downloads_tab, orient="vertical", command=self.downloads_canvas.yview, style='Vertical.TScrollbar')
        self.downloads_scrollbar.pack(side='right', fill='y')

        self.downloads_canvas.configure(yscrollcommand=self.downloads_scrollbar.set)
        
        # Frame à l'intérieur du Canvas pour contenir les cartes de téléchargement
        # Le tag "downloads_frame_window" est utilisé pour identifier cette fenêtre dans le canvas
        self.downloads_container_frame = ttk.Frame(self.downloads_canvas, style='Custom.TFrame')
        self.downloads_container_frame_id = self.downloads_canvas.create_window((0, 0), window=self.downloads_container_frame, anchor='nw', tags="downloads_frame_window")

        # Bind pour redimensionner le frame interne lorsque le canvas est redimensionné
        self.downloads_container_frame.bind("<Configure>", lambda e: self.downloads_canvas.configure(scrollregion=self.downloads_canvas.bbox("all")))
        self.downloads_canvas.bind('<Configure>', self._on_canvas_resize)


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
        config_menu.add_command(label="Définir la limite de téléchargements", command=self.set_concurrent_downloads_limit_dialog) # Nouvelle option

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

    def _on_canvas_resize(self, event):
        """Redimensionne la fenêtre interne du canvas pour qu'elle corresponde à la largeur du canvas."""
        self.downloads_canvas.itemconfig(self.downloads_container_frame_id, width=event.width)


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

    def _extract_video_info_from_url(self, url: str) -> list:
        """
        Extrait les informations (titre, URL, durée) depuis une URL YouTube/YouTube Music.
        Gère à la fois les vidéos individuelles et les playlists.
        Retourne une liste de dictionnaires, chaque dict étant {'title': ..., 'url': ..., 'duration': ...}.
        """
        import re
        
        # Vérifier si yt-dlp est disponible
        if not self.downloader.yt_dlp_path:
            self.log("Erreur: yt-dlp n'est pas trouvé. Impossible d'extraire les informations.")
            return []

        is_playlist = self._is_playlist_url(url)
        
        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            cmd = [self.downloader.yt_dlp_path, "--dump-json"]
            if is_playlist:
                cmd.append("--flat-playlist") # Ne télécharge pas, juste extrait la liste des vidéos
            cmd.append(url)

            self.log(f"Extraction des informations pour: {url} (playlist: {is_playlist})...")
            process = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                creationflags=creationflags
            )
            
            output_lines = process.stdout.strip().split('\n')
            extracted_items = []

            for line in output_lines:
                try:
                    data = json.loads(line)
                    title = data.get('title', 'Titre inconnu')
                    video_url = data.get('webpage_url', data.get('url', url)) # Utilise webpage_url ou url
                    
                    # Assurez-vous que duration_seconds est un entier, même si yt-dlp renvoie None
                    duration_seconds = data.get('duration')
                    if duration_seconds is None:
                        duration_seconds = 0 # Valeur par défaut si None est retourné

                    # Convertir la durée en format HH:MM:SS
                    hours = duration_seconds // 3600
                    minutes = (duration_seconds % 3600) // 60
                    seconds = duration_seconds % 60
                    duration_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"
                    
                    extracted_items.append({
                        "title": title,
                        "url": video_url,
                        "duration": duration_formatted
                    })
                except json.JSONDecodeError:
                    self.log(f"Avertissement: Ligne non-JSON reçue de yt-dlp: {line[:100]}...") # Log partiel
                    continue
            
            if not extracted_items:
                self.log(f"Aucune information extraite pour l'URL: {url}. Sortie brute: {process.stdout.strip()}")
                return []
            
            self.log(f"Informations extraites pour {len(extracted_items)} élément(s) depuis {url}.")
            return extracted_items

        except FileNotFoundError:
            self.log("Erreur: yt-dlp n'est pas trouvé. Impossible d'extraire les informations.")
            return []
        except subprocess.CalledProcessError as e:
            self.log(f"Erreur lors de l'exécution de yt-dlp pour extraire les infos: {e.stderr}")
            self.log(f"Commande exécutée: {' '.join(cmd)}")
            return []
        except Exception as e:
            self.log(f"Erreur inattendue lors de l'extraction des informations: {e}")
            return []

    def _is_playlist_url(self, url: str) -> bool:
        """Vérifie si l'URL est une URL de playlist YouTube."""
        playlist_patterns = [
            r'https?://(www\.)?youtube\.com/playlist\?list=',
            r'https?://(www\.)?youtube\.com/watch\?.*&list=',
            r'https?://music\.youtube\.com/playlist\?list=',
        ]
        import re
        for pattern in playlist_patterns:
            if re.match(pattern, url):
                return True
        return False


    def add_url_to_memory(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Ajouter à la Mémoire", "Veuillez entrer une URL.")
            return

        if not self._validate_youtube_url(url):
            messagebox.showwarning("URL Invalide", "L'URL fournie n'est pas une URL YouTube/YouTube Music valide.")
            return

        self.log(f"Tentative d'extraction des informations pour: {url}")
        threading.Thread(target=self._add_url_to_memory_task, args=(url,)).start()

    def _add_url_to_memory_task(self, url: str):
        try:
            # Cette méthode retourne maintenant une liste
            extracted_items = self._extract_video_info_from_url(url)
            
            if not extracted_items:
                self.log(f"Impossible d'obtenir des informations valides pour l'URL: {url}. Non ajouté.")
                self.root.after(0, lambda: messagebox.showerror("Erreur d'extraction", "Impossible d'extraire les informations de la vidéo/playlist pour l'URL fournie. Veuillez vérifier l'URL ou votre connexion Internet."))
                return

            added_count = 0
            for info in extracted_items:
                if self.memory.add_item(info["title"], info["url"], info["duration"]):
                    self.log(f"Ajouté à la mémoire: {info['title']}")
                    added_count += 1
                else:
                    self.log(f"Échec de l'ajout à la mémoire (peut-être déjà présent): {info['title']}")
            
            self.root.after(0, self.update_memory_display)
            self.root.after(0, lambda: messagebox.showinfo("Ajouter à la Mémoire", f"{added_count} élément(s) ajouté(s) à la mémoire."))

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
        
        if (selected_format in ["mp3", "wav", "flac", "m4a", "opus"]) and not self.downloader.ffmpeg_path:
            messagebox.showwarning("FFmpeg introuvable", "FFmpeg n'est pas configuré. Impossible de convertir en MP3/WAV/FLAC/M4A/OPUS. Veuillez l'installer via le menu Aide.")
            return

        self.log(f"Préparation du téléchargement de l'URL: {url} au format {selected_format}...")
        
        # Lancer l'extraction d'informations en arrière-plan
        threading.Thread(target=self._queue_download_from_url_task, args=(url, selected_format)).start()
        self.notebook.select(1) # Sélectionner l'onglet "Téléchargements"

    def _queue_download_from_url_task(self, url: str, selected_format: str):
        """Tâche asynchrone pour extraire les infos et ajouter à la file d'attente."""
        try:
            extracted_items = self._extract_video_info_from_url(url)
            if not extracted_items:
                self.root.after(0, lambda: messagebox.showerror("Erreur d'extraction", "Impossible d'extraire les informations de la vidéo/playlist pour l'URL fournie. Le téléchargement ne peut pas démarrer."))
                return

            for item_info in extracted_items:
                download_id = str(uuid.uuid4())
                self.add_download_to_queue({
                    "id": download_id,
                    "title": item_info['title'],
                    "url": item_info['url'],
                    "format": selected_format,
                    "status": "En attente",
                    "progress": 0
                })
        except Exception as e:
            self.log(f"Erreur lors de la mise en file d'attente de l'URL: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", f"Une erreur est survenue lors de la préparation du téléchargement: {e}"))


    def add_selected_to_memory(self):
        selected_items = self.results_tree.selection()
        if not selected_items:
            messagebox.showwarning("Ajouter à la Mémoire", "Veuillez sélectionner au moins un élément dans les résultats de recherche.")
            return

        success_count = 0
        for item_id in selected_items:
            item_values = self.results_tree.item(item_id, 'values')
            selected_result_index = int(item_values[0]) - 1
            
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
        selected_items_ids = self.results_tree.selection()
        if not selected_items_ids:
            messagebox.showwarning("Téléchargement", "Veuillez sélectionner au moins un élément dans les résultats de recherche.")
            return

        selected_format = self.download_format_var.get().lower()

        if not self.downloader.yt_dlp_path:
            messagebox.showwarning("yt-dlp introuvable", "yt-dlp n'est pas configuré. Impossible de télécharger. Veuillez l'installer via le menu Aide.")
            return
        
        if (selected_format in ["mp3", "wav", "flac", "m4a", "opus"]) and not self.downloader.ffmpeg_path:
            messagebox.showwarning("FFmpeg introuvable", "FFmpeg n'est pas configuré. Impossible de convertir en MP3/WAV/FLAC/M4A/OPUS. Veuillez l'installer via le menu Aide.")
            return

        self.log(f"Préparation du téléchargement de {len(selected_items_ids)} éléments sélectionnés...")
        for item_id in selected_items_ids:
            item_values = self.results_tree.item(item_id, 'values')
            selected_result_index = int(item_values[0]) - 1
            if 0 <= selected_result_index < len(self.search_results):
                item_data = self.search_results[selected_result_index]
                download_id = str(uuid.uuid4())
                self.add_download_to_queue({
                    "id": download_id,
                    "title": item_data['title'],
                    "url": item_data['url'],
                    "format": selected_format,
                    "status": "En attente",
                    "progress": 0
                })
        self.notebook.select(1) # Sélectionner l'onglet "Téléchargements"


    def remove_selected_from_memory(self):
        selected_items = self.memory_tree.selection()
        if not selected_items:
            messagebox.showwarning("Supprimer de la Mémoire", "Veuillez sélectionner au moins un élément à supprimer.")
            return

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
        memory_items = self.memory.get_memory()
        if not memory_items:
            messagebox.showwarning("Téléchargement", "La mémoire est vide. Aucun élément à télécharger.")
            return

        selected_format = self.download_format_var.get().lower()

        if not self.downloader.yt_dlp_path:
            messagebox.showwarning("yt-dlp introuvable", "yt-dlp n'est pas configuré. Impossible de télécharger. Veuillez l'installer via le menu Aide.")
            return
        
        if (selected_format in ["mp3", "wav", "flac", "m4a", "opus"]) and not self.downloader.ffmpeg_path:
            messagebox.showwarning("FFmpeg introuvable", "FFmpeg n'est pas configuré. Impossible de convertir en MP3/WAV/FLAC/M4A/OPUS. Veuillez l'installer via le menu Aide.")
            return

        self.log(f"Préparation du téléchargement de tous les {len(memory_items)} éléments de la mémoire...")
        for item in memory_items:
            download_id = str(uuid.uuid4())
            self.add_download_to_queue({
                "id": download_id,
                "title": item['title'],
                "url": item['url'],
                "format": selected_format,
                "status": "En attente",
                "progress": 0
            })
        self.notebook.select(1) # Sélectionner l'onglet "Téléchargements"

    def add_download_to_queue(self, download_info: dict):
        """Ajoute un téléchargement à la file d'attente et crée sa carte d'affichage."""
        self.download_queue.put(download_info)
        self.downloads_list.append(download_info) # Ajouter à la liste globale pour suivi
        self.root.after(0, lambda: self._create_download_card(download_info))
        self.log(f"Ajouté à la file d'attente: {download_info['title']} (ID: {download_info['id']})")
        self.pending_downloads_count_var.set(self.pending_downloads_count_var.get() + 1) # Incrémenter le compteur "en attente"
        self.root.after(100, self._start_next_download_if_possible) # Tenter de démarrer immédiatement

    def _create_download_card(self, download_info: dict):
        """Crée les widgets Tkinter pour une nouvelle carte de téléchargement."""
        download_id = download_info['id']
        title = download_info['title']
        status = download_info['status']
        progress = download_info['progress']

        card_frame = ttk.Frame(self.downloads_container_frame, style='DownloadCard.TFrame')
        card_frame.pack(fill='x', padx=5, pady=5)

        title_label = ttk.Label(card_frame, text=title, style='DownloadTitle.TLabel', wraplength=300)
        title_label.pack(fill='x', anchor='w', pady=(0, 5))

        status_label = ttk.Label(card_frame, text=f"Statut: {status}", style='DownloadStatus.TLabel')
        status_label.pack(fill='x', anchor='w', pady=(0, 5))

        progressbar = ttk.Progressbar(card_frame, orient="horizontal", length=200, mode="determinate", style="TProgressbar")
        progressbar.pack(fill='x', pady=(0, 5))
        progressbar.config(value=progress)

        cancel_button = ttk.Button(card_frame, text="Annuler", style='Danger.TButton',
                                   command=lambda: self.cancel_download(download_id))
        cancel_button.pack(side='right', pady=(0, 0))

        self.download_widgets[download_id] = {
            'card_frame': card_frame,
            'title_label': title_label,
            'status_label': status_label,
            'progressbar': progressbar,
            'cancel_button': cancel_button
        }
        self.downloads_container_frame.update_idletasks()
        self.downloads_canvas.config(scrollregion=self.downloads_canvas.bbox("all"))

    def _start_next_download_if_possible(self):
        """Démarre le prochain téléchargement de la file d'attente si la limite n'est pas atteinte."""
        with self.download_lock:
            if self.active_download_count < self.concurrent_limit and not self.download_queue.empty():
                try:
                    download_info = self.download_queue.get_nowait() # Récupère sans bloquer
                    # Vérifier si le téléchargement n'a pas été annulé pendant qu'il était en attente
                    if download_info['status'] == "cancelled":
                        self.log(f"Téléchargement {download_info['title']} (ID: {download_info['id']}) a été annulé avant de commencer.")
                        self.root.after(0, lambda: self._update_download_card_widgets(self.download_widgets[download_info['id']], download_info))
                        # Le compteur failed_downloads_count_var est déjà mis à jour dans cancel_download si annulé depuis "En attente"
                        # Ou il sera mis à jour par update_download_progress si le statut final est "cancelled"
                        # Décrémenter le compteur "en attente" car il ne l'est plus
                        self.pending_downloads_count_var.set(self.pending_downloads_count_var.get() - 1)
                        self._start_next_download_if_possible() # Tenter le suivant
                        return

                    self.active_download_count += 1
                    self.active_downloads_count_var.set(self.active_download_count) # Mettre à jour le compteur Tkinter
                    self.pending_downloads_count_var.set(self.pending_downloads_count_var.get() - 1) # Décrémenter le compteur "en attente"

                    self.log(f"Démarrage du téléchargement: {download_info['title']} (Actifs: {self.active_download_count}/{self.concurrent_limit})")
                    # Mettre à jour le statut de la carte immédiatement
                    self.root.after(0, lambda: self._update_download_card_widgets(
                        self.download_widgets[download_info['id']], 
                        {**download_info, 'status': 'active', 'message': 'Démarrage...'} # Utiliser 'active' pour correspondre au downloader
                    ))
                    # Lancer le téléchargement dans un thread séparé
                    threading.Thread(target=lambda: self.downloader._download_single_item(
                        download_info['url'], 
                        download_info['format'], 
                        download_info['id']
                    )).start()
                except queue.Empty:
                    pass # La queue était vide, rien à faire
            else:
                self.log(f"File d'attente pleine ou limite atteinte. Actifs: {self.active_download_count}/{self.concurrent_limit}, En attente: {self.download_queue.qsize()}")


    def update_download_progress(self, download_id: str, status: str, progress: float, message: str = ""):
        """
        Met à jour la progression d'un téléchargement dans la liste et son widget.
        Appelé par le Downloader.
        """
        # Trouver l'info de téléchargement dans la liste
        dl_info = next((dl for dl in self.downloads_list if dl['id'] == download_id), None)
        if dl_info:
            # Sauvegarder l'ancien statut pour la logique de décrémentation
            old_status = dl_info['status'] 
            dl_info['status'] = status
            dl_info['progress'] = progress
            dl_info['message'] = message # Stocker le message de progression détaillé

            # Mettre à jour les compteurs si le statut final est atteint
            if status in ["completed", "failed", "cancelled"] and old_status not in ["completed", "failed", "cancelled"]:
                with self.download_lock:
                    self.active_download_count -= 1
                    self.active_downloads_count_var.set(self.active_downloads_count) # Décrémenter le compteur Tkinter actif
                    self.log(f"Téléchargement {download_id} terminé/annulé/échoué. Actifs restants: {self.active_download_count}")
                
                if status == "completed":
                    self.completed_downloads_count_var.set(self.completed_downloads_count_var.get() + 1)
                elif status in ["failed", "cancelled"]: # Regrouper les échecs et annulations
                    self.failed_downloads_count_var.set(self.failed_downloads_count_var.get() + 1)

                self.root.after(100, self._start_next_download_if_possible) # Tenter de démarrer le suivant

        # Mettre à jour les widgets correspondants
        if download_id in self.download_widgets:
            widgets = self.download_widgets[download_id]
            self.root.after(0, lambda: self._update_download_card_widgets(widgets, dl_info))

    def _update_download_card_widgets(self, widgets: dict, dl_info: dict):
        """Met à jour les widgets d'une carte de téléchargement spécifique."""
        status_text = f"Statut: {dl_info['status']}"
        if dl_info['status'] == "active":
            status_text = f"Statut: Actif ({dl_info['progress']:.1f}%)"
            widgets['progressbar'].config(value=dl_info['progress'])
            widgets['cancel_button'].config(state='normal') # Activer le bouton Annuler
        elif dl_info['status'] == "En attente":
            status_text = f"Statut: En attente"
            widgets['progressbar'].config(value=0)
            widgets['cancel_button'].config(state='normal')
        elif dl_info['status'] == "completed":
            status_text = f"Statut: Terminé ({dl_info['message']})"
            widgets['progressbar'].config(value=100)
            widgets['cancel_button'].config(state='disabled') # Désactiver le bouton Annuler après la fin
            widgets['progressbar'].stop() # Arrêter l'animation si elle était en mode indéterminé
        elif dl_info['status'] == "failed":
            status_text = f"Statut: Échec ({dl_info['message']})"
            widgets['progressbar'].config(value=0) # Réinitialiser la barre ou la vider
            widgets['cancel_button'].config(state='disabled')
            widgets['progressbar'].stop()
        elif dl_info['status'] == "cancelled":
            status_text = f"Statut: Annulé ({dl_info['message']})"
            widgets['progressbar'].config(value=0)
            widgets['cancel_button'].config(state='disabled')
            widgets['progressbar'].stop()

        widgets['status_label'].config(text=status_text)
        
        # Mettre à jour la couleur du statut
        if dl_info['status'] == "active":
            widgets['status_label'].config(foreground="blue")
        elif dl_info['status'] == "completed":
            widgets['status_label'].config(foreground="green")
        elif dl_info['status'] == "failed":
            widgets['status_label'].config(foreground="red")
        elif dl_info['status'] == "cancelled":
            widgets['status_label'].config(foreground="orange")
        elif dl_info['status'] == "En attente":
            widgets['status_label'].config(foreground=self.root.tk.eval('ttk::style lookup DownloadStatus.TLabel -foreground')) # Couleur par défaut ou gris
        else:
            widgets['status_label'].config(foreground=self.root.tk.eval('ttk::style lookup DownloadStatus.TLabel -foreground')) # Couleur par défaut

        # Mettre à jour la région de défilement du canvas après la mise à jour des widgets
        self.downloads_container_frame.update_idletasks()
        self.downloads_canvas.config(scrollregion=self.downloads_canvas.bbox("all"))


    def cancel_download(self, download_id: str):
        """Annule un téléchargement spécifique."""
        dl_to_cancel = next((dl for dl in self.downloads_list if dl['id'] == download_id), None)
        if dl_to_cancel:
            if dl_to_cancel['status'] == "active":
                if messagebox.askyesno("Confirmer Annulation", f"Êtes-vous sûr de vouloir annuler le téléchargement de '{dl_to_cancel['title']}' ?"):
                    self.downloader.cancel_download(download_id)
                    # Le progress_callback mettra à jour le statut à "cancelled"
            elif dl_to_cancel['status'] == "En attente":
                # Si en attente, on le marque comme annulé et on met à jour son statut
                if messagebox.askyesno("Confirmer Annulation", f"Êtes-vous sûr de vouloir annuler le téléchargement en attente de '{dl_to_cancel['title']}' ?"):
                    dl_to_cancel['status'] = "cancelled"
                    dl_to_cancel['message'] = "Annulé (en attente)"
                    self.root.after(0, lambda: self._update_download_card_widgets(self.download_widgets[download_id], dl_to_cancel))
                    self.log(f"Téléchargement en attente {dl_to_cancel['title']} annulé.")
                    # Mettre à jour le compteur d'échecs/annulations et décrémenter "en attente"
                    self.failed_downloads_count_var.set(self.failed_downloads_count_var.get() + 1)
                    self.pending_downloads_count_var.set(self.pending_downloads_count_var.get() - 1)
                    # Tenter de démarrer le prochain téléchargement si un slot se libère (bien que ce ne soit pas un slot "actif")
                    self.root.after(100, self._start_next_download_if_possible)
            else:
                messagebox.showinfo("Annuler Téléchargement", f"Le téléchargement de '{dl_to_cancel['title']}' n'est pas actif ou en attente et ne peut pas être annulé.")
        else:
            self.log(f"Erreur: Téléchargement non trouvé pour l'ID {download_id}.")


    def set_concurrent_downloads_limit_dialog(self):
        """Ouvre une boîte de dialogue pour définir la limite de téléchargements simultanés."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Limite de Téléchargements")
        dialog.geometry("300x150")
        dialog.configure(bg='#2b2b2b')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        current_limit = self.config.get_concurrent_downloads_limit()
        limit_var = tk.IntVar(value=current_limit)

        ttk.Label(dialog, text="Nombre de téléchargements simultanés (1-15):",
                  style='Custom.TLabel', background='#2b2b2b').pack(pady=10)

        limit_spinbox = ttk.Spinbox(dialog, from_=1, to=15, textvariable=limit_var,
                                    width=5, font=('Arial', 10), style='TEntry')
        limit_spinbox.pack(pady=5)

        def save_limit():
            try:
                new_limit = limit_var.get()
                self.config.set_concurrent_downloads_limit(new_limit)
                self.concurrent_limit = new_limit # Mettre à jour la limite interne
                self.log(f"Limite de téléchargements simultanés définie sur: {new_limit}")
                messagebox.showinfo("Configuration", f"Limite définie sur {new_limit}.")
                dialog.destroy()
                self.root.after(100, self._start_next_download_if_possible) # Tenter de démarrer de nouveaux téléchargements avec la nouvelle limite
            except tk.TclError:
                messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")

        save_btn = ttk.Button(dialog, text="Sauvegarder", command=save_limit, style='Accent.TButton')
        save_btn.pack(pady=10)

        dialog.wait_window(dialog)


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
                    webbrowser.open("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe")
                    messagebox.showinfo("Téléchargement yt-dlp", "Le téléchargement de yt-dlp.exe devrait commencer dans votre navigateur. Placez le fichier téléchargé dans le même dossier que l'exécutable de cette application.")
                    self.log("Ouverture du lien de téléchargement de yt-dlp.exe.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible d'ouvrir le navigateur : {e}")
            else:
                webbrowser.open("https://github.com/yt-dlp/yt-dlp#installation")
                messagebox.showinfo("Installation yt-dlp", "La page d'installation de yt-dlp s'est ouverte dans votre navigateur. Suivez les instructions pour votre système.")
                self.log("Ouverture de la page d'installation de yt-dlp.")
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
        self.root.after(1000, self.check_ffmpeg_status)


    def check_and_offer_yt_dlp_install(self):
        """Vérifie yt-dlp au démarrage et propose l'installation si non trouvé."""
        if not self.downloader.find_yt_dlp_location():
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

    def on_multiple_download_complete(self, success_count: int, total_count: int):
        """Callback après un téléchargement multiple."""
        self.log(f"Téléchargement multiple terminé: {success_count} sur {total_count} réussis.")
        if success_count == total_count:
            self.root.after(0, lambda: messagebox.showinfo("Téléchargement Terminé", f"Tous les {total_count} éléments ont été téléchargés avec succès!"))
        elif success_count > 0:
            self.root.after(0, lambda: messagebox.showwarning("Téléchargement Partiel", f"{success_count} sur {total_count} éléments ont été téléchargés. Voir les logs pour les détails."))
        else:
            self.root.after(0, lambda: messagebox.showerror("Échec du Téléchargement", "Aucun élément n'a pu être téléchargé. Voir les logs pour les détails."))

    def run(self):
        """Lancer l'application."""
        self.root.mainloop()

