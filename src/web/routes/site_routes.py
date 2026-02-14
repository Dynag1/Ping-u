from flask import Blueprint, request, jsonify, current_app
from src.web_auth import WebAuth
from src.utils.logger import get_logger
from src.utils.headless_compat import QStandardItem
from src import var, db

logger = get_logger(__name__)

site_bp = Blueprint('site', __name__)

@site_bp.route('/api/get_sites')
@WebAuth.any_login_required
def get_sites():
    try:
        main_window = current_app.config['MAIN_WINDOW']
        model = main_window.treeIpModel
        dynamic_sites = set()
        for row in range(model.rowCount()):
            s = model.item(row, 8).text() if model.item(row, 8) else ''
            if s: dynamic_sites.add(s)
        all_sites = sorted(list(set(var.sites_list) | dynamic_sites))
        return jsonify({
            'success': True,
            'sites': all_sites,
            'sites_actifs': var.sites_actifs,
            'site_filter': var.site_filter
        })
    except Exception as e:
        logger.error(f"Erreur get_sites: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@site_bp.route('/api/add_site', methods=['POST'])
@WebAuth.login_required
def add_site():
    try:
        data = request.get_json()
        site_name = data.get('name', '').strip()
        if not site_name: return jsonify({'success': False}), 400
        if site_name in var.sites_list: return jsonify({'success': False, 'error': 'Existe déjà'}), 400
        var.sites_list.append(site_name)
        db.save_sites()
        return jsonify({'success': True, 'sites': var.sites_list})
    except Exception as e:
        logger.error(f"Erreur add_site: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@site_bp.route('/api/set_site_filter', methods=['POST'])
@WebAuth.login_required
def set_site_filter():
    try:
        data = request.get_json()
        var.site_filter = data.get('sites', [])
        db.save_sites()
        current_app.config['WEB_SERVER'].broadcast_update()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur set_site_filter: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
