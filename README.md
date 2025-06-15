# MusicDL - Téléchargeur de Musique et Vidéos YouTube

MusicDL est une application de bureau conçue pour faciliter la recherche et le téléchargement de musique et de vidéos depuis YouTube. Elle offre une interface graphique intuitive, des fonctionnalités de recherche via l'API YouTube, un gestionnaire de file d'attente, et la possibilité de gérer une "mémoire" de liens pour des téléchargements en masse.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
  - [Formats Supportés](#formats-supportés)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Lancement de l'application](#lancement-de-lapplication)
  - [Clé API YouTube](#clé-api-youtube-recommandé)
- [Utilisation](#utilisation)
  - [Interface principale](#interface-principale)
  - [Recherche et Téléchargement](#recherche-et-téléchargement)
  - [Gestion de la mémoire](#gestion-de-la-mémoire)
  - [File d'attente des téléchargements](#file-dattente-des-téléchargements)
- [Configuration](#configuration)
- [Structure du projet](#structure-du-projet)
- [Dépannage](#dépannage)
- [Contribuer](#contribuer)
- [Licence](#licence)

## Fonctionnalités

| Fonctionnalité | Description | Statut |
|----------------|-------------|--------|
| 🔧 **Installation Automatique** | Vérification et installation automatique des dépendances au démarrage | ✅ Disponible |
| 🔍 **Recherche YouTube** | Recherche intégrée via l'API YouTube Data v3 | ✅ Disponible |
| 📥 **Téléchargement Multi-format** | Support des formats MP3, MP4, WAV, FLAC, etc. | ✅ Disponible |
| 📋 **Gestionnaire de File d'Attente** | Téléchargements séquentiels avec limite configurable | ✅ Disponible |
| 💾 **Gestion de la Mémoire** | Sauvegarde de listes de liens pour téléchargement ultérieur | ✅ Disponible |
| 🖥️ **Interface Graphique** | Interface utilisateur basée sur tkinter | ✅ Disponible |
| ⚙️ **Configuration Persistante** | Sauvegarde des paramètres utilisateur | ✅ Disponible |
| 📊 **Suivi des Téléchargements** | Monitoring en temps réel des téléchargements | ✅ Disponible |
| 🎵 **Support Playlist** | Téléchargement de playlists YouTube complètes | ✅ Disponible |

### Formats Supportés

| Type | Formats Disponibles |
|------|-------------------|
| **Audio** | MP3, WAV, FLAC, M4A, OPUS |
| **Vidéo** | MP4, AVI, MKV, WEBM, MOV |

> 📝 **Note** : La sélection de qualité spécifique (résolution/bitrate) n'est pas encore disponible. Seuls les formats de fichiers peuvent être choisis.

## Prérequis

| Composant | Version Minimale | Recommandé | Notes |
|-----------|------------------|------------|-------|
| **Python** | 3.7+ | 3.10+ | Téléchargeable depuis [python.org](https://python.org) |
| **Système d'exploitation** | Windows 10+ | Windows 10+ | Conçu pour Windows, non testé sur autres OS |
| **Espace disque** | 100 MB | 1 GB+ | Pour l'application + téléchargements |
| **Connexion Internet** | Requise | Haut débit | Pour l'API YouTube et téléchargements |

## Installation

### Installation Automatique (Recommandée)

1. Téléchargez le projet
2. Exécutez `Youtube Downloader.bat`
3. L'application installera automatiquement toutes les dépendances nécessaires

> ⚡ **Installation Intelligente** : Toutes les dépendances sont installées automatiquement au premier lancement. Aucun fichier `requirements.txt` n'est nécessaire.

### Installation Manuelle

```bash
# Cloner le dépôt
git clone [URL_DU_DEPOT]
cd MusicDL

# Lancer l'application (les dépendances s'installent automatiquement)
python main.py
```

### Dépendances Principales

Les packages suivants sont installés automatiquement :

| Package | Utilisation |
|---------|-------------|
| `yt-dlp` | Téléchargement YouTube |
| `requests` | API YouTube |
| `tkinter` | Interface graphique (inclus avec Python) |

## Lancement de l'application

Pour lancer MusicDL, exécutez simplement le fichier `Youtube Downloader.bat`.

Au premier lancement, le script installera automatiquement les bibliothèques nécessaires si elles ne sont pas déjà présentes.

### Clé API YouTube (Recommandé)

Pour utiliser la fonctionnalité de recherche, une clé API YouTube Data v3 est nécessaire.

| Étape | Action | Description |
|-------|--------|-------------|
| 1️⃣ | **Accès Console** | Rendez-vous sur la [console Google Cloud](https://console.cloud.google.com/) |
| 2️⃣ | **Création Projet** | Créez un nouveau projet ou sélectionnez un existant |
| 3️⃣ | **Activation API** | Activez l'API YouTube Data API v3 |
| 4️⃣ | **Génération Clé** | Créez une "Clé API" (API Key) |
| 5️⃣ | **Configuration** | Dans MusicDL : **Configuration > Configurer la clé API YouTube** |

> ⚠️ **Important** : Sans clé API, seule la fonctionnalité de téléchargement par URL directe sera disponible.

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

| Fichier | Rôle | Description |
|---------|------|-------------|
| `main.py` | 🚀 **Point d'entrée** | Gère l'installation des dépendances et lance l'application |
| `main_gui.py` | 🖥️ **Interface principale** | Cœur de l'application, gère l'interface et la logique |
| `config_manager.py` | ⚙️ **Configuration** | Gestion des paramètres (clé API, chemins, préférences) |
| `youtube_api.py` | 🔍 **API YouTube** | Interface avec l'API YouTube Data v3 |
| `downloader.py` | 📥 **Téléchargement** | Logique de téléchargement avec yt-dlp |
| `memory_manager.py` | 💾 **Mémoire** | Sauvegarde et chargement des listes de liens |
| `dialogs.py` | 💬 **Dialogues** | Boîtes de dialogue personnalisées |
| `Youtube Downloader.bat` | 🏃 **Lanceur Windows** | Script de lancement pour Windows |

## Dépannage

### Problèmes Courants

| Problème | Cause Probable | Solution |
|----------|----------------|----------|
| ❌ **Erreur de téléchargement** | URL invalide ou vidéo privée | Vérifiez l'URL et les permissions |
| 🔑 **Recherche non disponible** | Clé API manquante/invalide | Configurez une clé API valide |
| 🐌 **Téléchargement lent** | Connexion Internet | Réduisez la limite de téléchargements simultanés |
| 💾 **Erreur de sauvegarde** | Permissions insuffisantes | Vérifiez les droits d'écriture du dossier |
| 🔄 **Interface figée** | Traitement en cours | Attendez la fin du traitement |

### Codes d'Erreur

| Code | Signification | Action |
|------|---------------|--------|
| `ERROR_001` | Clé API invalide | Vérifiez votre clé dans Configuration |
| `ERROR_002` | Quota API dépassé | Attendez le renouvellement (24h) |
| `ERROR_003` | Fichier inaccessible | Vérifiez les permissions |
| `ERROR_004` | Format non supporté | Choisissez un format compatible |

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à forker le dépôt et à proposer des pull requests pour de nouvelles fonctionnalités ou des corrections de bugs.

## Licence

Ce projet est sous licence MIT.