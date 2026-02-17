# -*- coding: utf-8 -*-
"""
Module de gestion des statistiques de connexion des hôtes.
Utilise SQLite pour stocker les événements de déconnexion/reconnexion.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager
from src.utils.logger import get_logger
from src.utils.paths import AppPaths

logger = get_logger(__name__)


class ConnectionStatsManager:
    """Gestionnaire des statistiques de connexion avec base SQLite."""
    
    def __init__(self, db_path=None):
        """Initialise le gestionnaire avec le chemin de la base de données."""
        if db_path is None:
            # Utiliser le dossier bd/ existant
            self.db_path = os.path.join(str(AppPaths.get_base_dir()), "bd", "connection_stats.db")
        else:
            self.db_path = db_path
        
        # S'assurer que le dossier existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialiser la base de données
        self._init_db()
    
    def _init_db(self):
        """Crée les tables si elles n'existent pas."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table des événements de connexion
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS connection_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    hostname TEXT,
                    site TEXT DEFAULT '',
                    event_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration_seconds INTEGER DEFAULT NULL
                )
            ''')
            
            # Ajouter la colonne site si elle n'existe pas (migration)
            try:
                cursor.execute('ALTER TABLE connection_events ADD COLUMN site TEXT DEFAULT ""')
                logger.info("Colonne 'site' ajoutée à la table connection_events")
            except sqlite3.OperationalError:
                pass  # Colonne existe déjà
            
            # Index pour accélérer les requêtes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_ip ON connection_events(ip)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_timestamp ON connection_events(timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_type ON connection_events(event_type)
            ''')
            
            conn.commit()
            logger.info(f"Base de données de statistiques initialisée: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Contexte manager pour les connexions SQLite thread-safe."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def record_disconnect(self, ip: str, hostname: str = None, site: str = None):
        """Enregistre une déconnexion d'hôte."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO connection_events (ip, hostname, site, event_type, timestamp)
                    VALUES (?, ?, ?, 'disconnect', datetime('now', 'localtime'))
                ''', (ip, hostname or '', site or ''))
                conn.commit()
                logger.info(f"[STATS] Déconnexion enregistrée: {ip} ({hostname}) [site: {site or 'N/A'}]")
        except Exception as e:
            logger.error(f"Erreur enregistrement déconnexion {ip}: {e}")
    
    def record_reconnect(self, ip: str, hostname: str = None, site: str = None):
        """Enregistre une reconnexion et calcule la durée de la panne."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Trouver la dernière déconnexion pour cet hôte
                cursor.execute('''
                    SELECT id, timestamp FROM connection_events
                    WHERE ip = ? AND event_type = 'disconnect'
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (ip,))
                last_disconnect = cursor.fetchone()
                
                duration_seconds = None
                if last_disconnect:
                    try:
                        disconnect_time = datetime.strptime(
                            last_disconnect['timestamp'], 
                            '%Y-%m-%d %H:%M:%S'
                        )
                        now = datetime.now()
                        duration_seconds = int((now - disconnect_time).total_seconds())
                    except Exception as e:
                        logger.warning(f"Erreur calcul durée: {e}")
                
                # Enregistrer la reconnexion avec la durée
                cursor.execute('''
                    INSERT INTO connection_events (ip, hostname, site, event_type, timestamp, duration_seconds)
                    VALUES (?, ?, ?, 'reconnect', datetime('now', 'localtime'), ?)
                ''', (ip, hostname or '', site or '', duration_seconds))
                conn.commit()
                
                duration_str = f"{duration_seconds}s" if duration_seconds else "inconnue"
                logger.info(f"[STATS] Reconnexion enregistrée: {ip} ({hostname}) [site: {site or 'N/A'}] - durée panne: {duration_str}")
        except Exception as e:
            logger.error(f"Erreur enregistrement reconnexion {ip}: {e}")
    
    def get_overview_stats(self, days: int = 30) -> dict:
        """Retourne les statistiques globales."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cutoff = datetime.now() - timedelta(days=days)
                cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
                
                # Total déconnexions
                cursor.execute('''
                    SELECT COUNT(*) as count FROM connection_events
                    WHERE event_type = 'disconnect' AND timestamp >= ?
                ''', (cutoff_str,))
                total_disconnects = cursor.fetchone()['count']
                
                # Total reconnexions
                cursor.execute('''
                    SELECT COUNT(*) as count FROM connection_events
                    WHERE event_type = 'reconnect' AND timestamp >= ?
                ''', (cutoff_str,))
                total_reconnects = cursor.fetchone()['count']
                
                # Durée moyenne des pannes
                cursor.execute('''
                    SELECT AVG(duration_seconds) as avg_duration FROM connection_events
                    WHERE event_type = 'reconnect' AND duration_seconds IS NOT NULL AND timestamp >= ?
                ''', (cutoff_str,))
                avg_duration = cursor.fetchone()['avg_duration'] or 0
                
                # Durée totale des pannes
                cursor.execute('''
                    SELECT SUM(duration_seconds) as total_duration FROM connection_events
                    WHERE event_type = 'reconnect' AND duration_seconds IS NOT NULL AND timestamp >= ?
                ''', (cutoff_str,))
                total_duration = cursor.fetchone()['total_duration'] or 0
                
                # Hôtes uniques affectés
                cursor.execute('''
                    SELECT COUNT(DISTINCT ip) as count FROM connection_events
                    WHERE event_type = 'disconnect' AND timestamp >= ?
                ''', (cutoff_str,))
                unique_hosts = cursor.fetchone()['count']
                
                # Stats par période
                stats_24h = self._get_period_stats(conn, 1)
                stats_7d = self._get_period_stats(conn, 7)
                
                return {
                    'period_days': days,
                    'total_disconnects': total_disconnects,
                    'total_reconnects': total_reconnects,
                    'avg_duration_seconds': round(avg_duration, 0),
                    'total_downtime_seconds': total_duration,
                    'unique_hosts_affected': unique_hosts,
                    'stats_24h': stats_24h,
                    'stats_7d': stats_7d
                }
        except Exception as e:
            logger.error(f"Erreur récupération stats globales: {e}")
            return {}
    
    def _get_period_stats(self, conn, days: int) -> dict:
        """Statistiques pour une période donnée."""
        cursor = conn.cursor()
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM connection_events
            WHERE event_type = 'disconnect' AND timestamp >= ?
        ''', (cutoff_str,))
        disconnects = cursor.fetchone()['count']
        
        return {'disconnects': disconnects, 'period_days': days}
    
    def get_top_disconnectors(self, limit: int = 10, days: int = 30) -> list:
        """Retourne les hôtes avec le plus de déconnexions."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cutoff = datetime.now() - timedelta(days=days)
                cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('''
                    SELECT 
                        ip,
                        hostname,
                        site,
                        COUNT(*) as disconnect_count,
                        MAX(timestamp) as last_disconnect
                    FROM connection_events
                    WHERE event_type = 'disconnect' AND timestamp >= ?
                    GROUP BY ip
                    ORDER BY disconnect_count DESC
                    LIMIT ?
                ''', (cutoff_str, limit))
                
                results = []
                for row in cursor.fetchall():
                    # Calculer le temps total de panne pour cet hôte
                    cursor.execute('''
                        SELECT SUM(duration_seconds) as total FROM connection_events
                        WHERE ip = ? AND event_type = 'reconnect' 
                        AND duration_seconds IS NOT NULL AND timestamp >= ?
                    ''', (row['ip'], cutoff_str))
                    total_downtime = cursor.fetchone()['total'] or 0
                    
                    results.append({
                        'ip': row['ip'],
                        'hostname': row['hostname'] or row['ip'],
                        'site': row['site'] or '',
                        'disconnect_count': row['disconnect_count'],
                        'last_disconnect': row['last_disconnect'],
                        'total_downtime_seconds': total_downtime
                    })
                
                return results
        except Exception as e:
            logger.error(f"Erreur récupération top déconnecteurs: {e}")
            return []
    
    def get_host_stats(self, ip: str) -> dict:
        """Retourne les statistiques détaillées pour un hôte."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Infos générales
                cursor.execute('''
                    SELECT 
                        hostname,
                        COUNT(*) as total_events,
                        MIN(timestamp) as first_event,
                        MAX(timestamp) as last_event
                    FROM connection_events
                    WHERE ip = ?
                ''', (ip,))
                info = cursor.fetchone()
                
                if not info or info['total_events'] == 0:
                    return {'ip': ip, 'exists': False}
                
                # Nombre de déconnexions
                cursor.execute('''
                    SELECT COUNT(*) as count FROM connection_events
                    WHERE ip = ? AND event_type = 'disconnect'
                ''', (ip,))
                disconnect_count = cursor.fetchone()['count']
                
                # Durée moyenne et totale
                cursor.execute('''
                    SELECT 
                        AVG(duration_seconds) as avg_duration,
                        SUM(duration_seconds) as total_duration,
                        MIN(duration_seconds) as min_duration,
                        MAX(duration_seconds) as max_duration
                    FROM connection_events
                    WHERE ip = ? AND event_type = 'reconnect' AND duration_seconds IS NOT NULL
                ''', (ip,))
                durations = cursor.fetchone()
                
                return {
                    'ip': ip,
                    'exists': True,
                    'hostname': info['hostname'] or ip,
                    'first_event': info['first_event'],
                    'last_event': info['last_event'],
                    'disconnect_count': disconnect_count,
                    'avg_duration_seconds': round(durations['avg_duration'] or 0, 0),
                    'total_downtime_seconds': durations['total_duration'] or 0,
                    'min_duration_seconds': durations['min_duration'] or 0,
                    'max_duration_seconds': durations['max_duration'] or 0
                }
        except Exception as e:
            logger.error(f"Erreur récupération stats hôte {ip}: {e}")
            return {'ip': ip, 'exists': False, 'error': str(e)}
    
    def get_host_events(self, ip: str, limit: int = 50) -> list:
        """Retourne l'historique des événements pour un hôte."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, event_type, timestamp, duration_seconds
                    FROM connection_events
                    WHERE ip = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (ip, limit))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erreur récupération événements hôte {ip}: {e}")
            return []
    
    def get_recent_events(self, limit: int = 50) -> list:
        """Retourne les événements les plus récents."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, ip, hostname, site, event_type, timestamp, duration_seconds
                    FROM connection_events
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erreur récupération événements récents: {e}")
            return []
    
    def get_all_tracked_hosts(self) -> list:
        """Retourne la liste de tous les hôtes avec des événements."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ip, MAX(hostname) as hostname, MAX(site) as site
                    FROM connection_events
                    GROUP BY ip
                    ORDER BY ip
                ''')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erreur récupération liste hôtes: {e}")
            return []
    
    def reset_all_stats(self):
        """Supprime toutes les statistiques de la base de données."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM connection_events')
                conn.commit()
                deleted_count = cursor.rowcount
                logger.info(f"[STATS] Toutes les statistiques ont été réinitialisées ({deleted_count} événements supprimés)")
                return deleted_count
        except Exception as e:
            logger.error(f"Erreur réinitialisation statistiques: {e}")
            return 0


# Instance singleton
stats_manager = ConnectionStatsManager()
