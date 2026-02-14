from flask import Blueprint, jsonify, request
import threading

notification_bp = Blueprint('notification', __name__)

# Cette variable sera initialisée plus tard
notification_manager = None

@notification_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    global notification_manager
    if not notification_manager:
        from src.web_server import notification_manager as nm
        notification_manager = nm

    limit = int(request.args.get('limit', 20))
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    notifications = notification_manager.get_notifications(limit=limit, unread_only=unread_only)
    return jsonify(notifications)

@notification_bp.route('/api/notifications/mark_read', methods=['POST'])
def mark_read():
    global notification_manager
    if not notification_manager:
        from src.web_server import notification_manager as nm
        notification_manager = nm
    
    data = request.json or {}
    notif_id = data.get('id')
    count = notification_manager.mark_as_read(notif_id)
    return jsonify({'success': True, 'count': count})

@notification_bp.route('/api/notifications/clear', methods=['POST'])
def clear_notifications():
    global notification_manager
    if not notification_manager:
        from src.web_server import notification_manager as nm
        notification_manager = nm
        
    notification_manager.clear_notifications()
    return jsonify({'success': True})
