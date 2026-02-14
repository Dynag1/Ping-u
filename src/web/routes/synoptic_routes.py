from flask import Blueprint, jsonify, request, send_file, current_app
from src.web_auth import WebAuth
from src.utils.logger import get_logger
import os
import json

logger = get_logger(__name__)
synoptic_bp = Blueprint('synoptic', __name__)

# Définition des chemins absolus
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
CONFIG_FILE = os.path.join(BASE_DIR, "bd", "synoptic.json")
IMAGE_FILE = os.path.join(BASE_DIR, "bd", "synoptic.png")

@synoptic_bp.route('/api/synoptic/config', methods=['GET'])
@WebAuth.any_login_required
def get_config():
    try:
        if os.path.exists(CONFIG_FILE):
             with open(CONFIG_FILE, 'r') as f:
                 config = json.load(f)
             return jsonify({'success': True, 'config': config})
        return jsonify({'success': True, 'config': {}})
    except Exception as e:
        logger.error(f"Error reading synoptic config: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@synoptic_bp.route('/api/synoptic/config', methods=['POST'])
@WebAuth.login_required
def save_config():
    try:
        data = request.get_json()
        # S'assurer que le répertoire bd existe
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving synoptic config: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@synoptic_bp.route('/api/synoptic/image', methods=['GET'])
@WebAuth.any_login_required
def get_image():
    try:
        if os.path.exists(IMAGE_FILE):
            return send_file(IMAGE_FILE, mimetype='image/png')
        return "Image not found", 404
    except Exception as e:
        logger.error(f"Error serving synoptic image: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@synoptic_bp.route('/api/synoptic/upload', methods=['POST'])
@WebAuth.login_required
def upload_image():
    try:
        if 'map_image' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400
        
        file = request.files['map_image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
            
        if file:
            # S'assurer que le répertoire bd existe
            os.makedirs(os.path.dirname(IMAGE_FILE), exist_ok=True)
            file.save(IMAGE_FILE)
            logger.info(f"Image synoptique sauvegardée: {IMAGE_FILE}")
            return jsonify({'success': True})
            
    except Exception as e:
        logger.error(f"Error uploading synoptic image: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
