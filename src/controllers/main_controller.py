from src import var
from src.fcy_ping import PingManager
from src.core.alert_manager import AlertManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MainController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.ui = main_window.ui
        self.ping_manager = None
        self.alert_manager = None

    def toggle_monitoring(self):
        """Gère le démarrage et l'arrêt du monitoring (Ping + Alertes)."""
        if self.ui.butStart.isChecked():
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """Démarre tous les services de monitoring."""
        try:
            # Recharger les paramètres d'alerte depuis la DB pour être sûr
            try:
                from src import db
                db.lire_param_db()
                logger.info(f"Paramètres chargés: Mail={var.mail}, Telegram={var.telegram}, Popup={var.popup}")
            except Exception as e:
                logger.error(f"Erreur rechargement paramètres DB: {e}")

            logger.info(f"Démarrage monitoring (délai: {var.delais}s, seuil HS: {var.nbrHs})")
            
            if self.ping_manager is not None or var.tourne:
                self.stop_monitoring()
                try:
                    from src.utils.headless_compat import QThread
                    if QThread.__name__ == 'QThread' and hasattr(QThread, 'msleep'):
                        QThread.msleep(500)
                    else:
                        import time
                        time.sleep(0.5)
                except:
                    import time
                    time.sleep(0.5)
            
            # Réinitialiser le stop_event pour permettre aux nouveaux threads de fonctionner
            var.stop_event.clear()
            
            # Réinitialiser les listes d'alertes
            var.liste_hs.clear()
            var.liste_mail.clear()
            var.liste_telegram.clear()
            var.liste_temp_alert.clear()
            
            # Instanciation des managers
            # Note: PingManager est maintenant découplé du modèle Qt
            self.ping_manager = PingManager(
                get_ips_callback=self.get_ips_to_monitor,
                main_window=self.main_window
            )
            # Connexion des signaux de résultat
            self.ping_manager.result_signal.connect(self.on_monitoring_result)
            
            self.alert_manager = AlertManager(
                self.main_window,
                get_host_metadata_callback=self.get_host_metadata,
                get_all_hosts_data_callback=self.get_all_hosts_data
            )
            
            var.tourne = True
            self.ping_manager.start()
            self.alert_manager.start()
            
            # Mise à jour UI - bloquer les signaux pour éviter les triggers en cascade
            self.ui.butStart.blockSignals(True)
            self.ui.butStart.setChecked(True)
            self.ui.butStart.blockSignals(False)
            self.ui.butStart.setStyleSheet(f"background-color: {var.couleur_rouge}; color: black;")
            self.ui.butStart.setText("Stop")
            
        except Exception as e:
            logger.error(f"Erreur démarrage monitoring: {e}", exc_info=True)
            # En cas d'erreur, on remet l'état visuel à l'arrêt
            self.ui.butStart.blockSignals(True)
            self.ui.butStart.setChecked(False)
            self.ui.butStart.blockSignals(False)
            self.stop_monitoring()

    def stop_monitoring(self):
        """Arrête tous les services de monitoring."""
        try:
            logger.info("Arrêt du monitoring via MainController")
            
            # 1. Signaler l'arrêt à tous les threads via stop_event (AVANT de mettre tourne à False)
            # Cela permet aux threads utilisant stop_event.wait() de s'arrêter immédiatement
            var.stop_event.set()
            var.tourne = False
            
            # 2. Arrêter d'abord l'alert manager (qui gère aussi le thread mail recap)
            if self.alert_manager:
                self.alert_manager.stop()
                self.alert_manager = None
            
            # 3. Puis arrêter le ping manager (plus complexe, avec QThread)
            if self.ping_manager:
                self.ping_manager.stop()
                # Traiter les événements Qt en attente pour laisser le temps au thread de se terminer
                from src.utils.headless_compat import QCoreApplication
                QCoreApplication.processEvents()
                self.ping_manager = None
            
            logger.info("Tous les services de monitoring arrêtés")
                
            # Mise à jour UI
            # On vérifie si l'UI existe encore (cas de fermeture)
            if hasattr(self.ui, 'butStart'):
                # Bloquer les signaux pour éviter les triggers en cascade
                self.ui.butStart.blockSignals(True)
                self.ui.butStart.setChecked(False)
                self.ui.butStart.blockSignals(False)
                self.ui.butStart.setStyleSheet(f"background-color: {var.couleur_vert}; color: black;")
                self.ui.butStart.setText("Start")
                    
        except Exception as e:
            logger.error(f"Erreur arrêt monitoring: {e}", exc_info=True)
    def get_ips_to_monitor(self):
        """Callback pour fournir la liste des IPs à monitorer au PingManager."""
        ips_set = set()
        try:
            model = self.main_window.treeIpModel
            for row in range(model.rowCount()):
                item = model.item(row, 1) # Colonne IP
                if item:
                    ip_text = item.text().strip()
                    if not ip_text: continue
                    
                    # Filtrage par sites actifs
                    if var.sites_actifs:
                        site_item = model.item(row, 8) # Colonne Site
                        host_site = site_item.text().strip() if site_item else ''
                        if host_site not in var.sites_actifs:
                            continue
                    
                    ips_set.add(ip_text)
        except Exception as e:
            logger.error(f"Erreur get_ips_to_monitor: {e}")
        return list(ips_set)

    def on_monitoring_result(self, ip, latency, color, temperature, bandwidth):
        """Gère le résultat d'un ping ou d'une mise à jour SNMP et met à jour le modèle Qt."""
        try:
            from src.utils.headless_compat import QStandardItem, QBrush, QColor, Qt
            from src.utils.colors import AppColors
            
            model = self.main_window.treeIpModel
            row = self.find_item_row(ip)
            if row == -1: return

            # Vérifier l'exclusion
            is_excluded = False
            item_excl = model.item(row, 10)
            if item_excl and item_excl.text() == "x":
                is_excluded = True

            # Mise à jour Latence (si latency >= 0)
            if latency >= 0:
                item_lat = model.item(row, 5)
                if not item_lat:
                    item_lat = QStandardItem()
                    model.setItem(row, 5, item_lat)
                
                if is_excluded:
                    latency_text = f"{latency:.1f} ms" if latency < 500 else "HS"
                    item_lat.setText(f"{latency_text}")
                else:
                    # Si latence HS (>= 500)
                    if latency >= 500:
                        # Si la couleur est ORANGE (Warning), c'est une vérification en cours (non confirmé)
                        if color == AppColors.ORANGE_PALE:
                            item_lat.setText("Verif...")
                        else:
                            item_lat.setText("HS")
                    else:
                        item_lat.setText(f"{latency:.1f} ms")
            
            # Cas spécial : SNMP OK (latency = -1.0)
            elif latency == -1.0:
                item_lat = model.item(row, 5)
                if not item_lat:
                    item_lat = QStandardItem()
                    model.setItem(row, 5, item_lat)
                
                # On ne change pas le texte de latence (on garde HS ou le temps de réponse)
                # Sauf si c'était vide, on peut mettre "SNMP" ou similaire
                if item_lat.text() == "":
                    item_lat.setText("Alive")

            # Mise à jour Température (si temperature n'est pas None)
            if temperature is not None:
                item_temp = model.item(row, 6)
                if not item_temp:
                    item_temp = QStandardItem()
                    model.setItem(row, 6, item_temp)
                
                temp_str = str(temperature)
                item_temp.setText(f"{temp_str}°C")
                
                # Couleur selon seuil
                try:
                    temp_val = float(temperature)
                    if temp_val >= var.tempSeuil:
                        item_temp.setBackground(QBrush(QColor(AppColors.ROUGE_PALE)))
                    elif temp_val >= var.tempSeuilWarning:
                        item_temp.setBackground(QBrush(QColor(AppColors.ORANGE_PALE)))
                    else:
                        item_temp.setBackground(QBrush(Qt.NoBrush))
                except (ValueError, TypeError):
                    pass

            # Coloration de la ligne (si latence mise à jour et non exclusion)
            if latency >= 0 or (latency == -1.0 and color):
                for col in range(model.columnCount()):
                    if col == 6: continue # On ne touche pas au fond de la température si géré spécifiquement
                    item = model.item(row, col)
                    if not item:
                        item = QStandardItem()
                        model.setItem(row, col, item)
                    
                    if is_excluded:
                        item.setForeground(QBrush(QColor("gray")))
                        if latency < 500:
                            item.setBackground(QBrush(QColor(240, 240, 240)))
                        else:
                            item.setBackground(QBrush(QColor(255, 240, 240)))
                    else:
                        if color:
                            item.setBackground(QBrush(QColor(color)))
                        item.setForeground(QBrush(QColor("black")))

            # Synchronisation Thread-Safe avec HostManager pour le serveur Web
            if hasattr(self.main_window, 'host_manager'):
                try:
                    # Récupérer l'état actuel de l'hôte pour ne pas tout écraser si latency = -1
                    current_host = self.main_window.host_manager.get_host_by_ip(ip)
                    
                    lat_text = current_host.get('latence', 'HS') if current_host else "HS"
                    status = current_host.get('status', 'offline') if current_host else "offline"
                    
                    # Mise à jour seulement si c'est un résultat de Ping (latency >= 0)
                    if latency >= 0:
                        status = "offline"
                        lat_text = "HS"
                        if not is_excluded and latency < 500:
                            lat_text = f"{latency:.1f} ms"
                            status = "online"
                    
                    # Mise à jour HostManager
                    self.main_window.host_manager.update_host_status(
                        ip, 
                        lat_text, 
                        status, 
                        str(temperature) if temperature is not None else (current_host.get('temp') if current_host else None)
                    )
                except Exception as hm_err:
                    logger.error(f"Erreur update HostManager: {hm_err}")

        except Exception as e:
            logger.error(f"Erreur on_monitoring_result pour {ip}: {e}")

    def find_item_row(self, ip):
        """Trouve la ligne correspondant à l'IP dans le modèle."""
        model = self.main_window.treeIpModel
        for row in range(model.rowCount()):
            item = model.item(row, 1)
            if item and item.text() == ip:
                return row
        return -1

    def get_host_metadata(self, ip):
        """Récupère les métadonnées pour un hôte spécifique."""
        metadata = {'ip': ip}
        try:
            row = self.find_item_row(ip)
            if row != -1:
                model = self.main_window.treeIpModel
                metadata['nom'] = model.item(row, 2).text() if model.item(row, 2) else ""
                metadata['mac'] = model.item(row, 3).text() if model.item(row, 3) else ""
                metadata['site'] = model.item(row, 8).text() if model.item(row, 8) else ""
                metadata['latence'] = model.item(row, 5).text() if model.item(row, 5) else ""
                metadata['temp'] = model.item(row, 6).text() if model.item(row, 6) else ""
        except Exception as e:
            logger.error(f"Erreur get_host_metadata pour {ip}: {e}")
        return metadata

    def get_all_hosts_data(self):
        """Récupère les données de tous les hôtes du modèle."""
        all_data = []
        try:
            model = self.main_window.treeIpModel
            for row in range(model.rowCount()):
                ip_item = model.item(row, 1)
                if ip_item:
                    ip = ip_item.text()
                    all_data.append(self.get_host_metadata(ip))
        except Exception as e:
            logger.error(f"Erreur get_all_hosts_data: {e}")
        return all_data
