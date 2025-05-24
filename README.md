# MusicDL - Téléchargeur de Musique YouTube

MusicDL est une application de bureau conçue pour faciliter le téléchargement de musique et de vidéos depuis YouTube. Elle offre une interface graphique intuitive, des fonctionnalités de recherche via l'API YouTube, et la possibilité de gérer une "mémoire" de liens pour des téléchargements en masse.

## Table des matières

* [MusicDL - Téléchargeur de Musique YouTube](#musicdl---téléchargeur-de-musique-youtube)

  * [Table des matières](#table-des-matières)

  * [Fonctionnalités](#fonctionnalités)

  * [Lancement de l'application](#lancement-de-lapplication)

    * [Clé API YouTube (Optionnel)](#clé-api-youtube-optionnel)

  * [Utilisation](#utilisation)

    * [Interface principale](#interface-principale)

    * [Recherche de vidéos](#recherche-de-vidéos)

    * [Téléchargement](#téléchargement)

    * [Gestion de la mémoire](#gestion-de-la-mémoire)

    * [Configuration](#configuration)

  * [Structure du projet](#structure-du-projet)

  * [Contribuer](#contribuer)

  * [Licence](#licence)

## Fonctionnalités

* **Recherche YouTube Intégrée :** Trouvez des vidéos et de la musique directement depuis l'application en utilisant l'API YouTube Data API v3.

* **Téléchargement de Vidéos/Audio :** Téléchargez des vidéos complètes ou extrayez uniquement l'audio dans le format de votre choix.

* **Gestion de la Mémoire :** Sauvegardez des liens YouTube pour des téléchargements ultérieurs ou en masse.

* **Téléchargement en Masse :** Téléchargez simultanément plusieurs éléments depuis votre "mémoire".

* **Interface Graphique (GUI) :** Basé sur `tkinter` pour une expérience utilisateur simple et interactive.

* **Configuration Persistante :** Sauvegarde le chemin de téléchargement et la clé API YouTube.

## Lancement de l'application

Pour lancer MusicDL, exécutez le script `Youtube Downloader.bat` :

```
python main.py

```

### Clé API YouTube (Optionnel)

Pour utiliser la fonctionnalité de recherche YouTube, vous aurez besoin d'une clé API YouTube Data API v3. Si vous ne la fournissez pas, l'application fonctionnera pour les téléchargements directs via URL, mais la fonction de recherche de vidéos via mots-clés sera désactivée.

1. Rendez-vous sur la [console Google Cloud](https://console.developers.google.com/).

2. Créez un nouveau projet ou sélectionnez un projet existant.

3. Activez l'**API YouTube Data API v3** pour votre projet.

4. Créez des identifiants (Credentials) de type "Clé API" (API Key).

5. Copiez votre clé API.

Vous pourrez saisir cette clé API dans l'application via le menu "Configuration" > "Clé API YouTube".

## Utilisation

### Interface principale

L'interface principale est divisée en plusieurs sections :

* **Champ de recherche :** Pour saisir des requêtes YouTube ou des URLs directes.

* **Boutons de recherche :** Pour lancer la recherche ou effacer les résultats.

* **Liste des résultats de recherche :** Affiche les vidéos trouvées avec leur titre, URL et durée.

* **Boutons d'action pour les résultats :** Pour ajouter à la mémoire, copier l'URL, ou télécharger directement.

* **Chemin de téléchargement :** Affiche et permet de modifier le dossier où les fichiers seront sauvegardés.

* **Sélection du format :** Permet de choisir entre le téléchargement audio seul ou vidéo complète.

* **Onglet "Mémoire" :** Affiche les éléments que vous avez sauvegardés pour des téléchargements en masse.

* **Zone de log :** Affiche les messages de l'application, les progrès de téléchargement et les erreurs.

### Recherche de vidéos

1. Saisissez votre requête (titre de la chanson, artiste, etc.) dans le champ de texte en haut.

2. Cliquez sur le bouton "Rechercher".

3. Les résultats s'afficheront dans la liste.

### Téléchargement

* **Téléchargement depuis les résultats de recherche :**

  1. Sélectionnez un ou plusieurs éléments dans la liste des résultats de recherche.

  2. Choisissez le format de téléchargement (`Audio` ou `Vidéo`) via le menu déroulant.

  3. Cliquez sur "Télécharger les sélectionnés".

* **Téléchargement depuis la mémoire :**

  1. Allez dans l'onglet "Mémoire".

  2. Sélectionnez un ou plusieurs éléments que vous avez précédemment ajoutés.

  3. Choisissez le format de téléchargement.

  4. Cliquez sur "Télécharger les sélectionnés".

* **Téléchargement direct par URL :**

  1. Dans la section de recherche, collez directement une URL YouTube valide dans le champ de recherche.

  2. Cliquez sur le bouton "Télécharger (URL directe)".

  3. Choisissez le format de téléchargement.

### Gestion de la mémoire

* **Ajouter à la mémoire :**

  * Depuis les résultats de recherche : Sélectionnez un ou plusieurs éléments et cliquez sur "Ajouter à la Mémoire".

  * Depuis une URL directe : Saisissez l'URL et cliquez sur "Ajouter à la Mémoire (URL directe)".

* **Voir la mémoire :** Cliquez sur l'onglet "Mémoire" pour voir tous les éléments sauvegardés.

* **Supprimer de la mémoire :** Dans l'onglet "Mémoire", sélectionnez un ou plusieurs éléments et cliquez sur "Supprimer les sélectionnés".

* **Vider la mémoire :** Dans l'onglet "Mémoire", cliquez sur "Vider la Mémoire" pour supprimer tous les éléments.

### Configuration

Le menu "Configuration" permet de :

* **Changer le dossier de téléchargement :** "Définir le dossier de téléchargement".

* **Configurer la clé API YouTube :** "Clé API YouTube". Une fenêtre de dialogue s'ouvrira pour saisir votre clé.

## Structure du projet

* `main.py` : Point d'entrée principal de l'application.

* `main_gui.py` : Contient la classe `MusicDLGUI` qui gère l'interface utilisateur et la logique principale de l'application.

* `config_manager.py` : Gère le chargement et la sauvegarde de la configuration de l'application (clé API, chemin de téléchargement).

* `youtube_api.py` : Interagit avec l'API YouTube Data API v3 pour la recherche de vidéos.

* `downloader.py` : Encapsule la logique de téléchargement en utilisant `yt-dlp`. Gère les téléchargements individuels et en masse.

* `memory_manager.py` : Gère le chargement, la sauvegarde, l'ajout et la suppression des liens dans la "mémoire" de l'application.

* `dialogs.py` : Contient les classes pour les boîtes de dialogue personnalisées, comme celle pour la saisie de la clé API.

* `README.md` : Ce fichier de documentation.

## Contribuer

Les contributions sont les bienvenues ! Si vous souhaitez améliorer MusicDL, n'hésitez pas à :

1. Forker le dépôt.

2. Créer une nouvelle branche (`git checkout -b feature/nouvelle-fonctionnalite`).

3. Effectuer vos modifications.

4. Commiter vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`).

5. Pousser vers la branche (`git push origin feature/nouvelle-fonctionnalite`).

6. Ouvrir une Pull Request.

## Licence

Ce projet est sous licence [MIT](LICENSE).
