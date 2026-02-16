from flask import Blueprint, jsonify, request, current_app
from src.web_auth import WebAuth
from src.utils.logger import get_logger
from src.monitoring_history import get_monitoring_manager

logger = get_logger(__name__)

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/api/monitoring/hosts')
@WebAuth.any_login_required
def get_monitoring_hosts():
    try:
        manager = get_monitoring_manager()
        hosts_data = manager.get_hosts_with_data()
        
        # Récupérer les noms d'hôtes via le HostManager
        host_manager = None
        if 'WEB_SERVER' in current_app.config:
            host_manager = current_app.config['WEB_SERVER'].host_manager
            
        all_hosts_info = {}
        if host_manager:
            for host in host_manager.get_all_hosts():
                ip = host.get('ip')
                if ip:
                    all_hosts_info[ip] = host.get('nom', ip)

        # Convertir en liste pour le frontend
        hosts_list = []
        for ip, data in hosts_data.items():
            hostname = all_hosts_info.get(ip, ip)
            hosts_list.append({
                'ip': ip,
                'hostname': hostname,
                'has_temperature': data.get('has_temperature', False),
                'has_bandwidth': data.get('has_bandwidth', False)
            })
            
        # Trier par nom
        hosts_list.sort(key=lambda x: x['hostname'])
            
        return jsonify({'success': True, 'data': hosts_list})
    except Exception as e:
        logger.error(f"Erreur API monitoring hosts: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/api/monitoring/temperature/<ip>')
@WebAuth.any_login_required
def get_temperature_history_route(ip):
    try:
        hours = int(request.args.get('hours', 24))
        manager = get_monitoring_manager()
        data = manager.get_temperature_history(ip, hours)
        
        # Transformer pour l'API
        result = [{'timestamp': r['timestamp'], 'value': r['value']} for r in data]
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        logger.error(f"Erreur API monitoring temperature {ip}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/api/monitoring/bandwidth/<ip>')
@WebAuth.any_login_required
def get_bandwidth_history_route(ip):
    try:
        hours = int(request.args.get('hours', 24))
        manager = get_monitoring_manager()
        data = manager.get_bandwidth_history(ip, hours)
        
        # Transformer pour l'API
        result = [{'timestamp': r['timestamp'], 'in_mbps': r['in_mbps'], 'out_mbps': r['out_mbps']} for r in data]
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        logger.error(f"Erreur API monitoring bandwidth {ip}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
