from flask import Blueprint, render_template, jsonify, request, current_app
from src.web_auth import WebAuth
from src.utils.logger import get_logger
import os

logger = get_logger(__name__)
log_bp = Blueprint('log', __name__)

# Chemin du fichier de logs
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")

@log_bp.route('/logs')
@WebAuth.login_required
def view_logs():
    """Affiche la page des logs"""
    return render_template('logs.html')

@log_bp.route('/api/logs/content')
@WebAuth.login_required
def get_log_content():
    """Récupère le contenu des logs (les N dernières lignes)"""
    try:
        lines_count = int(request.args.get('lines', 200))
        if not os.path.exists(LOG_FILE):
            return jsonify({'success': False, 'error': 'Fichier de logs introuvable'}), 404
            
        logs = []
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            # Lire tout et garder les dernières lignes
            # Pour un gros fichier, ce n'est pas optimal mais suffisant pour < 10MB
            # Une optimisation serait d'utiliser seek() depuis la fin
            all_lines = f.readlines()
            logs = all_lines[-lines_count:]
            
        return jsonify({'success': True, 'logs': ''.join(logs)})
    except Exception as e:
        logger.error(f"Erreur lecture logs: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@log_bp.route('/api/logs/clear', methods=['POST'])
@WebAuth.login_required
def clear_logs():
    """Efface le fichier de logs"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w') as f:
                f.write("")
            logger.info("Logs effacés via l'interface web")
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Fichier introuvable'}), 404
    except Exception as e:
        logger.error(f"Erreur effacement logs: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
