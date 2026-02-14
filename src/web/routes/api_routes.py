from flask import Blueprint, jsonify, session, request, current_app
from src.web_auth import WebAuth
from src.utils.logger import get_logger
import socket

logger = get_logger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/status')
def status():
    server = current_app.config['WEB_SERVER']
    return jsonify({
        'status': 'running',
        'hosts_count': server._get_hosts_count()
    })

@api_bp.route('/api/local_ip')
@WebAuth.login_required
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return jsonify({'success': True, 'ip': IP})
    except Exception as e:
        logger.error(f"Erreur IP locale: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/api/user_info')
@WebAuth.any_login_required
def user_info():
    return jsonify({
        'success': True,
        'username': session.get('username', ''),
        'role': session.get('role', 'user'),
        'is_admin': session.get('role') == 'admin'
    })
