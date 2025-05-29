# gui_elements.py
import tkinter as tk
from tkinter import ttk, scrolledtext

def create_search_frame(parent_frame, search_entry_ref, perform_search_cmd):
    search_frame = ttk.LabelFrame(parent_frame, text="Recherche YouTube", style='Custom.TLabelframe',
                                  padding=(15, 10, 15, 15))
    search_frame.pack(fill='x', pady=(0, 10), padx=10)

    ttk.Label(search_frame, text="Rechercher:", style='Custom.TLabel').pack(pady=(0, 5), anchor='w')
    search_entry = ttk.Entry(search_frame, width=50, style='TEntry')
    search_entry.pack(fill='x', pady=(0, 10))
    search_entry.bind('<Return>', lambda e: perform_search_cmd())

    search_btn = ttk.Button(search_frame, text="Rechercher", command=perform_search_cmd,
                            style='Accent.TButton')
    search_btn.pack(pady=(0, 0), side='right')

    # Passer la référence à search_entry au lieu de créer une variable Tkinter ici
    search_entry_ref['widget'] = search_entry # Utilisez un dictionnaire pour passer la référence

    return search_entry

def create_url_download_frame(parent_frame, download_format_var, download_url_cmd, add_url_to_memory_cmd, url_entry_ref):
    url_frame = ttk.LabelFrame(parent_frame, text="Téléchargement Direct", style='Custom.TLabelframe',
                               padding=(15, 10, 15, 15))
    url_frame.pack(fill='x', pady=(0, 10), padx=10)

    ttk.Label(url_frame, text="URL YouTube:", style='Custom.TLabel').pack(pady=(0, 5), anchor='w')
    url_entry = ttk.Entry(url_frame, width=50, style='TEntry')
    url_entry.pack(fill='x', pady=(0, 10))
    url_entry.bind('<Return>', lambda e: download_url_cmd())

    url_btn_frame = ttk.Frame(url_frame, style='Custom.TFrame')
    url_btn_frame.pack(fill='x')

    format_selector_url_frame = ttk.Frame(url_btn_frame, style='Custom.TFrame')
    format_selector_url_frame.pack(side='left', padx=(0, 15))

    ttk.Label(format_selector_url_frame, text="Format:", style='Custom.TLabel').pack(side='left', padx=(0, 5))
    format_combobox_url = ttk.Combobox(format_selector_url_frame,
                                       textvariable=download_format_var,
                                       values=["MP3", "MP4"],
                                       state="readonly", width=5, style='TCombobox')
    format_combobox_url.pack(side='left')
    format_combobox_url.set("MP4")

    download_url_btn = ttk.Button(url_btn_frame, text="Télécharger",
                                 command=download_url_cmd, style='Accent.TButton')
    download_url_btn.pack(side='right')

    add_url_to_memory_btn = ttk.Button(url_btn_frame, text="Ajouter à la Mémoire",
                                      command=add_url_to_memory_cmd, style='Custom.TButton')
    add_url_to_memory_btn.pack(side='right', padx=(0, 10))

    url_entry_ref['widget'] = url_entry # Passer la référence

    return url_entry, format_combobox_url, download_url_btn, add_url_to_memory_btn

def create_results_frame(parent_frame, download_format_var, add_to_memory_cmd, download_selected_cmd):
    results_frame = ttk.LabelFrame(parent_frame, text="Résultats de Recherche", style='Custom.TLabelframe',
                                   padding=(15, 10, 15, 15))
    results_frame.pack(fill='both', expand=True, pady=10, padx=10)

    results_tree = ttk.Treeview(results_frame, columns=("ID", "Titre", "Durée"), show="headings", style='Treeview')
    results_tree.heading("ID", text="ID", anchor=tk.CENTER)
    results_tree.heading("Titre", text="Titre", anchor=tk.W)
    results_tree.heading("Durée", text="Durée", anchor=tk.CENTER)

    results_tree.column("ID", width=30, minwidth=30, anchor=tk.CENTER, stretch=False)
    results_tree.column("Titre", width=300, minwidth=150, anchor=tk.W)
    results_tree.column("Durée", width=80, minwidth=80, anchor=tk.CENTER, stretch=False)

    results_tree.pack(side='left', fill='both', expand=True, padx=(0, 5), pady=(0, 5))

    results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview, style='Vertical.TScrollbar')
    results_scrollbar.pack(side='right', fill='y', padx=(0, 0), pady=(0, 5))
    results_tree.configure(yscrollcommand=results_scrollbar.set)

    results_btn_frame = ttk.Frame(parent_frame, style='Custom.TFrame')
    results_btn_frame.pack(fill='x', pady=5, padx=10)

    add_to_memory_btn = ttk.Button(results_btn_frame, text="Ajouter à la Mémoire",
                                   command=add_to_memory_cmd, style='Custom.TButton')
    add_to_memory_btn.pack(side='left', padx=(0, 5))

    format_selector_results_frame = ttk.Frame(results_btn_frame, style='Custom.TFrame')
    format_selector_results_frame.pack(side='left', padx=(5, 15))

    ttk.Label(format_selector_results_frame, text="Format:", style='Custom.TLabel').pack(side='left', padx=(0, 5))
    format_combobox_results = ttk.Combobox(format_selector_results_frame,
                                         textvariable=download_format_var,
                                         values=["MP3", "MP4"],
                                         state="readonly", width=5, style='TCombobox')
    format_combobox_results.pack(side='left')
    format_combobox_results.set("MP4")

    download_selected_btn = ttk.Button(results_btn_frame, text="Télécharger Sélection",
                                       command=download_selected_cmd, style='Accent.TButton')
    download_selected_btn.pack(side='right', padx=(5, 0))

    return results_tree, format_combobox_results

