# MusicDL - Téléchargeur de Musique et Vidéos YouTube

MusicDL est une application de bureau conçue pour faciliter la recherche et le téléchargement de musique et de vidéos depuis YouTube. Elle offre une interface graphique intuitive, des fonctionnalités de recherche via l'API YouTube, un gestionnaire de file d'attente, et la possibilité de gérer une "mémoire" de liens pour des téléchargements en masse.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Lancement de l'application](#lancement-de-lapplication)
- [Utilisation](#utilisation)
  - [Interface principale](#interface-principale)
  - [Recherche et Téléchargement](#recherche-et-téléchargement)
  - [Gestion de la mémoire](#gestion-de-la-mémoire)
  - [File d'attente des téléchargements](#file-dattente-des-téléchargements)
- [Configuration](#configuration)
- [Structure du projet](#structure-du-projet)
- [Contribuer](#contribuer)
- [Licence](#licence)

## Fonctionnalités

- **Installation Automatique des Dépendances** : L'application vérifie et installe automatiquement les paquets nécessaires au démarrage.
- **Recherche YouTube Intégrée** : Trouvez des vidéos directement depuis l'application avec l'API YouTube Data v3.
- **Téléchargement Polyvalent** : Téléchargez des vidéos complètes ou extrayez l'audio dans une multitude de formats (MP3, MP4, WAV, FLAC, etc.).
- **Gestionnaire de File d'Attente** : Ajoutez plusieurs téléchargements qui seront traités séquentiellement avec une limite de téléchargements simultanés configurable.
- **Gestion de la Mémoire** : Sauvegardez une liste de liens pour les télécharger plus tard.
- **Interface Graphique (GUI)** : Basée sur tkinter pour une expérience utilisateur simple et interactive.
- **Configuration Persistante** : Sauvegarde votre chemin de téléchargement, clé API et limite de téléchargements.

## Prérequis

Assurez-vous d'avoir Python 3 installé sur votre système. Vous pouvez le télécharger depuis [python.org](https://python.org).

## Lancement de l'application

Pour lancer MusicDL, exécutez simplement le fichier `Youtube Downloader.bat`.

Au premier lancement, le script installera automatiquement les bibliothèques nécessaires si elles ne sont pas déjà présentes.

### Clé API YouTube (Recommandé)

Pour utiliser la fonctionnalité de recherche, une clé API YouTube Data v3 est nécessaire.

1. Rendez-vous sur la [console Google Cloud](https://console.cloud.google.com/).
2. Créez un projet et activez l'API YouTube Data API v3.
3. Créez une "Clé API" (API Key).
4. Copiez votre clé et collez-la dans l'application via le menu **Configuration > Configurer la clé API YouTube**.

**Sans clé API, seule la fonctionnalité de téléchargement par URL directe sera disponible.**

## Utilisation

### Interface principale

L'interface est divisée en deux panneaux principaux :

- **Panneau de Gauche** : Recherche, téléchargement par URL et résultats de recherche.
- **Panneau de Droite** : Mémoire (playlist), file d'attente des téléchargements et logs.

### Recherche et Téléchargement

- **Rechercher** : Entrez un nom d'artiste ou de chanson dans la barre de recherche et cliquez sur "Rechercher". Les résultats s'afficheront en dessous.
- **Télécharger par URL** : Collez une URL de vidéo ou de playlist YouTube dans le champ "URL YouTube" et cliquez sur "Télécharger".
- **Télécharger depuis les résultats** : Sélectionnez un ou plusieurs éléments dans la liste des résultats, choisissez un format, puis cliquez sur "Télécharger Sélection".

Tous les téléchargements sont ajoutés à la file d'attente dans l'onglet "Téléchargements".

### Gestion de la mémoire

- **Ajouter** : Sélectionnez des éléments dans les résultats de recherche et cliquez sur "Ajouter à la Mémoire".
- **Télécharger** : Allez dans la section "Mémoire", choisissez un format, et cliquez sur "Télécharger Tout".
- **Supprimer** : Sélectionnez des éléments dans la mémoire et utilisez les boutons "Supprimer Sélection" ou "Vider la Mémoire".

### File d'attente des téléchargements

L'onglet "Téléchargements" dans le panneau de droite affiche tous les téléchargements en attente, en cours, terminés ou échoués. Vous pouvez y suivre la progression et annuler des téléchargements.

## Configuration

Le menu "Configuration" permet de :

- Définir le dossier de téléchargement.
- Configurer la clé API YouTube.
- Définir la limite de téléchargements simultanés.

## Structure du projet

- `main.py` : Point d'entrée, gère l'installation des dépendances.
- `main_gui.py` : Cœur de l'application, gère l'interface et la logique principale.
- `config_manager.py` : Gère la configuration (clé API, chemins).
- `youtube_api.py` : Gère les interactions avec l'API YouTube.
- `downloader.py` : Encapsule la logique de téléchargement avec yt-dlp.
- `memory_manager.py` : Gère la sauvegarde et le chargement de la mémoire.
- `dialogs.py` : Contient les boîtes de dialogue personnalisées.
- `README.md` : Ce fichier de documentation.

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à forker le dépôt et à proposer des pull requests pour de nouvelles fonctionnalités ou des corrections de bugs.

## Licence

Ce projet est sous licence MIT.