from flask import Blueprint, request, jsonify, render_template, current_app
from src.web_auth import WebAuth, web_auth
from src.utils.logger import get_logger

logger = get_logger(__name__)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@WebAuth.login_required
def admin_page():
    try:
        return render_template('admin.html')
    except Exception as e:
        logger.error(f"Erreur rendu admin: {e}", exc_info=True)
        return jsonify({'error': 'Template introuvable'}), 500

@admin_bp.route('/api/get_users')
@WebAuth.login_required
def get_users():
    try:
        users = web_auth.get_users_list()
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        logger.error(f"Erreur récupération utilisateurs: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/add_user', methods=['POST'])
@WebAuth.login_required
def add_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        success, message = web_auth.add_user(username, password, role)
        return jsonify({'success': success, 'message' if success else 'error': message})
    except Exception as e:
        logger.error(f"Erreur ajout utilisateur: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/delete_user', methods=['POST'])
@WebAuth.login_required
def delete_user():
    try:
        data = request.get_json()
        username = data.get('username')
        success, message = web_auth.delete_user(username)
        return jsonify({'success': success, 'message' if success else 'error': message})
    except Exception as e:
        logger.error(f"Erreur suppression utilisateur: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/update_user_password', methods=['POST'])
@WebAuth.login_required
def update_user_password():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('new_password')
        success, message = web_auth.update_user_password(username, password)
        return jsonify({'success': success, 'message' if success else 'error': message})
    except Exception as e:
        logger.error(f"Erreur update_user_password: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/update_user_role', methods=['POST'])
@WebAuth.login_required
def update_user_role():
    try:
        data = request.get_json()
        username = data.get('username')
        role = data.get('role')
        success, message = web_auth.update_user_role(username, role)
        return jsonify({'success': success, 'message' if success else 'error': message})
    except Exception as e:
        logger.error(f"Erreur update_user_role: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
@admin_bp.route('/api/change_user_credentials', methods=['POST'])
@WebAuth.login_required
def change_user_credentials():
    try:
        data = request.get_json()
        target_role = data.get('role')
        new_username = data.get('new_username')
        new_password = data.get('new_password')
        success, message = web_auth.change_user_credentials(target_role, new_username, new_password)
        return jsonify({'success': success, 'message': message if success else message})
    except Exception as e:
        logger.error(f"Erreur change_user_credentials: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
