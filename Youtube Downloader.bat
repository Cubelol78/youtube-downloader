@echo off
:: Définit le nom de votre script Python
SET SCRIPT_PYTHON="main.pyw"

:: --- Vérifie si Python est installé et accessible via la variable PATH ---
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas trouvé dans votre PATH.
    echo.
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    echo ou assurez-vous qu'il est ajouté à votre variable d'environnement PATH.
    echo.
    echo Le script ne peut pas continuer.
    pause
    exit /b 1
)

:: --- Lance le script Python en utilisant pythonw pour les applications graphiques ---
echo Lancement de %SCRIPT_PYTHON%...
start "" pythonw %SCRIPT_PYTHON%

:: Vérifie si le lancement a rencontré une erreur (bien que 'start' ne renvoie pas toujours un errorlevel fiable pour le processus lancé)
if %errorlevel% neq 0 (
    echo Une erreur est survenue lors du lancement de %SCRIPT_PYTHON%.
    echo Assurez-vous que le fichier %SCRIPT_PYTHON% existe dans le meme repertoire que ce lanceur.
    pause
    exit /b 1
)

:: Quitte le script avec un code de succes
exit /b 0
