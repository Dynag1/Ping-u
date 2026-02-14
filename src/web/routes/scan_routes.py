from flask import Blueprint, request, jsonify, current_app, send_file
from src.web_auth import WebAuth
from src.utils.logger import get_logger
import tempfile
import os

logger = get_logger(__name__)

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/api/add_hosts', methods=['POST'])
@WebAuth.login_required
def add_hosts():
    try:
        data = request.get_json()
        ip = data.get('ip', '').strip()
        hosts = data.get('hosts', 1)
        port = data.get('port', '80')
        scan_type = data.get('scan_type', 'alive')
        site = data.get('site', '')
        
        # Validation simplified for brevity here, normally should be robust
        main_window = current_app.config['MAIN_WINDOW']
        import threading
        from src import threadAjIp
        
        thread = threading.Thread(
            target=threadAjIp.main,
            args=(main_window, main_window.comm, 
                  main_window.treeIpModel, ip, hosts, 
                  scan_type.capitalize(), str(port), "", site)
        )
        thread.start()
        return jsonify({'success': True, 'message': 'Scan démarré'})
    except Exception as e:
        logger.error(f"Erreur add_hosts: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@scan_bp.route('/api/export_csv')
def export_csv():
    try:
        from src import fct
        main_window = current_app.config['MAIN_WINDOW']
        temp_path = os.path.join(tempfile.gettempdir(), 'export_hosts.csv')
        fct.save_csv(main_window, main_window.treeIpModel, filepath=temp_path, return_path=True)
        return send_file(temp_path, as_attachment=True, download_name='hosts.csv', mimetype='text/csv')
    except Exception as e:
        logger.error(f"Erreur export_csv: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@scan_bp.route('/api/import_csv', methods=['POST'])
@WebAuth.login_required
def import_csv():
    try:
        if 'file' not in request.files: return jsonify({'success': False}), 400
        file = request.files['file']
        temp_path = os.path.join(tempfile.gettempdir(), 'import.csv')
        file.save(temp_path)
        from src import fct
        fct.load_csv(current_app.config['MAIN_WINDOW'], current_app.config['MAIN_WINDOW'].treeIpModel, temp_path)
        os.remove(temp_path)
        current_app.config['WEB_SERVER'].broadcast_update()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur import_csv: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@scan_bp.route('/api/export_xls')
@WebAuth.login_required
def export_xls():
    try:
        from src import fctXls
        temp_path = os.path.join(tempfile.gettempdir(), 'export_hosts.xlsx')
        fctXls.export_xls_web(current_app.config['MAIN_WINDOW'].treeIpModel, temp_path)
        return send_file(temp_path, as_attachment=True, download_name='hosts.xlsx', 
                       mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        logger.error(f"Erreur export_xls: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
@scan_bp.route('/api/network_scan/start', methods=['POST'])
@WebAuth.login_required
def start_network_scan():
    try:
        data = request.get_json() or {}
        # Par défaut, scanner tous les types supportés
        scan_types = data.get('scan_types', ['hik', 'onvif', 'dahua', 'xiaomi', 'samsung', 'upnp', 'server'])
        timeout = int(data.get('timeout', 15))
        
        web_server = current_app.config['WEB_SERVER']
        if hasattr(web_server, '_network_scanner') and web_server._network_scanner:
            import threading
            # Lancer le scan dans un thread séparé
            threading.Thread(target=web_server._network_scanner.scan_network, 
                           args=(scan_types, timeout)).start()
            return jsonify({'success': True, 'message': 'Scan réseau démarré'})
        
        return jsonify({'success': False, 'error': 'Scanner réseau non disponible'}), 500
    except Exception as e:
        logger.error(f"Erreur start_network_scan: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@scan_bp.route('/api/network_scan/stop', methods=['POST'])
@WebAuth.login_required
def stop_network_scan():
    try:
        from src import var
        var.stop_event.set()
        return jsonify({'success': True, 'message': 'Demande d\'arrêt envoyée'})
    except Exception as e:
        logger.error(f"Erreur stop_network_scan: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
