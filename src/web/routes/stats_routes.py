from flask import Blueprint, jsonify, request
from src.web_auth import WebAuth
from src.utils.logger import get_logger
from src.connection_stats import stats_manager

logger = get_logger(__name__)

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/stats/overview')
@WebAuth.any_login_required
def get_overview_stats():
    try:
        days = int(request.args.get('days', 30))
        data = stats_manager.get_overview_stats(days=days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Erreur get_overview_stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@stats_bp.route('/api/stats/top')
@WebAuth.any_login_required
def get_top_disconnectors():
    try:
        limit = int(request.args.get('limit', 10))
        days = int(request.args.get('days', 30))
        data = stats_manager.get_top_disconnectors(limit=limit, days=days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Erreur get_top_disconnectors: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@stats_bp.route('/api/stats/events')
@WebAuth.any_login_required
def get_recent_events():
    try:
        limit = int(request.args.get('limit', 15))
        data = stats_manager.get_recent_events(limit=limit)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Erreur get_recent_events: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@stats_bp.route('/api/stats/hosts')
@WebAuth.any_login_required
def get_tracked_hosts():
    try:
        from flask import current_app
        hosts = stats_manager.get_all_tracked_hosts()
        
        # Enrichir avec le statut temps réel
        main_window = current_app.config.get('MAIN_WINDOW')
        if main_window and hasattr(main_window, 'host_manager'):
            for host in hosts:
                # Statut par défaut
                host['status'] = 'offline'
                
                # Récupérer l'hôte vivant
                live_host = main_window.host_manager.get_host_by_ip(host['ip'])
                if live_host:
                    # Le statut dans HostManager est 'online' ou 'offline'
                    host['status'] = live_host.get('status', 'offline')
                    # Mise à jour du nom si manquant en DB
                    if not host.get('hostname') and live_host.get('nom'):
                        host['hostname'] = live_host.get('nom')
                        
        return jsonify({'success': True, 'data': hosts})
    except Exception as e:
        logger.error(f"Erreur get_tracked_hosts: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@stats_bp.route('/api/stats/host/<ip>')
@WebAuth.any_login_required
def get_host_stats(ip):
    try:
        # Récupérer les stats globales
        stats = stats_manager.get_host_stats(ip)
        
        # Récupérer l'historique des événements (limité à 50 pour la timeline/table)
        events = stats_manager.get_host_events(ip, limit=50)
        
        # Retourner la structure combinée attendue par displayHostDetails
        return jsonify({
            'success': True, 
            'data': {
                'stats': stats,
                'events': events
            }
        })
    except Exception as e:
        logger.error(f"Erreur get_host_stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@stats_bp.route('/api/stats/host/<ip>/events')
@WebAuth.any_login_required
def get_host_events(ip):
    try:
        limit = int(request.args.get('limit', 50))
        data = stats_manager.get_host_events(ip, limit=limit)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Erreur get_host_events: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@stats_bp.route('/api/stats/reset', methods=['POST'])
@WebAuth.login_required
def reset_stats():
    try:
        count = stats_manager.reset_all_stats()
        return jsonify({'success': True, 'message': f'{count} événements supprimés'})
    except Exception as e:
        logger.error(f"Erreur reset_stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
