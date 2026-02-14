from flask import Blueprint, request, jsonify, session
from src.web_auth import WebAuth
from src.utils.logger import get_logger
from src.database import create_dashboard, get_dashboards, get_dashboard, update_dashboard, delete_dashboard

logger = get_logger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboards', methods=['GET'])
@WebAuth.login_required
def list_dashboards():
    try:
        # On pourrait filtrer par user via session['user_id'] si on l'avait stocké
        dashboards = get_dashboards()
        return jsonify({'success': True, 'dashboards': dashboards})
    except Exception as e:
        logger.error(f"Erreur list_dashboards: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/dashboards', methods=['POST'])
@WebAuth.login_required
def create_dashboard_route():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'success': False, 'error': 'Nom requis'}), 400
            
        dash_id = create_dashboard(name)
        if dash_id:
            return jsonify({'success': True, 'id': dash_id})
        else:
            return jsonify({'success': False, 'error': 'Erreur création'}), 500
    except Exception as e:
        logger.error(f"Erreur create_dashboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/dashboards/<int:dash_id>', methods=['GET'])
@WebAuth.login_required
def get_dashboard_route(dash_id):
    try:
        dashboard = get_dashboard(dash_id)
        if dashboard:
            return jsonify({'success': True, 'dashboard': dashboard})
        else:
            return jsonify({'success': False, 'error': 'Tableau de bord non trouvé'}), 404
    except Exception as e:
        logger.error(f"Erreur get_dashboard {dash_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/dashboards/<int:dash_id>', methods=['PUT'])
@WebAuth.login_required
def update_dashboard_route(dash_id):
    try:
        data = request.get_json()
        name = data.get('name')
        hosts = data.get('hosts', []) # Liste d'IPs
        
        if not name:
            return jsonify({'success': False, 'error': 'Nom requis'}), 400
            
        if update_dashboard(dash_id, name, hosts):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Erreur mise à jour'}), 500
    except Exception as e:
        logger.error(f"Erreur update_dashboard {dash_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/dashboards/<int:dash_id>', methods=['DELETE'])
@WebAuth.login_required
def delete_dashboard_route(dash_id):
    try:
        if delete_dashboard(dash_id):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Erreur suppression'}), 500
    except Exception as e:
        logger.error(f"Erreur delete_dashboard {dash_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
