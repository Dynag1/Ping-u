from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from src.web_auth import web_auth, WebAuth
from src.utils.logger import get_logger

logger = get_logger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    try:
        if session.get('logged_in'):
            if session.get('role') == 'admin':
                return redirect(url_for('admin.admin_page'))
            else:
                return redirect(url_for('main.index'))
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Erreur rendu login: {e}", exc_info=True)
        return jsonify({'error': 'Template introuvable'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        client_ip = request.remote_addr
        
        success, role, must_change = web_auth.verify_credentials(username, password, client_ip)
        if success:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = role
            logger.info(f"Connexion réussie: {username} (role: {role})")
            return jsonify({
                'success': True, 
                'role': role,
                'must_change_password': must_change
            })
        else:
            return jsonify({'success': False, 'error': 'Identifiants incorrects'}), 401
    except Exception as e:
        logger.error(f"Erreur login: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Erreur serveur'}), 500

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"Déconnexion: {username}")
    return jsonify({'success': True})

@auth_bp.route('/api/change_credentials', methods=['POST'])
@WebAuth.login_required
def change_credentials():
    try:
        data = request.get_json()
        old_password = data.get('old_password')
        new_username = data.get('new_username')
        new_password = data.get('new_password')
        
        success, message = web_auth.change_credentials(old_password, new_username, new_password)
        if success:
            session.clear()
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
    except Exception as e:
        logger.error(f"Erreur changement credentials: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
