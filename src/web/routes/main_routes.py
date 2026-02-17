from flask import Blueprint, render_template, session, jsonify, request, current_app
from src.web_auth import WebAuth
from src.utils.logger import get_logger
from src import var, db

logger = get_logger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@WebAuth.any_login_required
def index():
    try:
        is_admin = session.get('role') == 'admin'
        username = session.get('username', '')
        return render_template('index.html', is_admin=is_admin, username=username)
    except Exception as e:
        logger.error(f"Erreur rendu index: {e}", exc_info=True)
        return jsonify({'error': 'Template introuvable'}), 500

@main_bp.route('/synoptic')
@WebAuth.any_login_required
def synoptic():
    try:
        # Vérification de la licence
        from src import lic
        if not lic.verify_license():
            # Licence invalide - afficher une page d'erreur
            error_message = "Vous devez avoir une licence active pour accéder à la page synoptique."
            return render_template('error.html', 
                                 error_title="Licence requise",
                                 error_message=error_message,
                                 is_admin=session.get('role') == 'admin',
                                 username=session.get('username', '')), 403
        
        # Licence valide - afficher la page normalement
        is_admin = session.get('role') == 'admin'
        username = session.get('username', '')
        return render_template('synoptic.html', is_admin=is_admin, username=username)
    except Exception as e:
        logger.error(f"Erreur rendu synoptic: {e}", exc_info=True)
        return jsonify({'error': 'Template introuvable'}), 500

@main_bp.route('/monitoring')
@WebAuth.any_login_required
def monitoring():
    try:
        is_admin = session.get('role') == 'admin'
        username = session.get('username', '')
        # Vérifier si on a un host_id en paramètre pour pré-sélectionner
        host_id = request.args.get('host', '')
        return render_template('monitoring.html', is_admin=is_admin, username=username, selected_host=host_id)
    except Exception as e:
        logger.error(f"Erreur rendu monitoring: {e}", exc_info=True)
        return jsonify({'error': 'Template introuvable'}), 500

@main_bp.route('/statistics')
@WebAuth.any_login_required
def statistics():
    try:
        is_admin = session.get('role') == 'admin'
        username = session.get('username', '')
        # Récupérer le paramètre IP si fourni
        ip_filter = request.args.get('ip', '')
        return render_template('statistics.html', is_admin=is_admin, username=username, ip_filter=ip_filter)
    except Exception as e:
        logger.error(f"Erreur rendu statistics: {e}", exc_info=True)
        return jsonify({'error': 'Template introuvable'}), 500

@main_bp.route('/api/start_monitoring', methods=['POST'])
@WebAuth.login_required
def start_monitoring():
    try:
        data = request.get_json()
        delai = data.get('delai', 10)
        nb_hs = data.get('nb_hs', 3)
        var.delais = delai
        var.nbrHs = int(nb_hs)
        
        main_window = current_app.config['MAIN_WINDOW']
        if hasattr(main_window, 'main_controller'):
            if main_window.main_controller.ping_manager is None:
                main_window.comm.start_monitoring_signal.emit()
                current_app.config['WEB_SERVER'].socketio.emit('monitoring_status', {'running': True})
                return jsonify({'success': True, 'message': 'Monitoring démarré'})
            else:
                current_app.config['WEB_SERVER']._clean_alert_lists_for_new_threshold(int(nb_hs))
                return jsonify({'success': True, 'message': 'Configuration mise à jour'})
        return jsonify({'success': False, 'error': 'Contrôleur non disponible'}), 500
    except Exception as e:
        logger.error(f"Erreur start_monitoring: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/stop_monitoring', methods=['POST'])
@WebAuth.login_required
def stop_monitoring():
    try:
        main_window = current_app.config['MAIN_WINDOW']
        if hasattr(main_window, 'main_controller'):
            if main_window.main_controller.ping_manager is not None:
                main_window.comm.stop_monitoring_signal.emit()
                current_app.config['WEB_SERVER'].socketio.emit('monitoring_status', {'running': False})
                return jsonify({'success': True, 'message': 'Monitoring arrêté'})
            return jsonify({'success': True, 'message': 'Monitoring déjà arrêté'})
        return jsonify({'success': False, 'error': 'Contrôleur non disponible'}), 500
    except Exception as e:
        logger.error(f"Erreur stop_monitoring: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/save_alerts', methods=['POST'])
@WebAuth.login_required
def save_alerts():
    try:
        data = request.get_json()
        var.popup = data.get('popup', False)
        var.mail = data.get('mail', False)
        var.telegram = data.get('telegram', False)
        var.mailRecap = data.get('mail_recap', False)
        var.dbExterne = data.get('db_externe', False)
        var.tempAlert = data.get('temp_alert', False)
        var.tempSeuil = data.get('temp_seuil', 70)
        var.tempSeuilWarning = data.get('temp_seuil_warning', 60)
        db.save_param_db()
        return jsonify({'success': True, 'message': 'Alertes sauvegardées'})
    except Exception as e:
        logger.error(f"Erreur save_alerts: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
