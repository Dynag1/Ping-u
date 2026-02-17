from flask import Blueprint, request, jsonify, current_app
from src.web_auth import WebAuth
from src.utils.logger import get_logger
from src import db, var, lic, secure_config

logger = get_logger(__name__)

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/api/get_settings')
def get_settings():
    try:
        main_window = current_app.config['MAIN_WINDOW']
        monitoring_running = False
        if hasattr(main_window, 'main_controller'):
            monitoring_running = main_window.main_controller.ping_manager is not None
        
        smtp_params = db.lire_param_mail() or ['', '', '', '', '', '']
        general_params = db.lire_param_gene() or ['', '', 'nord', 'Paramètres Avancés']
        license_active = lic.verify_license()
        
        return jsonify({
            'success': True,
            'delai': var.delais,
            'nb_hs': var.nbrHs,
            'alerts': {
                'popup': var.popup, 'mail': var.mail, 'telegram': var.telegram,
                'mail_recap': var.mailRecap, 'db_externe': var.dbExterne,
                'temp_alert': var.tempAlert, 'temp_seuil': var.tempSeuil,
                'temp_seuil_warning': var.tempSeuilWarning
            },
            'monitoring_running': monitoring_running,
            'smtp': {
                'server': smtp_params[3] if len(smtp_params) > 3 else '',
                'port': smtp_params[2] if len(smtp_params) > 2 else '',
                'email': smtp_params[0] if len(smtp_params) > 0 else '',
                'recipients': smtp_params[4] if len(smtp_params) > 4 else ''
            },
            'telegram': {
                'configured': bool(smtp_params[5] if len(smtp_params) > 5 else ''),
                'chatid': smtp_params[5] if len(smtp_params) > 5 else '',
                'token': secure_config.get_telegram_token()
            },
            'general': {
                'site': general_params[0],
                'license': general_params[1] if len(general_params) > 1 else '',
                'theme': general_params[2],
                'advanced_title': general_params[3] if len(general_params) > 3 else 'Paramètres Avancés'
            },
            'version': var.version
        })
    except Exception as e:
        logger.error(f"Erreur get_settings: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/save_smtp', methods=['POST'])
@WebAuth.login_required
def save_smtp():
    try:
        data = request.get_json()
        current_params = db.lire_param_mail()
        telegram_chatid = current_params[5] if current_params and len(current_params) > 5 else ''
        variables = [
            data.get('email', ''), data.get('password', ''), data.get('port', ''),
            data.get('server', ''), data.get('recipients', ''), telegram_chatid
        ]
        db.save_param_mail(variables)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur save_smtp: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/save_telegram', methods=['POST'])
@WebAuth.login_required
def save_telegram():
    try:
        data = request.get_json()
        chatid = data.get('chatid', '')
        token = data.get('token', '')

        # Save to database/config
        current_params = db.lire_param_mail() or ['', '', '', '', '', '']
        
        # Save chat ID in legacy db param for compatibility
        variables = [
            current_params[0], current_params[1], current_params[2],
            current_params[3], current_params[4], chatid
        ]
        db.save_param_mail(variables)
        
        # Save token and chat ID in secure config
        secure_config.save_telegram_config(token=token, chat_ids=[chatid])
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur save_telegram: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/test_telegram', methods=['POST'])
@WebAuth.login_required
def test_telegram():
    try:
        data = request.get_json()
        chatid = data.get('chatid', '')
        from src import thread_telegram
        import threading
        msg = f"Ping ü: Test de notification Telegram réussi [Site: {var.nom_site}]"
        threading.Thread(target=thread_telegram.main, args=(msg, chatid)).start()
        return jsonify({'success': True, 'message': 'Test envoyé'})
    except Exception as e:
        logger.error(f"Erreur test_telegram: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/save_alerts', methods=['POST'])
@WebAuth.login_required
def save_alerts():
    try:
        data = request.get_json()
        
        # Mise à jour des variables
        var.popup = data.get('popup', False)
        var.mail = data.get('mail', False)
        var.telegram = data.get('telegram', False)
        var.mailRecap = data.get('mail_recap', False)
        var.dbExterne = data.get('db_externe', False)
        var.tempAlert = data.get('temp_alert', False)
        
        try:
            var.tempSeuil = int(data.get('temp_seuil', 70))
        except:
            pass
            
        try:
            var.tempSeuilWarning = int(data.get('temp_seuil_warning', 60))
        except:
            pass
            
        # Sauvegarde persistante
        db.save_param_db()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur save_alerts: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
@settings_bp.route('/api/get_mail_recap_settings')
@WebAuth.login_required
def get_mail_recap_settings():
    try:
        params = db.lire_param_mail_recap() or ['', False, False, False, False, False, False, False]
        heure = params[0]
        if hasattr(heure, 'strftime'):
            heure = heure.strftime('%H:%M')
        elif not isinstance(heure, str):
            heure = str(heure)

        return jsonify({
            'success': True,
            'heure': heure,
            'lundi': params[1], 'mardi': params[2], 'mercredi': params[3],
            'jeudi': params[4], 'vendredi': params[5], 'samedi': params[6], 'dimanche': params[7]
        })
    except Exception as e:
        logger.error(f"Erreur get_mail_recap_settings: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/save_mail_recap', methods=['POST'])
@WebAuth.login_required
def save_mail_recap():
    try:
        data = request.get_json()
        variables = [
            data.get('heure', '08:00'),
            data.get('lundi', False), data.get('mardi', False), data.get('mercredi', False),
            data.get('jeudi', False), data.get('vendredi', False), data.get('samedi', False),
            data.get('dimanche', False)
        ]
        db.save_param_mail_recap(variables)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur save_mail_recap: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/send_test_recap', methods=['POST'])
@WebAuth.login_required
def send_test_recap():
    try:
        from src import email_sender
        import threading
        main_window = current_app.config['MAIN_WINDOW']
        threading.Thread(target=email_sender.send_recap_email, args=(main_window.treeIpModel, True)).start()
        return jsonify({'success': True, 'message': 'Email de test envoyé'})
    except Exception as e:
        logger.error(f"Erreur send_test_recap: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/get_license_info')
@WebAuth.login_required
def get_license_info():
    try:
        is_active = lic.verify_license()
        activation_code = lic.generate_activation_code()
        
        # Log pour debug
        logger.info(f"API get_license_info: active={is_active}, code={activation_code}")
        
        return jsonify({
            'success': True,
            'active': is_active,
            'activation_code': activation_code,
            'days_remaining': lic.jours_restants_licence()
        })
    except Exception as e:
        logger.error(f"Erreur get_license_info: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/save_general', methods=['POST'])
@WebAuth.login_required
def save_general():
    try:
        data = request.get_json()
        
        # Sauvegarde via secure_config
        secure_config.save_general_config(
            site_name=data.get('site', ''),
            license_key=data.get('license', ''),
            theme=data.get('theme', 'nord')
        )
        
        # Mise à jour des variables globales pour effet immédiat
        var.nom_site = data.get('site', '')
        var.license_key = data.get('license', '')
        var.theme = data.get('theme', 'nord')
        
        # Legacy backup
        db.save_param_db()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur save_general: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/update_general_setting', methods=['POST'])
@WebAuth.login_required
def update_general_setting():
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        
        if key == 'site': 
            var.nom_site = value
            secure_config.save_general_config(site_name=value)
        elif key == 'theme': 
            var.theme = value
            secure_config.save_general_config(theme=value)
        elif key == 'advanced_title':
            secure_config.save_general_config(advanced_title=value)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur update_general_setting: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/save_settings', methods=['POST'])
@WebAuth.login_required
def save_settings():
    try:
        # Si des données sont envoyées, on met à jour les variables
        if request.is_json:
            data = request.get_json()
            if 'delai' in data:
                try:
                    var.delais = int(data['delai'])
                except:
                    pass
            if 'nb_hs' in data:
                try:
                    var.nbrHs = int(data['nb_hs'])
                except:
                    pass
                    
        db.save_param_db()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur save_settings: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

from src.database import get_host_notification_settings, set_host_notification_settings

@settings_bp.route('/api/test_smtp', methods=['POST'])
@WebAuth.login_required
def test_smtp():
    try:
        from src import thread_mail
        import threading
        msg = f"Ping ü: Test de configuration SMTP réussi [Site: {var.nom_site}]"
        threading.Thread(target=thread_mail.envoie_mail, args=(msg, "Test SMTP Ping ü")).start()
        return jsonify({'success': True, 'message': 'Test envoyé'})
    except Exception as e:
        logger.error(f"Erreur test_smtp: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/host/settings/<path:ip>', methods=['GET'])
@WebAuth.login_required
def get_host_settings_route(ip):
    try:
        settings = get_host_notification_settings(ip)
        return jsonify({'success': True, 'settings': settings})
    except Exception as e:
        logger.error(f"Erreur get_host_settings {ip}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/api/host/settings/<path:ip>', methods=['POST'])
@WebAuth.login_required
def save_host_settings_route(ip):
    try:
        data = request.get_json()
        email = data.get('email', True)
        telegram = data.get('telegram', True)
        
        if set_host_notification_settings(ip, email, telegram):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Erreur sauvegarde'}), 500
    except Exception as e:
        logger.error(f"Erreur save_host_settings {ip}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
