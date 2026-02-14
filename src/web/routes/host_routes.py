from flask import Blueprint, request, jsonify, current_app
from src.web_auth import WebAuth
from src.utils.logger import get_logger
from src.utils.headless_compat import QStandardItem
import threading

logger = get_logger(__name__)

host_bp = Blueprint('host', __name__)

@host_bp.route('/api/hosts')
def get_hosts():
    server = current_app.config['WEB_SERVER']
    hosts = server._get_hosts_data(apply_filter=False)
    return jsonify(hosts)

@host_bp.route('/api/delete_host', methods=['POST'])
@WebAuth.login_required
def delete_host():
    try:
        data = request.get_json()
        ip = data.get('ip')
        main_window = current_app.config['MAIN_WINDOW']
        model = main_window.treeIpModel
        for row in range(model.rowCount()):
            item = model.item(row, 1)
            if item and item.text() == ip:
                model.removeRow(row)
                current_app.config['WEB_SERVER'].broadcast_update()
                return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Hôte non trouvé'}), 404
    except Exception as e:
        logger.error(f"Erreur delete_host: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@host_bp.route('/api/exclude_host', methods=['POST'])
@WebAuth.login_required
def exclude_host():
    try:
        data = request.get_json()
        ip = data.get('ip')
        main_window = current_app.config['MAIN_WINDOW']
        model = main_window.treeIpModel
        for row in range(model.rowCount()):
            item_ip = model.item(row, 1)
            if item_ip and item_ip.text() == ip:
                model.setItem(row, 10, QStandardItem("x"))
                latence_item = model.item(row, 5)
                if latence_item: latence_item.setText("EXCLU")
                current_app.config['WEB_SERVER'].broadcast_update()
                return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Hôte non trouvé'}), 404
    except Exception as e:
        logger.error(f"Erreur exclude_host: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@host_bp.route('/api/update_comment', methods=['POST'])
@WebAuth.any_login_required
def update_comment():
    try:
        data = request.get_json()
        ip, comment = data.get('ip'), data.get('comment')
        main_window = current_app.config['MAIN_WINDOW']
        model = main_window.treeIpModel
        for row in range(model.rowCount()):
            item_ip = model.item(row, 1)
            if item_ip and item_ip.text() == ip:
                model.setItem(row, 9, QStandardItem(comment))
                current_app.config['WEB_SERVER'].broadcast_update()
                return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'IP non trouvée'}), 404
    except Exception as e:
        logger.error(f"Erreur update_comment: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
@host_bp.route('/api/update_host_name', methods=['POST'])
@WebAuth.any_login_required
def update_host_name():
    try:
        data = request.get_json()
        ip, name = data.get('ip'), data.get('name')
        main_window = current_app.config['MAIN_WINDOW']
        model = main_window.treeIpModel
        for row in range(model.rowCount()):
            item_ip = model.item(row, 1)
            if item_ip and item_ip.text() == ip:
                model.setItem(row, 2, QStandardItem(name))
                current_app.config['WEB_SERVER'].broadcast_update()
                return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'IP non trouvée'}), 404
    except Exception as e:
        logger.error(f"Erreur update_host_name: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@host_bp.route('/api/clear_all', methods=['POST'])
@WebAuth.login_required
def clear_all():
    try:
        main_window = current_app.config['MAIN_WINDOW']
        model = main_window.treeIpModel
        model.removeRows(0, model.rowCount())
        current_app.config['WEB_SERVER'].broadcast_update()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur clear_all: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@host_bp.route('/api/remove_duplicates', methods=['POST'])
@WebAuth.login_required
def remove_duplicates():
    try:
        from src import fct
        main_window = current_app.config['MAIN_WINDOW']
        fct.remove_duplicates(main_window.treeIpModel)
        current_app.config['WEB_SERVER'].broadcast_update()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur remove_duplicates: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
