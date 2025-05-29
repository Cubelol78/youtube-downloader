# styles.py
import tkinter as tk
from tkinter import ttk

def apply_styles(root):
    style = ttk.Style()
    style.theme_use('clam')

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