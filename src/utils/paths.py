import os
from pathlib import Path
import sys

class AppPaths:
    """
    Gestionnaire centralisé des chemins de l'application.
    Assure la compatibilité cross-platform et gère les chemins pour PyInstaller.
    """
    
    @staticmethod
    def get_base_dir() -> Path:
        """Retourne le dossier racine de l'application."""
        if getattr(sys, 'frozen', False):
            # Si exécuté en tant qu'exe (PyInstaller)
            return Path(sys._MEIPASS)
        else:
            # Si exécuté en tant que script
            # On remonte de src/utils/ vers la racine
            return Path(__file__).parent.parent.parent.resolve()

    @staticmethod
    def get_cwd() -> Path:
        """Retourne le dossier de travail actuel (là où l'app est lancée)."""
        return Path.cwd()

    @staticmethod
    def get_logs_dir() -> Path:
        return AppPaths.get_cwd() / "logs"

    @staticmethod
    def get_config_dir() -> Path:
        # Pour l'instant, on garde la compatibilité avec l'existant (racine)
        # Idéalement, ce serait dans AppData ou .config
        return AppPaths.get_cwd()

    @staticmethod
    def get_db_dir() -> Path:
        return AppPaths.get_cwd() / "bd"

    @staticmethod
    def get_plugin_dir() -> Path:
        return AppPaths.get_cwd() / "fichier" / "plugin"
        
    @staticmethod
    def get_keys_dir() -> Path:
        return AppPaths.get_cwd() / "cle"

    @staticmethod
    def ensure_dirs():
        """Crée tous les dossiers nécessaires s'ils n'existent pas."""
        dirs = [
            AppPaths.get_logs_dir(),
            AppPaths.get_db_dir(),
            AppPaths.get_plugin_dir(),
            AppPaths.get_keys_dir(),
            AppPaths.get_cwd() / "fichier" # Parent de plugin
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
