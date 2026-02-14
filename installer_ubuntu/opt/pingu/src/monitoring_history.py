# -*- coding: utf-8 -*-
"""
Module de gestion de l'historique des données de monitoring (température et débit).
Stocke les données dans une base SQLite pour permettre l'affichage de graphiques.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MonitoringHistoryManager:
    """Gestionnaire d'historique des données de monitoring."""
    
    def __init__(self, db_path: str = None):
        """Initialise le gestionnaire avec le chemin de la base de données."""
        if db_path is None:
            # Chemin par défaut dans le dossier bd/
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bd_path = os.path.join(base_path, 'bd')
            os.makedirs(bd_path, exist_ok=True)
            db_path = os.path.join(bd_path, 'monitoring_history.db')
        
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        """Crée une connexion à la base de données."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialise les tables de la base de données."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Table historique température
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS temperature_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        value REAL NOT NULL
                    )
                ''')
                
                # Table historique débit
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bandwidth_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        in_mbps REAL NOT NULL,
                        out_mbps REAL NOT NULL
                    )
                ''')
                
                # Index pour accélérer les requêtes
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_temp_ip_ts 
                    ON temperature_history(ip, timestamp)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_bw_ip_ts 
                    ON bandwidth_history(ip, timestamp)
                ''')
                
                conn.commit()
                logger.info(f"Base de données monitoring initialisée: {self.db_path}")
        except Exception as e:
            logger.error(f"Erreur initialisation BDD monitoring: {e}")
    
    def record_temperature(self, ip: str, value: float):
        """Enregistre une mesure de température."""
        if value is None:
            return
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO temperature_history (ip, timestamp, value)
                    VALUES (?, datetime('now', 'localtime'), ?)
                ''', (ip, float(value)))
                conn.commit()
        except Exception as e:
            logger.debug(f"Erreur enregistrement température {ip}: {e}")
    
    def record_bandwidth(self, ip: str, in_mbps: float, out_mbps: float):
        """Enregistre une mesure de débit."""
        if in_mbps is None and out_mbps is None:
            return
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO bandwidth_history (ip, timestamp, in_mbps, out_mbps)
                    VALUES (?, datetime('now', 'localtime'), ?, ?)
                ''', (ip, float(in_mbps or 0), float(out_mbps or 0)))
                conn.commit()
        except Exception as e:
            logger.debug(f"Erreur enregistrement débit {ip}: {e}")
    
    def get_temperature_history(self, ip: str, hours: int = 24) -> List[Dict]:
        """Récupère l'historique de température pour un hôte."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cutoff = datetime.now() - timedelta(hours=hours)
                cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('''
                    SELECT timestamp, value
                    FROM temperature_history
                    WHERE ip = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (ip, cutoff_str))
                
                return [
                    {'timestamp': row['timestamp'], 'value': row['value']}
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Erreur lecture historique température {ip}: {e}")
            return []
    
    def get_bandwidth_history(self, ip: str, hours: int = 24) -> List[Dict]:
        """Récupère l'historique de débit pour un hôte."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cutoff = datetime.now() - timedelta(hours=hours)
                cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('''
                    SELECT timestamp, in_mbps, out_mbps
                    FROM bandwidth_history
                    WHERE ip = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (ip, cutoff_str))
                
                return [
                    {
                        'timestamp': row['timestamp'],
                        'in_mbps': row['in_mbps'],
                        'out_mbps': row['out_mbps']
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Erreur lecture historique débit {ip}: {e}")
            return []
    
    def get_hosts_with_data(self) -> Dict[str, Dict]:
        """Retourne la liste des hôtes ayant des données disponibles."""
        result = {}
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Hôtes avec données de température
                cursor.execute('''
                    SELECT DISTINCT ip, MAX(timestamp) as last_update
                    FROM temperature_history
                    GROUP BY ip
                ''')
                for row in cursor.fetchall():
                    ip = row['ip']
                    if ip not in result:
                        result[ip] = {'has_temperature': False, 'has_bandwidth': False}
                    result[ip]['has_temperature'] = True
                    result[ip]['temp_last_update'] = row['last_update']
                
                # Hôtes avec données de débit
                cursor.execute('''
                    SELECT DISTINCT ip, MAX(timestamp) as last_update
                    FROM bandwidth_history
                    GROUP BY ip
                ''')
                for row in cursor.fetchall():
                    ip = row['ip']
                    if ip not in result:
                        result[ip] = {'has_temperature': False, 'has_bandwidth': False}
                    result[ip]['has_bandwidth'] = True
                    result[ip]['bw_last_update'] = row['last_update']
                
        except Exception as e:
            logger.error(f"Erreur liste hôtes monitoring: {e}")
        
        return result
    
    def cleanup_old_data(self, days: int = 7):
        """Supprime les données plus anciennes que le nombre de jours spécifié."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cutoff = datetime.now() - timedelta(days=days)
                cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute(
                    'DELETE FROM temperature_history WHERE timestamp < ?',
                    (cutoff_str,)
                )
                temp_deleted = cursor.rowcount
                
                cursor.execute(
                    'DELETE FROM bandwidth_history WHERE timestamp < ?',
                    (cutoff_str,)
                )
                bw_deleted = cursor.rowcount
                
                conn.commit()
                
                if temp_deleted > 0 or bw_deleted > 0:
                    logger.info(f"Nettoyage monitoring: {temp_deleted} temp, {bw_deleted} bw supprimés")
                    
        except Exception as e:
            logger.error(f"Erreur nettoyage données monitoring: {e}")


# Instance globale
monitoring_manager = None

def get_monitoring_manager() -> MonitoringHistoryManager:
    """Retourne l'instance globale du gestionnaire de monitoring."""
    global monitoring_manager
    if monitoring_manager is None:
        monitoring_manager = MonitoringHistoryManager()
    return monitoring_manager