def create_memory_frame(parent_frame, download_format_var, download_all_cmd, remove_selected_cmd, clear_all_cmd):
    memory_frame = ttk.LabelFrame(parent_frame, text="Mémoire (Playlist)", style='Custom.TLabelframe',
                                  padding=(15, 10, 15, 15))
    memory_frame.pack(fill='x', pady=(0, 10), padx=10)

    memory_tree = ttk.Treeview(memory_frame, columns=("ID", "Titre", "Durée"), show="headings", style='Treeview')
    memory_tree.heading("ID", text="ID", anchor=tk.CENTER)
    memory_tree.heading("Titre", text="Titre", anchor=tk.W)
    memory_tree.heading("Durée", text="Durée", anchor=tk.CENTER)

    memory_tree.column("ID", width=30, minwidth=30, anchor=tk.CENTER, stretch=False)
    memory_tree.column("Titre", width=300, minwidth=150, anchor=tk.W)
    memory_tree.column("Durée", width=80, minwidth=80, anchor=tk.CENTER, stretch=False)

    memory_tree.pack(side='left', fill='x', expand=True, padx=(0, 5), pady=(0, 5))

    memory_scrollbar = ttk.Scrollbar(memory_frame, orient="vertical", command=memory_tree.yview, style='Vertical.TScrollbar')
    memory_scrollbar.pack(side='right', fill='y', padx=(0, 0), pady=(0, 5))
    memory_tree.configure(yscrollcommand=memory_scrollbar.set)

    memory_btn_frame = ttk.Frame(parent_frame, style='Custom.TFrame')
    memory_btn_frame.pack(fill='x', pady=5, padx=10)

    format_selector_memory_frame = ttk.Frame(memory_btn_frame, style='Custom.TFrame')
    format_selector_memory_frame.pack(side='left', padx=(0, 15))

    ttk.Label(format_selector_memory_frame, text="Format:", style='Custom.TLabel').pack(side='left', padx=(0, 5))
    format_combobox_memory = ttk.Combobox(format_selector_memory_frame,
                                         textvariable=download_format_var,
                                         values=["MP3", "MP4"],
                                         state="readonly", width=5, style='TCombobox')
    format_combobox_memory.pack(side='left')
    format_combobox_memory.set("MP4")

    download_memory_btn = ttk.Button(memory_btn_frame, text="Télécharger Tout",
                                     command=download_all_cmd, style='Accent.TButton')
    download_memory_btn.pack(side='left', expand=True, padx=(5, 5))

    remove_from_memory_btn = ttk.Button(memory_btn_frame, text="Supprimer Sélection",
                                        command=remove_selected_cmd, style='Danger.TButton')
    remove_from_memory_btn.pack(side='right', padx=(5, 0))

    clear_memory_btn = ttk.Button(memory_btn_frame, text="Vider la Mémoire",
                                  command=clear_all_cmd, style='Danger.TButton')
    clear_memory_btn.pack(side='right', padx=(5, 5))

    return memory_tree, format_combobox_memory

def create_log_frame(parent_frame):
    log_frame = ttk.LabelFrame(parent_frame, text="Logs", style='Custom.TLabelframe',
                               padding=(15, 10, 15, 15))
    log_frame.pack(fill='both', expand=True, pady=10, padx=10)

    log_display = scrolledtext.ScrolledText(log_frame, wrap='word', height=10,
                                             bg='#4c4c4c', fg='white', font=('Consolas', 9),
                                             state='disabled', relief='flat', borderwidth=0)
    log_display.pack(fill='both', expand=True, padx=5, pady=5)

    return log_display

def create_menubar(root, set_download_folder_cmd, quit_cmd, configure_api_key_cmd,
                   check_google_api_client_cmd, check_yt_dlp_cmd, install_yt_dlp_cmd,
                   check_ffmpeg_status_cmd, offer_ffmpeg_install_cmd):
    menubar = tk.Menu(root, bg='#3c3c3c', fg='white', relief='flat', borderwidth=0)

    file_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white',
                         activebackground='#007bff', activeforeground='white')
    menubar.add_cascade(label="Fichier", menu=file_menu)
    file_menu.add_command(label="Définir le dossier de téléchargement", command=set_download_folder_cmd)
    file_menu.add_separator(background='#2b2b2b')
    file_menu.add_command(label="Quitter", command=quit_cmd)

    config_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white',
                           activebackground='#007bff', activeforeground='white')
    menubar.add_cascade(label="Configuration", menu=config_menu)
    config_menu.add_command(label="Configurer la clé API YouTube", command=configure_api_key_cmd)

    help_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white',
                         activebackground='#007bff', activeforeground='white')
    menubar.add_cascade(label="Aide", menu=help_menu)
    help_menu.add_command(label="Vérifier Google API Client", command=check_google_api_client_cmd)
    help_menu.add_command(label="Vérifier yt-dlp", command=check_yt_dlp_cmd)
    help_menu.add_command(label="Installer yt-dlp", command=install_yt_dlp_cmd)
    help_menu.add_separator(background='#2b2b2b')
    help_menu.add_command(label="Vérifier FFmpeg", command=check_ffmpeg_status_cmd)
    help_menu.add_command(label="Installer FFmpeg", command=offer_ffmpeg_install_cmd)

    return menubar