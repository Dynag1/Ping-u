from flask import Blueprint, request, jsonify, session, send_file
from src.web_auth import WebAuth
from src.utils.logger import get_logger
import zipfile
import io
import os
import datetime

logger = get_logger(__name__)

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/api/admin/backup')
@WebAuth.login_required
def admin_backup():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Accès refusé'}), 403
    
    try:
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists('web_users.json'): zf.write('web_users.json', 'web_users.json')
            if os.path.exists('sites.pkl'): zf.write('sites.pkl', 'sites.pkl')
            bd_tabs_dir = os.path.join('bd', 'tabs')
            if os.path.exists(bd_tabs_dir):
                for filename in os.listdir(bd_tabs_dir):
                    file_path = os.path.join(bd_tabs_dir, filename)
                    if os.path.isfile(file_path):
                        zf.write(file_path, os.path.join('bd', 'tabs', filename))
            autosave_path = os.path.join('bd', 'autosave.pin')
            if os.path.exists(autosave_path): zf.write(autosave_path, os.path.join('bd', 'autosave.pin'))
            synoptic_json = os.path.join('bd', 'synoptic.json')
            if os.path.exists(synoptic_json): zf.write(synoptic_json, os.path.join('bd', 'synoptic.json'))
            synoptic_png = os.path.join('bd', 'synoptic.png')
            if os.path.exists(synoptic_png): zf.write(synoptic_png, os.path.join('bd', 'synoptic.png'))

        memory_file.seek(0)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pingu_backup_{timestamp}.pingu"
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"Erreur backup: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@backup_bp.route('/api/admin/restore', methods=['POST'])
@WebAuth.login_required
def admin_restore():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Accès refusé'}), 403
    try:
        if 'backup_file' not in request.files: return jsonify({'success': False}), 400
        file = request.files['backup_file']
        with zipfile.ZipFile(file, 'r') as zf:
            for member in zf.infolist():
                if '..' in member.filename or member.filename.startswith('/'):
                    raise Exception(f"Chemin suspect: {member.filename}")
            zf.extractall('.')
        return jsonify({'success': True, 'message': 'Restauration terminée. Redémarrez l\'app.'})
    except Exception as e:
        logger.error(f"Erreur restauration: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
