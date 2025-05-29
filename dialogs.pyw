import tkinter as tk
from tkinter import messagebox

class APIKeyDialog:
    def __init__(self, parent, current_key=""):
        self.result = None
        
        # Créer la fenêtre de dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuration de la clé API YouTube")
        self.dialog.geometry("500x300")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.resizable(False, False)
        
        # Centrer la fenêtre
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Titre
        title_label = tk.Label(main_frame, text="Configuration de la clé API YouTube", 
                              font=('Arial', 14, 'bold'), bg='#2b2b2b', fg='white')
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = """Pour utiliser la recherche YouTube, vous devez obtenir une clé API :

1. Allez sur https://console.developers.google.com
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API YouTube Data API v3
4. Créez des identifiants (clé API)
5. Copiez votre clé API ci-dessous"""
        
        instructions_label = tk.Label(main_frame, text=instructions, 
                                     font=('Arial', 9), bg='#2b2b2b', fg='#cccccc',
                                     justify='left', wraplength=450)
        instructions_label.pack(pady=(0, 20))
        
        # Champ de saisie
        tk.Label(main_frame, text="Clé API YouTube:", 
                font=('Arial', 10, 'bold'), bg='#2b2b2b', fg='white').pack(anchor='w')
        
        self.api_entry = tk.Entry(main_frame, font=('Arial', 10), bg='#404040', fg='white',
                                 insertbackground='white', width=60)
        self.api_entry.pack(fill='x', pady=(5, 20))
        
        if current_key:
            self.api_entry.insert(0, current_key)
            
        # Boutons
        btn_frame = tk.Frame(main_frame, bg='#2b2b2b')
        btn_frame.pack(fill='x')
        
        cancel_btn = tk.Button(btn_frame, text="Annuler", command=self.cancel,
                              bg='#606060', fg='white', font=('Arial', 10),
                              relief='flat', padx=20, pady=5)
        cancel_btn.pack(side='right', padx=(10, 0))
        
        save_btn = tk.Button(btn_frame, text="Sauvegarder", command=self.save,
                            bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                            relief='flat', padx=20, pady=5)
        save_btn.pack(side='right')
        
        # Lier Enter à la sauvegarde
        self.api_entry.bind('<Return>', lambda e: self.save())
        self.api_entry.focus()
        
    def save(self):
        """Sauvegarder la clé API"""
        api_key = self.api_entry.get().strip()
        if api_key:
            self.result = api_key
            self.dialog.destroy()
        else:
            messagebox.showwarning("Attention", "Veuillez entrer une clé API valide!")
            
    def cancel(self):
        """Annuler la configuration"""
        self.dialog.destroy()