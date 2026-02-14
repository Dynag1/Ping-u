import sqlite3
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)

DB_PATH = os.path.join("bd", "pingu.db")

def get_db_connection():
    """Crée et retourne une connexion à la base de données SQLite"""
    try:
        # Assurer que le dossier existe
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        return None

def init_db():
    """Initialise la structure de la base de données"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            must_change_password BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # Table des tableaux de bord personnalisés
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')

        # Items des tableaux de bord (liés par IP)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dashboard_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dashboard_id INTEGER NOT NULL,
            host_ip TEXT NOT NULL,
            FOREIGN KEY(dashboard_id) REFERENCES dashboards(id) ON DELETE CASCADE
        )
        ''')

        # Paramètres spécifiques par hôte (Notifications granulaires)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS host_settings (
            host_ip TEXT PRIMARY KEY,
            email_enabled BOOLEAN DEFAULT 1,
            telegram_enabled BOOLEAN DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        logger.info("Base de données initialisée avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        return False
    finally:
        conn.close()

# --- Fonctions pour les paramètres hôte (Notifications Granulaires) ---

def get_host_notification_settings(ip):
    """
    Récupère les paramètres de notification pour une IP.
    Retourne un dict {'email': bool, 'telegram': bool}.
    Par défaut True si non défini.
    """
    conn = get_db_connection()
    if not conn:
        return {'email': True, 'telegram': True}
        
    try:
        row = conn.execute('SELECT email_enabled, telegram_enabled FROM host_settings WHERE host_ip = ?', (ip,)).fetchone()
        if row:
            return {
                'email': bool(row['email_enabled']),
                'telegram': bool(row['telegram_enabled'])
            }
        return {'email': True, 'telegram': True} # Défaut: activé
    except Exception as e:
        logger.error(f"Erreur lecture settings host {ip}: {e}")
        return {'email': True, 'telegram': True}
    finally:
        conn.close()

def set_host_notification_settings(ip, email_enabled, telegram_enabled):
    """Définit les paramètres de notification pour une IP"""
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        conn.execute('''
        INSERT INTO host_settings (host_ip, email_enabled, telegram_enabled, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(host_ip) DO UPDATE SET
            email_enabled = excluded.email_enabled,
            telegram_enabled = excluded.telegram_enabled,
            updated_at = CURRENT_TIMESTAMP
        ''', (ip, email_enabled, telegram_enabled))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Erreur écriture settings host {ip}: {e}")
        return False
    finally:
        conn.close()

# --- Fonctions pour les tableaux de bord ---

def create_dashboard(name, user_id=None):
    """Crée un nouveau tableau de bord"""
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.execute('INSERT INTO dashboards (name, user_id) VALUES (?, ?)', (name, user_id))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"Erreur création dashboard: {e}")
        return None
    finally:
        conn.close()

def get_dashboards(user_id=None):
    """Récupère tous les tableaux de bord (optionnel: filtre par user)"""
    conn = get_db_connection()
    if not conn: return []
    try:
        # Pour l'instant on ignore user_id car le système d'auth est global (admin/user partagent la même vue admin)
        # Mais on garde la structure pour le futur.
        dashboards = conn.execute('SELECT * FROM dashboards ORDER BY created_at DESC').fetchall()
        
        result = []
        for d in dashboards:
            items = conn.execute('SELECT host_ip FROM dashboard_items WHERE dashboard_id = ?', (d['id'],)).fetchall()
            d_dict = dict(d)
            d_dict['hosts'] = [item['host_ip'] for item in items]
            result.append(d_dict)
        return result
    except Exception as e:
        logger.error(f"Erreur lecture dashboards: {e}")
        return []
    finally:
        conn.close()

def get_dashboard(dashboard_id):
    """Récupère un tableau de bord par ID"""
    conn = get_db_connection()
    if not conn: return None
    try:
        d = conn.execute('SELECT * FROM dashboards WHERE id = ?', (dashboard_id,)).fetchone()
        if not d: return None
        
        items = conn.execute('SELECT host_ip FROM dashboard_items WHERE dashboard_id = ?', (dashboard_id,)).fetchall()
        d_dict = dict(d)
        d_dict['hosts'] = [item['host_ip'] for item in items]
        return d_dict
    except Exception as e:
        logger.error(f"Erreur lecture dashboard {dashboard_id}: {e}")
        return None
    finally:
        conn.close()

def update_dashboard(dashboard_id, name, hosts):
    """Met à jour un tableau de bord (nom et liste d'hôtes)"""
    conn = get_db_connection()
    if not conn: return False
    try:
        conn.execute('UPDATE dashboards SET name = ? WHERE id = ?', (name, dashboard_id))
        
        # Remplacer les items
        conn.execute('DELETE FROM dashboard_items WHERE dashboard_id = ?', (dashboard_id,))
        if hosts:
            items = [(dashboard_id, ip) for ip in hosts]
            conn.executemany('INSERT INTO dashboard_items (dashboard_id, host_ip) VALUES (?, ?)', items)
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Erreur update dashboard {dashboard_id}: {e}")
        return False
    finally:
        conn.close()

def delete_dashboard(dashboard_id):
    """Supprime un tableau de bord"""
    conn = get_db_connection()
    if not conn: return False
    try:
        conn.execute('DELETE FROM dashboards WHERE id = ?', (dashboard_id,))
        # Les items sont supprimés par CASCADE
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Erreur suppression dashboard {dashboard_id}: {e}")
        return False
    finally:
        conn.close()
