// ==================== Menu Hamburger ====================
function toggleMenu() {
    const sideMenu = document.getElementById('side-menu');
    const overlay = document.getElementById('menu-overlay');
    const hamburgerBtn = document.getElementById('hamburger-btn');

    sideMenu.classList.toggle('active');
    overlay.classList.toggle('active');
    hamburgerBtn.classList.toggle('active');
}

// Fermer le menu avec la touche Escape
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        const sideMenu = document.getElementById('side-menu');
        if (sideMenu && sideMenu.classList.contains('active')) {
            toggleMenu();
        }
        // Also close any active modals
        document.querySelectorAll('.section-modal.active').forEach(modal => {
            const sectionId = modal.id.replace('modal-', '');
            closeSectionModal(sectionId);
        });
    }
});

// ==================== Système de traduction ====================
const translations = {
    fr: {
        admin_title: "Administration - Ping ü",
        menu: "Menu",
        language: "Langue",
        status: "Statut",
        actions: "Actions",
        sections: "Sections",
        menu_home: "Accueil",
        menu_synoptic: "Synoptique",
        menu_monitoring: "Graphiques",
        menu_user_section: "Utilisateur",
        menu_parameters: "Paramètres",
        welcome_title: "Bienvenue dans l'administration",
        welcome_desc: "Gérez vos hôtes, configurez les alertes et supervisez votre réseau depuis cette interface.",
        quick_actions: "Actions rapides",
        navigation: "Navigation",
        change_credentials: "Changer identifiants",
        monitoring_view: "Vue Monitoring",
        logout: "Déconnexion",
        status_running: "En cours",
        status_stopped: "Arrêté",
        manage_users_title: "Gestion des Utilisateurs",
        admin_user: "Administrateur",
        standard_user: "Utilisateur",
        admin_role: "Rôle Admin",
        admin_role_desc: "Accès complet à l'administration",
        user_role: "Rôle Utilisateur",
        user_role_desc: "Accès à la vue monitoring uniquement",
        change_credentials_title: "Changer les identifiants",
        current_password: "Mot de passe actuel",
        new_username: "Nouveau nom d'utilisateur",
        new_password: "Nouveau mot de passe",
        user_credentials_changed: "Identifiants utilisateur modifiés",
        save: "Enregistrer",
        cancel: "Annuler",
        total_hosts: "Total Hôtes",
        online: "En ligne",
        offline: "Hors ligne",
        delay_sec: "Délai",
        add_hosts: "Ajout d'Hôtes",
        add_hosts_desc: "Scanner et ajouter des hôtes",
        monitoring_desc: "Démarrer/arrêter et configurer",
        backup_restore_title: "Sauvegarde & Restauration",
        backup_restore_desc: "Gérez les sauvegardes de votre configuration compléte",
        backup_title: "Sauvegarder",
        backup_desc: "Téléchargez une archive complète (.pingu) contenant :",
        download_backup: "Télécharger la sauvegarde",
        restore_title: "Restaurer",
        restore_desc: "Restaurez une configuration depuis un fichier .pingu.",
        restore_btn: "Restaurer la sauvegarde",
        alerts_desc: "Email, Telegram, popup",
        actions_desc: "Import, export, nettoyage",
        base_ip: "Adresse IP de base",
        hosts_count: "Nombre d'hôtes",
        scan_type: "Type de scan",
        scan_alive: "Alive (actifs uniquement)",
        scan_all: "Tous les hôtes",
        scan_site: "Site spécifique",
        scan_hosts: "Scanner les hôtes",
        assign_to_site: "Assigner au site",
        monitoring_control: "Contrôle du Monitoring",
        ping_delay: "Délai entre pings (sec)",
        hs_before_alert: "Nombre de HS avant alerte",
        start: "Démarrer",
        stop: "Arrêter",
        alerts_config: "Configuration des Alertes",
        alert_popup: "Popup (notification visuelle)",
        alert_email: "Email d'alerte",
        alert_recap: "Email récapitulatif",
        alert_db: "Base de données externe",
        alert_temp: "Alerte température élevée",
        temp_threshold: "Seuil critique (°C)",
        temp_threshold_warning: "Seuil de warning (°C)",
        alert_if_temp: "Alerte + Visuel si température ≥ seuil critique",
        alert_if_temp_warning: "Visuel uniquement si température ≥ seuil de warning",
        save_alerts: "Sauvegarder les alertes",
        quick_actions: "Actions Rapides",
        clear_all: "Tout effacer",
        remove_duplicates: "Suppr. doublons",
        export_csv: "Exporter CSV",
        import_csv: "Importer CSV",
        export_xls: "Exporter Excel",
        import_xls: "Importer Excel",
        export_xls_started: "Export Excel démarré",
        import_xls_success: "Import Excel réussi",
        // Gestion des sites
        sites_management: "Gestion des Sites",
        sites_subtitle: "Organisez vos hôtes par localisation",
        display_filter: "Affichage",
        filter_desc: "Sites visibles dans le tableau",
        monitor_sites: "Surveillance",
        monitor_desc: "Sites à pinger activement",
        apply: "Appliquer",
        show_all: "Tout afficher",
        monitor_all: "Tout surveiller",
        add_site: "Créer",
        add_site_hint: "Créez votre premier site ci-dessus",
        all: "Tous",
        add: "Ajouter",
        site: "Site",
        no_site: "Aucun",
        no_sites: "Aucun site défini",
        enter_site_name: "Entrez un nom de site",
        confirm_delete_site: "Supprimer le site",
        filter_applied: "Filtre appliqué",
        filter_cleared: "Affichage de tous les sites",
        monitoring_sites_updated: "Sites de surveillance mis à jour",
        all_sites_monitored: "Tous les sites surveillés",
        site_updated: "Site mis à jour",
        select_hosts_first: "Sélectionnez au moins un hôte",
        enter_site_for_hosts: "Entrez le nom du site pour les hôtes sélectionnés:",
        assign_site: "Assigner site",
        advanced_settings: "Paramètres Avancés",
        advanced_settings_desc: "Configuration SMTP, Telegram et système",
        smtp_config: "Configuration Email (SMTP)",
        smtp_server: "Serveur SMTP",
        or: "ou",
        sender_email: "Email expéditeur",
        password: "Mot de passe",
        password_placeholder: "Mot de passe ou app password",
        recipients: "Destinataires (séparés par des virgules)",
        test: "Tester",
        telegram_config: "Configuration Telegram",
        bot_token: "Token du Bot",
        recap_email_config: "Email Récapitulatif Périodique",
        send_time: "Heure d'envoi",
        send_days: "Jours d'envoi",
        monday: "Lundi",
        tuesday: "Mardi",
        wednesday: "Mercredi",
        thursday: "Jeudi",
        friday: "Vendredi",
        saturday: "Samedi",
        sunday: "Dimanche",
        send_test: "Envoyer un test",
        general_settings: "Paramètres Généraux",
        site_name: "Nom du Site",
        theme: "Thème",
        license_management: "Gestion de Licence",
        no_license: "Pas de licence active",
        license_active: "Licence active",
        days_remaining: "jours restants",
        features_limited: "Certaines fonctionnalités sont limitées (Alertes)",
        activation_code_label: "Code d'activation (Hardware ID) à envoyer :",
        license_key: "Clé de licence",
        enter_license: "Entrez votre clé de licence",
        activate_license: "Activer la licence",
        system_info: "Informations Système",
        web_server: "Serveur Web",
        connected_user: "Utilisateur connecté:",
        hosts_list: "Liste des Hôtes Monitorés",
        name: "Nom",
        latency: "Latence",
        temperature: "Température",
        status: "Statut",
        actions: "Actions",
        no_hosts_configured: "Aucun hôte configuré. Ajoutez des hôtes pour commencer le monitoring.",
        status_online: "En ligne",
        status_offline: "Hors ligne",
        copied: "Copié !",
        confirm_delete_all: "Voulez-vous vraiment effacer tous les hôtes ?",
        confirm_delete_host: "Voulez-vous vraiment supprimer l'hôte",
        confirm_logout: "Voulez-vous vraiment vous déconnecter ?",
        monitoring_started: "Monitoring démarré",
        monitoring_stopped: "Monitoring arrêté",
        alerts_saved: "Alertes sauvegardées",
        all_hosts_deleted: "Tous les hôtes ont été supprimés",
        duplicates_removed: "doublon(s) supprimé(s)",
        no_duplicates: "Aucun doublon trouvé",
        export_started: "Export CSV démarré",
        import_success: "Import réussi",
        settings_saved: "Paramètres sauvegardés",
        host_deleted: "Hôte supprimé",
        host_excluded: "Hôte exclu",
        host_included: "Hôte réinclus",
        name_modified: "Nom modifié pour",
        comment_modified: "Commentaire modifié pour",
        smtp_saved: "Configuration SMTP sauvegardée",
        test_email_sent: "Email de test envoyé",
        telegram_saved: "Configuration Telegram sauvegardée",
        telegram_test_sent: "Message de test envoyé sur Telegram",
        recap_saved: "Configuration email récapitulatif sauvegardée",
        recap_test_sent: "Email récapitulatif de test envoyé",
        general_saved: "Paramètres généraux sauvegardés",
        license_saved: "Licence enregistrée",
        credentials_changed: "Identifiants modifiés ! Reconnexion nécessaire.",
        scan_complete: "Scan terminé!",
        hosts_scanned: "hôte(s) scanné(s)",
        requires_license: "Nécessite une licence active",
        edit_name: "Modifier le nom",
        edit_comment: "Modifier le commentaire",
        comment: "Commentaire",
        delete: "Supprimer",
        include_excluded: "Inclure (Actuellement exclu)",
        exclude: "Exclure",
        menu_users: "Utilisateurs",
        add_user: "Ajouter un utilisateur",
        add_user_btn: "Ajouter l'utilisateur",
        users_list: "Liste des utilisateurs",
        username: "Nom d'utilisateur",
        password: "Mot de passe",
        role: "Rôle",
        role_user: "Utilisateur",
        role_admin: "Administrateur",
        user_actions: "Actions",
        change_password: "Mot de passe",
        change_role: "Rôle",
        current_user: "(Vous)",
        confirm_delete_user: "Êtes-vous sûr de vouloir supprimer cet utilisateur ?",
        enter_new_password: "Entrez le nouveau mot de passe :",
        confirm_change_role: "Voulez-vous changer le rôle de cet utilisateur ?",
        user_created: "Utilisateur créé avec succès",
        user_deleted: "Utilisateur supprimé",
        password_changed: "Mot de passe modifié",
        role_changed: "Rôle modifié",
        // Dashboards & Host Settings
        host_settings: "Paramètres Hôte",
        host_notif_desc: "Activez ou désactivez les alertes spécifiques pour cet hôte.",
        notifications: "Notifications",
        menu_dashboards: "Tableaux de Bord",
        dashboards: "Tableaux de Bord",
        add_dashboard: "Créer",
        create_dashboard: "Créer Tableau de Bord",
        edit_dashboard: "Modifier Tableau de Bord",
        hosts: "Hôtes"
    },
    en: {
        admin_title: "Administration - Ping ü",
        menu: "Menu",
        language: "Language",
        status: "Status",
        actions: "Actions",
        menu_users: "Users",
        menu_statistics: "Statistics",
        menu_synoptic: "Synoptic",
        menu_monitoring: "Monitoring Graphs",
        navigation: "Navigation",
        sections: "Sections",
        menu_home: "Home",
        menu_user_section: "User",
        menu_parameters: "Parameters",
        welcome_title: "Welcome to Administration",
        welcome_desc: "Manage your hosts, configure alerts and supervise your network from this interface.",
        quick_actions: "Quick Actions",
        change_credentials: "Change credentials",
        monitoring_view: "Monitoring View",
        logout: "Logout",
        status_running: "Running",
        status_stopped: "Stopped",
        manage_users_title: "User Management",
        admin_user: "Administrator",
        standard_user: "User",
        admin_role: "Admin Role",
        admin_role_desc: "Full access to administration",
        user_role: "User Role",
        user_role_desc: "Access to monitoring view only",
        change_credentials_title: "Change credentials",
        current_password: "Current password",
        new_username: "New username",
        new_password: "New password",
        user_credentials_changed: "User credentials changed",
        save: "Save",
        cancel: "Cancel",
        total_hosts: "Total Hosts",
        online: "Online",
        offline: "Offline",
        delay_sec: "Delay (sec)",
        add_hosts: "Add Hosts",
        add_hosts_desc: "Scan and add hosts",
        backup_restore_title: "Backup & Restore",
        backup_restore_desc: "Manage full configuration backups",
        backup_title: "Backup",
        backup_desc: "Download a full archive (.pingu) containing:",
        download_backup: "Download backup",
        restore_title: "Restore",
        restore_desc: "Restore configuration from a .pingu file.",
        restore_btn: "Restore backup",
        monitoring_desc: "Start/stop and configure",
        alerts_desc: "Email, Telegram, popup",
        actions_desc: "Import, export, cleanup",
        base_ip: "Base IP address",
        hosts_count: "Number of hosts",
        scan_type: "Scan type",
        scan_alive: "Alive (active only)",
        scan_all: "All hosts",
        scan_site: "Specific site",
        scan_hosts: "Scan hosts",
        assign_to_site: "Assign to site",
        monitoring_control: "Monitoring Control",
        ping_delay: "Delay between pings (sec)",
        hs_before_alert: "Failures before alert",
        start: "Start",
        stop: "Stop",
        alerts_config: "Alerts Configuration",
        alert_popup: "Popup (visual notification)",
        alert_email: "Alert email",
        alert_recap: "Summary email",
        alert_db: "External database",
        alert_temp: "High temperature alert",
        temp_threshold: "Critical Threshold (°C)",
        temp_threshold_warning: "Warning Threshold (°C)",
        alert_if_temp: "Alert + Visual if temperature ≥ critical threshold",
        alert_if_temp_warning: "Visual only if temperature ≥ warning threshold",
        save_alerts: "Save alerts",
        quick_actions: "Quick Actions",
        clear_all: "Clear all",
        remove_duplicates: "Remove duplicates",
        export_csv: "Export CSV",
        import_csv: "Import CSV",
        export_xls: "Export Excel",
        import_xls: "Import Excel",
        export_xls_started: "Excel export started",
        import_xls_success: "Excel import successful",
        // Sites management
        sites_management: "Sites Management",
        sites_subtitle: "Organize your hosts by location",
        display_filter: "Display",
        filter_desc: "Sites visible in the table",
        monitor_sites: "Monitoring",
        monitor_desc: "Sites to actively ping",
        apply: "Apply",
        show_all: "Show all",
        monitor_all: "Monitor all",
        add_site: "Create",
        add_site_hint: "Create your first site above",
        all: "All",
        add: "Add",
        site: "Site",
        no_site: "None",
        no_sites: "No sites defined",
        enter_site_name: "Enter a site name",
        confirm_delete_site: "Delete site",
        filter_applied: "Filter applied",
        filter_cleared: "Displaying all sites",
        monitoring_sites_updated: "Monitoring sites updated",
        all_sites_monitored: "All sites monitored",
        site_updated: "Site updated",
        select_hosts_first: "Select at least one host",
        enter_site_for_hosts: "Enter the site name for selected hosts:",
        assign_site: "Assign site",
        advanced_settings: "Advanced Settings",
        advanced_settings_desc: "SMTP, Telegram and system configuration",
        smtp_config: "Email Configuration (SMTP)",
        smtp_server: "SMTP Server",
        or: "or",
        sender_email: "Sender email",
        password: "Password",
        password_placeholder: "Password or app password",
        recipients: "Recipients (comma separated)",
        test: "Test",
        telegram_config: "Telegram Configuration",
        bot_token: "Bot Token",
        recap_email_config: "Periodic Summary Email",
        send_time: "Send time",
        send_days: "Send days",
        monday: "Monday",
        tuesday: "Tuesday",
        wednesday: "Wednesday",
        thursday: "Thursday",
        friday: "Friday",
        saturday: "Saturday",
        sunday: "Sunday",
        send_test: "Send a test",
        general_settings: "General Settings",
        site_name: "Site Name",
        theme: "Theme",
        license_management: "License Management",
        no_license: "No active license",
        license_active: "License active",
        days_remaining: "days remaining",
        features_limited: "Some features are limited (Alerts)",
        activation_code_label: "Activation code (Hardware ID) to send:",
        license_key: "License key",
        enter_license: "Enter your license key",
        activate_license: "Activate license",
        system_info: "System Information",
        web_server: "Web Server",
        connected_user: "Connected user:",
        hosts_list: "Monitored Hosts List",
        name: "Name",
        latency: "Latency",
        temperature: "Temperature",
        status: "Status",
        actions: "Actions",
        no_hosts_configured: "No hosts configured. Add hosts to start monitoring.",
        status_online: "Online",
        status_offline: "Offline",
        copied: "Copied!",
        confirm_delete_all: "Are you sure you want to delete all hosts?",
        confirm_delete_host: "Are you sure you want to delete host",
        confirm_logout: "Are you sure you want to logout?",
        monitoring_started: "Monitoring started",
        monitoring_stopped: "Monitoring stopped",
        alerts_saved: "Alerts saved",
        all_hosts_deleted: "All hosts have been deleted",
        duplicates_removed: "duplicate(s) removed",
        no_duplicates: "No duplicates found",
        export_started: "CSV export started",
        import_success: "Import successful",
        settings_saved: "Settings saved",
        host_deleted: "Host deleted",
        host_excluded: "Host excluded",
        host_included: "Host re-included",
        name_modified: "Name modified for",
        comment_modified: "Comment modified for",
        smtp_saved: "SMTP configuration saved",
        test_email_sent: "Test email sent",
        telegram_saved: "Telegram configuration saved",
        telegram_test_sent: "Test message sent on Telegram",
        recap_saved: "Summary email configuration saved",
        recap_test_sent: "Test summary email sent",
        general_saved: "General settings saved",
        license_saved: "License saved",
        credentials_changed: "Credentials changed! Reconnection required.",
        scan_complete: "Scan complete!",
        hosts_scanned: "host(s) scanned",
        requires_license: "Requires active license",
        edit_name: "Edit name",
        edit_comment: "Edit comment",
        comment: "Commentaire",
        delete: "Delete",
        include_excluded: "Include (Currently excluded)",
        exclude: "Exclude",
        menu_users: "Users",
        add_user: "Add user",
        add_user_btn: "Add user",
        users_list: "Users list",
        username: "Username",
        password: "Password",
        role: "Role",
        role_user: "User",
        role_admin: "Administrator",
        user_actions: "Actions",
        change_password: "Password",
        change_role: "Role",
        current_user: "(You)",
        confirm_delete_user: "Are you sure you want to delete this user?",
        enter_new_password: "Enter the new password:",
        confirm_change_role: "Do you want to change this user's role?",
        user_created: "User created successfully",
        user_deleted: "User deleted",
        password_changed: "Password changed",
        role_changed: "Role changed",
        // Dashboards & Host Settings
        host_settings: "Host Settings",
        host_notif_desc: "Enable or disable specific alerts for this host.",
        notifications: "Notifications",
        menu_dashboards: "Dashboards",
        dashboards: "Dashboards",
        add_dashboard: "Create",
        create_dashboard: "Create Dashboard",
        edit_dashboard: "Edit Dashboard",
        hosts: "Hosts"
    }
};

let currentLang = 'fr';

// Détecter la langue du navigateur
function detectBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    return browserLang.startsWith('fr') ? 'fr' : 'en';
}

// Charger la langue sauvegardée ou détecter automatiquement
function loadLanguage() {
    const savedLang = localStorage.getItem('pingü_lang');
    if (savedLang && translations[savedLang]) {
        currentLang = savedLang;
    } else {
        currentLang = detectBrowserLanguage();
    }
    const langSelect = document.getElementById('lang-select');
    if (langSelect) {
        langSelect.value = currentLang;
    }
    applyTranslations();
}

// Changer la langue
function changeLanguage(lang) {
    if (translations[lang]) {
        currentLang = lang;
        localStorage.setItem('pingü_lang', lang);
        applyTranslations();
        // Re-render le tableau des hôtes
        if (hostsData.length > 0) {
            updateHostsTable(hostsData);
        }
    }
}

// Appliquer les traductions
function applyTranslations() {
    const trans = translations[currentLang];

    // Mettre à jour les éléments avec data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (trans[key]) {
            el.textContent = trans[key];
        }
    });

    // Mettre à jour les placeholders
    document.querySelectorAll('[data-placeholder-i18n]').forEach(el => {
        const key = el.getAttribute('data-placeholder-i18n');
        if (trans[key]) {
            el.placeholder = trans[key];
        }
    });

    // Mettre à jour les options des selects
    document.querySelectorAll('select option[data-i18n]').forEach(option => {
        const key = option.getAttribute('data-i18n');
        if (key && trans[key]) {
            option.textContent = trans[key];
        }
    });

    // Mettre à jour le titre de la page
    document.title = trans.admin_title;

    // Mettre à jour l'attribut lang du HTML
    document.documentElement.lang = currentLang;

    // Mettre à jour le statut du monitoring
    updateMonitoringStatus(monitoringRunning);
}

// Fonction d'aide pour obtenir une traduction
function t(key) {
    return translations[currentLang][key] || key;
}

// ==================== Socket.IO ====================
const socket = io({
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 10
});

let hostsData = [];
let monitoringRunning = false;
let sitesList = [];
let sitesActifs = [];
let siteFilter = [];

// ==================== Sections Collapsibles ====================

function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.toggle('open');
        // Sauvegarder l'état dans localStorage
        saveSectionsState();
    }
}

function saveSectionsState() {
    const sections = document.querySelectorAll('.collapsible-section');
    const state = {};
    sections.forEach(section => {
        state[section.id] = section.classList.contains('open');
    });
    localStorage.setItem('adminSectionsState', JSON.stringify(state));
}

function loadSectionsState() {
    try {
        const saved = localStorage.getItem('adminSectionsState');
        if (saved) {
            const state = JSON.parse(saved);
            Object.keys(state).forEach(sectionId => {
                const section = document.getElementById(sectionId);
                if (section) {
                    if (state[sectionId]) {
                        section.classList.add('open');
                    } else {
                        section.classList.remove('open');
                    }
                }
            });
        }
    } catch (e) {
        console.log('Erreur chargement état sections:', e);
    }
}

// Charger l'état des sections au démarrage
document.addEventListener('DOMContentLoaded', loadSectionsState);

// ==================== Gestion des Sites ====================

// ==================== Gestion des Sites ====================

async function loadLocalIp() {
    try {
        const response = await fetch('/api/local_ip');
        const data = await response.json();
        if (data.success && data.ip) {
            const parts = data.ip.split('.');
            if (parts.length === 4) {
                parts[3] = '1';
                const subnetIp = parts.join('.');
                const ipInput = document.getElementById('input-ip');
                if (ipInput && !ipInput.value) { // Only set if empty? User asked to fill it, maybe overwrite? "remplisse automatiquement". Let's overwrite or fill if empty. Standard behavior is usually fill initial value. The input is hardcoded placeholder="192...". 
                    // Let's overwrite for now as per "remplisse automatiquement".
                    ipInput.value = subnetIp;
                }
            }
        }
    } catch (error) {
        console.error('Erreur chargement IP locale:', error);
    }
}

async function loadSites() {
    try {
        const response = await fetch('/api/get_sites');
        const data = await response.json();

        if (data.success) {
            sitesList = data.sites || [];
            sitesActifs = data.sites_actifs || [];
            siteFilter = data.site_filter || [];

            updateSitesUI();
        }
    } catch (error) {
        console.error('Erreur chargement sites:', error);
    }
}

function updateSitesUI() {
    // Mettre à jour la liste des sites
    const sitesList_container = document.getElementById('sites-list');
    const countBadge = document.getElementById('sites-count-badge');

    if (countBadge) {
        countBadge.textContent = `${sitesList.length} site${sitesList.length > 1 ? 's' : ''}`;
    }

    if (sitesList_container) {
        if (sitesList.length === 0) {
            sitesList_container.innerHTML = `
        <div class="no-sites-message">
            <div class="empty-icon">🏗️</div>
            <p>${t('no_sites') || 'Aucun site défini'}</p>
            <p style="font-size: 12px; margin-top: 5px;">${t('add_site_hint') || 'Créez votre premier site ci-dessus'}</p>
        </div>
    `;
        } else {
            sitesList_container.innerHTML = sitesList.map((site, index) => {
                const colors = getSiteColor(site);
                return `
        <div class="site-tag-premium" style="animation-delay: ${index * 0.05}s; background: ${colors.badge}; border-color: ${colors.border};">
            <div class="site-tag-icon" style="background: linear-gradient(135deg, ${colors.text}, ${colors.bg});">🏢</div>
            <span class="site-tag-name" style="color: ${colors.text};">${escapeHtml(site)}</span>
            <button class="site-tag-delete" onclick="deleteSite('${escapeHtml(site)}')" title="${t('delete') || 'Supprimer'}">✕</button>
        </div>
    `;
            }).join('');
        }
    }

    // Mettre à jour les selects de filtrage
    updateSiteSelect('select-site-filter', siteFilter);
    updateSiteSelect('select-sites-actifs', sitesActifs);

    // Mettre à jour le sélecteur de site dans le formulaire de scan
    updateScanSiteSelect();
}

function updateScanSiteSelect() {
    const select = document.getElementById('select-scan-site');
    if (!select) return;

    // Garder la valeur sélectionnée
    const currentValue = select.value;

    select.innerHTML = `<option value="">${t('no_site') || '- Aucun -'}</option>` +
        sitesList.map(site => `<option value="${escapeHtml(site)}" ${site === currentValue ? 'selected' : ''}>${escapeHtml(site)}</option>`).join('');

    // Restaurer la valeur si elle existe encore
    if (currentValue && sitesList.includes(currentValue)) {
        select.value = currentValue;
    }
}

function updateSiteSelect(selectId, selectedValues) {
    const select = document.getElementById(selectId);
    if (!select) return;

    select.innerHTML = sitesList.map(site => `
    <option value="${escapeHtml(site)}" ${selectedValues.includes(site) ? 'selected' : ''}>${escapeHtml(site)}</option>
    `).join('');
}

async function addSite() {
    const input = document.getElementById('input-new-site');
    const siteName = input.value.trim();

    if (!siteName) {
        showNotification(t('enter_site_name') || 'Entrez un nom de site', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/add_site', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: siteName })
        });

        const data = await response.json();

        if (data.success) {
            sitesList = data.sites;
            input.value = '';
            updateSitesUI();
            showNotification(data.message, 'success');
            socket.emit('request_update');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Erreur ajout site', 'error');
    }
}

async function deleteSite(siteName) {
    if (!confirm(`${t('confirm_delete_site') || 'Supprimer le site'} "${siteName}" ?`)) return;

    try {
        const response = await fetch('/api/delete_site', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: siteName })
        });

        const data = await response.json();

        if (data.success) {
            sitesList = data.sites;
            sitesActifs = sitesActifs.filter(s => s !== siteName);
            siteFilter = siteFilter.filter(s => s !== siteName);
            updateSitesUI();
            showNotification(data.message, 'success');
            socket.emit('request_update');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Erreur suppression site', 'error');
    }
}

async function applySiteFilter() {
    const select = document.getElementById('select-site-filter');
    const selectedSites = Array.from(select.selectedOptions).map(opt => opt.value);

    try {
        const response = await fetch('/api/set_site_filter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sites: selectedSites })
        });

        const data = await response.json();

        if (data.success) {
            siteFilter = data.site_filter;
            showNotification(t('filter_applied') || 'Filtre appliqué', 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Erreur application filtre', 'error');
    }
}

async function clearSiteFilter() {
    try {
        const response = await fetch('/api/set_site_filter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sites: [] })
        });

        const data = await response.json();

        if (data.success) {
            siteFilter = [];
            updateSiteSelect('select-site-filter', []);
            showNotification(t('filter_cleared') || 'Affichage de tous les sites', 'success');
        }
    } catch (error) {
        showNotification('Erreur', 'error');
    }
}

// ==================== Gestion des Notifications ====================
let notifications = [];

async function loadNotifications(limit = 50, forceReload = true) {
    const unreadOnly = document.getElementById('chk-unread-only').checked;

    try {
        const response = await fetch(`/api/notifications?limit=${limit}&unread_only=${unreadOnly}`);
        const data = await response.json();

        notifications = data;
        updateNotificationsUI();
        updateNotificationBadge();

    } catch (error) {
        console.error('Erreur chargement notifications:', error);
    }
}

function updateNotificationsUI() {
    const list = document.getElementById('notifications-list');
    if (!list) return;

    if (notifications.length === 0) {
        list.innerHTML = `<div style="text-align: center; color: #a0aec0; padding: 40px;">Aucune notification</div>`;
        return;
    }

    list.innerHTML = notifications.map(notif => {
        let icon = '🔔';
        let color = '#a0aec0';
        let bg = 'rgba(255,255,255,0.05)';

        switch (notif.level) {
            case 'error': icon = '🚨'; color = '#ef4444'; bg = 'rgba(239, 68, 68, 0.1)'; break;
            case 'warning': icon = '⚠️'; color = '#f59e0b'; bg = 'rgba(245, 158, 11, 0.1)'; break;
            case 'success': icon = '✅'; color = '#10b981'; bg = 'rgba(16, 185, 129, 0.1)'; break;
            case 'info': icon = 'ℹ️'; color = '#3b82f6'; bg = 'rgba(59, 130, 246, 0.1)'; break;
        }

        if (!notif.read) {
            bg = `linear-gradient(to right, ${bg}, rgba(255,255,255,0.05))`;
            color = '#fff';
        }

        const time = new Date(notif.timestamp).toLocaleString();

        return `
        <div class="notification-item ${notif.read ? 'read' : 'unread'}" 
             style="background: ${bg}; border-left: 4px solid ${color}; padding: 12px; border-radius: 6px; position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px;">
                <strong style="color: ${color}; display: flex; align-items: center; gap: 8px;">
                    ${icon} ${escapeHtml(notif.message)}
                </strong>
                <span style="font-size: 11px; color: #718096;">${time}</span>
            </div>
            ${notif.details && Object.keys(notif.details).length > 0 ?
                `<pre style="margin: 5px 0 0; font-size: 11px; color: #a0aec0; overflow-x: auto;">${JSON.stringify(notif.details, null, 2)}</pre>`
                : ''}
        </div>
        `;
    }).join('');
}

async function markAllNotificationsRead() {
    try {
        await fetch('/api/notifications/mark_read', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: null }) // null means all
        });
        loadNotifications();
    } catch (e) { console.error(e); }
}

async function clearAllNotifications() {
    if (!confirm("Tout effacer ?")) return;
    try {
        await fetch('/api/notifications/clear', { method: 'POST' });
        loadNotifications();
    } catch (e) { console.error(e); }
}

function updateNotificationBadge() {
    // Calcul simple coté client ou API séparée
    const unread = notifications.filter(n => !n.read).length;
    const badge = document.getElementById('header-notif-badge');
    if (badge) {
        badge.innerText = unread;
        badge.style.display = unread > 0 ? 'inline-block' : 'none';
    }
}

// Charger périodiquement
setInterval(() => {
    // Refresh discret seulement si le panneau n'est pas ouvert ou pour le badge
    loadNotifications(50, false);
}, 30000);

// Chargement initial
loadNotifications();

async function applySitesActifs() {
    const select = document.getElementById('select-sites-actifs');
    const selectedSites = Array.from(select.selectedOptions).map(opt => opt.value);

    try {
        const response = await fetch('/api/set_sites_actifs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sites: selectedSites })
        });

        const data = await response.json();

        if (data.success) {
            sitesActifs = data.sites_actifs;
            showNotification(t('monitoring_sites_updated') || 'Sites de surveillance mis à jour', 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Erreur', 'error');
    }
}

async function clearSitesActifs() {
    try {
        const response = await fetch('/api/set_sites_actifs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sites: [] })
        });

        const data = await response.json();

        if (data.success) {
            sitesActifs = [];
            updateSiteSelect('select-sites-actifs', []);
            showNotification(t('all_sites_monitored') || 'Tous les sites surveillés', 'success');
        }
    } catch (error) {
        showNotification('Erreur', 'error');
    }
}

async function setHostSite(ip, site) {
    try {
        const response = await fetch('/api/set_host_site', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip: ip, site: site })
        });

        const data = await response.json();

        if (data.success) {
            showNotification(t('site_updated') || 'Site mis à jour', 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Erreur assignation site', 'error');
    }
}

async function setSelectedHostsSite() {
    const selectedIps = getSelectedHosts();

    if (selectedIps.length === 0) {
        showNotification(t('select_hosts_first') || 'Sélectionnez au moins un hôte', 'warning');
        return;
    }

    const siteName = prompt(t('enter_site_for_hosts') || 'Entrez le nom du site pour les hôtes sélectionnés:');
    if (siteName === null) return;

    try {
        const response = await fetch('/api/set_multiple_hosts_site', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ips: selectedIps, site: siteName.trim() })
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Erreur', 'error');
    }
}

// ==================== Socket Events ====================
socket.on('connect', async function () {
    console.log('✅ Connected to server');
    await loadSites();  // Attendre le chargement des sites
    loadSettings();
    loadLocalIp();
    socket.emit('request_update');  // Demander les hôtes APRÈS avoir chargé les sites
});

socket.on('disconnect', function () {
    console.log('❌ Disconnected from server');
});

socket.on('hosts_update', function (hosts) {
    if (!Array.isArray(hosts)) {
        hosts = [];
    }
    hostsData = hosts;
    // Appliquer le tri actuel si défini
    if (currentSort.column) {
        const savedDirection = currentSort.direction;
        currentSort.direction = savedDirection === 'asc' ? 'desc' : 'asc';
        sortHosts(currentSort.column);
    } else {
        updateHostsTable(hosts);
    }
    updateStats(hosts);
});

socket.on('monitoring_status', function (data) {
    monitoringRunning = data.running;
    updateMonitoringStatus(data.running);
});

socket.on('notification', function (data) {
    showNotification(data.message, data.type || 'info');
});

socket.on('scan_complete', function (data) {
    console.log('📡 Scan complete:', data.count, 'host(s)');
    showNotification(`${t('scan_complete')} ${data.count} ${t('hosts_scanned')}`, 'success');
    showBrowserNotification(t('scan_complete'), `${data.count} ${t('hosts_scanned')}`);
    socket.emit('request_update');
});

// ==================== Sorting Functions ====================
let currentSort = { column: 'ip', direction: 'asc' };

function naturalSort(a, b) {
    const ax = [], bx = [];
    a.replace(/(\d+)|(\D+)/g, function (_, $1, $2) { ax.push([$1 || Infinity, $2 || ""]) });
    b.replace(/(\d+)|(\D+)/g, function (_, $1, $2) { bx.push([$1 || Infinity, $2 || ""]) });
    while (ax.length && bx.length) {
        const an = ax.shift();
        const bn = bx.shift();
        const nn = (an[0] - bn[0]) || an[1].localeCompare(bn[1]);
        if (nn) return nn;
    }
    return ax.length - bx.length;
}

function sortHosts(column) {
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = 'asc';
    }

    document.querySelectorAll('.sort-icon').forEach(icon => icon.textContent = '↕️');
    const currentIcon = document.getElementById(`sort-${column}`);
    if (currentIcon) {
        currentIcon.textContent = currentSort.direction === 'asc' ? '⬆️' : '⬇️';
    }

    hostsData.sort((a, b) => {
        let valA = a[column] || '';
        let valB = b[column] || '';

        if (column === 'ip') {
            const ipA = valA.split('.').map(Number);
            const ipB = valB.split('.').map(Number);
            for (let i = 0; i < 4; i++) {
                if (ipA[i] !== ipB[i]) {
                    return (ipA[i] - ipB[i]) * (currentSort.direction === 'asc' ? 1 : -1);
                }
            }
            return 0;
        }

        if (column === 'commentaire') {
            valA = a.commentaire || '';
            valB = b.commentaire || '';
        }

        const comparison = naturalSort(String(valA), String(valB));
        return currentSort.direction === 'asc' ? comparison : -comparison;
    });

    updateHostsTable(hostsData);
}

function updateStats(hosts) {
    const total = hosts.length;
    const online = hosts.filter(h => h.status === 'online').length;
    const offline = total - online;

    // Stats dans la grille principale
    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-online').textContent = online;
    document.getElementById('stat-offline').textContent = offline;

    // Stats dans la page d'accueil
    const homeTotal = document.getElementById('home-stat-total');
    const homeOnline = document.getElementById('home-stat-online');
    const homeOffline = document.getElementById('home-stat-offline');
    if (homeTotal) homeTotal.textContent = total;
    if (homeOnline) homeOnline.textContent = online;
    if (homeOffline) homeOffline.textContent = offline;
}

function updateMonitoringStatus(running) {
    const statusEl = document.getElementById('monitoring-status');
    const statusMiniEl = document.getElementById('monitoring-status-mini');

    // Helper to safely update status elements
    const updateStatusElement = (el, isRunning) => {
        if (!el) return;
        const dot = el.querySelector('.status-dot');
        const text = el.querySelector('span[data-i18n]');

        if (isRunning) {
            el.className = 'status-indicator running';
            if (dot) dot.className = 'status-dot running';
            if (text) {
                text.textContent = t('status_running');
                text.setAttribute('data-i18n', 'status_running');
            }
        } else {
            el.className = 'status-indicator stopped';
            if (dot) dot.className = 'status-dot stopped';
            if (text) {
                text.textContent = t('status_stopped');
                text.setAttribute('data-i18n', 'status_stopped');
            }
        }
    };

    updateStatusElement(statusEl, running);
    updateStatusElement(statusMiniEl, running);

    // Update Header Buttons
    const btnStart = document.getElementById('btn-start-monitoring');
    const btnStop = document.getElementById('btn-stop-monitoring');

    if (running) {
        if (btnStart) btnStart.style.display = 'none';
        if (btnStop) btnStop.style.display = 'flex';
    } else {
        if (btnStart) btnStart.style.display = 'flex';
        if (btnStop) btnStop.style.display = 'none';
    }
}


function updateHostsTable(hosts) {
    const tbody = document.getElementById('hosts-table-body');

    if (hosts.length === 0) {
        tbody.innerHTML = `
    <tr>
        <td colspan="10" style="text-align: center; padding: 40px; color: #9ca3af;">
            ${t('no_hosts_configured')}
        </td>
    </tr>
`;
        return;
    }

    // Debug: vérifier si les sites sont bien reçus
    console.log('Sites présents dans les données:', hosts.filter(h => h.site).map(h => `${h.ip} -> ${h.site}`));
    console.log('sitesList disponibles:', sitesList);

    tbody.innerHTML = hosts.map(host => {
        const siteColors = host.site ? getSiteColor(host.site) : { bg: 'rgba(0, 0, 0, 0.3)', text: '#e4e4e4', border: 'rgba(255, 255, 255, 0.2)' };
        return `
    <tr>
        <td><strong>${escapeHtml(host.ip)}</strong></td>
        <td>
            <span class="host-name-display" id="name-display-${escapeHtml(host.ip).replace(/\./g, '-')}"
                onclick="editHostName('${host.ip}')"
                style="cursor: pointer; display: inline-block; min-width: 50px; border-bottom: 1px dashed #667eea55;"
                title="${t('edit_name')}">
                ${escapeHtml(host.nom) || '-'}
            </span>
            <input type="text" class="host-name-input" id="name-input-${escapeHtml(host.ip).replace(/\./g, '-')}"
                value="${escapeHtml(host.nom)}"
                onblur="saveHostName('${host.ip}')"
                onkeydown="if(event.key === 'Enter') this.blur()"
                style="display: none; width: 100%; padding: 5px; border: 2px solid #10b981; border-radius: 6px; font-weight: 600;">
        </td>
        <td>${escapeHtml(host.mac) || '-'}</td>
        <td>${escapeHtml(host.port) || '-'}</td>
        <td style="text-align: center;">
            <span class="latency-badge ${getLatencyClass(host.latence)}">${escapeHtml(host.latence) || '-'}</span>
        </td>
        <td>${escapeHtml(host.temp) || '-'}</td>
        <td>
            <span class="host-status ${host.status}">
                ${host.status === 'online' ? t('status_online') : t('status_offline')}
            </span>
        </td>
        <td>
            <select class="site-select" onchange="setHostSite('${host.ip}', this.value)"
                style="padding: 5px 10px; border-radius: 15px; border: 1px solid ${siteColors.border} !important; background-color: ${siteColors.bg} !important; color: ${siteColors.text} !important; font-size: 12px; cursor: pointer; -webkit-appearance: none; appearance: none; text-align: center;">
                <option value="" ${!host.site ? 'selected' : ''}>- ${t('no_site') || 'Aucun'} -</option>
                ${sitesList.map(site => {
            const isSelected = (host.site && host.site === site);
            return `<option value="${escapeHtml(site)}" ${isSelected ? 'selected' : ''}>${escapeHtml(site)}</option>`;
        }).join('')}
            </select>
        </td>
        <td>
            <span class="host-comment-display" id="comment-display-${escapeHtml(host.ip).replace(/\./g, '-')}"
                onclick="editHostComment('${host.ip}')"
                style="cursor: pointer; display: inline-block; min-width: 80px; border-bottom: 1px dashed #667eea55;"
                title="${t('edit_comment')}">
                ${escapeHtml(host.commentaire) || '-'}
            </span>
            <input type="text" class="host-comment-input" id="comment-input-${escapeHtml(host.ip).replace(/\./g, '-')}"
                value="${escapeHtml(host.commentaire)}"
                onblur="saveHostComment('${host.ip}')"
                onkeydown="if(event.key === 'Enter') this.blur()"
                style="display: none; width: 100%; padding: 5px; border: 2px solid #10b981; border-radius: 6px;">
        </td>
        <td class="host-actions">
            <button class="btn btn-secondary btn-small" onclick="openHostSettings('${host.ip}', '${escapeHtml(host.nom)}')" title="${t('host_settings') || 'Paramètres'}">
                ⚙️
            </button>
            <button class="btn btn-danger btn-small" onclick="deleteHost('${host.ip}')" title="${t('delete')}">
                🗑️
            </button>
            <button class="btn ${host.excl === 'x' ? 'btn-secondary' : 'btn-secondary'} btn-small"
                onclick="excludeHost('${host.ip}', ${host.excl === 'x' ? true : false})"
                title="${host.excl === 'x' ? t('include_excluded') : t('exclude')}"
                style="${host.excl === 'x' ? 'background: #f59e0b;' : ''}">
                ${host.excl === 'x' ? '⚠️' : '🚫'}
            </button>
        </td>
    </tr>
    `;
    }).join('');
}

// ==================== Utility Functions ====================
/**
 * Formate le délai de manière intelligente
 * < 60s : affiche en secondes
 * 60s - 3600s : affiche en minutes
 * > 3600s : affiche en heures et minutes
 */
function formatDelay(seconds) {
    const sec = parseInt(seconds);

    if (sec < 60) {
        // Moins d'une minute : afficher en secondes
        return `${sec}s`;
    } else if (sec < 3600) {
        // Moins d'une heure : afficher en minutes
        const minutes = Math.floor(sec / 60);
        const remainingSeconds = sec % 60;
        if (remainingSeconds === 0) {
            return `${minutes}min`;
        } else {
            return `${minutes}min ${remainingSeconds}s`;
        }
    } else {
        // Plus d'une heure : afficher en heures et minutes
        const hours = Math.floor(sec / 3600);
        const minutes = Math.floor((sec % 3600) / 60);
        if (minutes === 0) {
            return `${hours}h`;
        } else {
            return `${hours}h ${minutes}min`;
        }
    }
}

// ==================== API Functions ====================
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(endpoint, options);

        // Vérifier si la réponse est du JSON
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            const text = await response.text();
            console.error('Expected JSON, got:', text.substring(0, 100));
            throw new Error('La réponse du serveur n\'est pas au format JSON (Erreur ' + response.status + ')');
        }

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'API Error');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        showNotification('Error: ' + error.message, 'error');
        throw error;
    }
}

// ==================== Event Handlers ====================
document.getElementById('form-add-hosts').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
        ip: document.getElementById('input-ip').value,
        hosts: parseInt(document.getElementById('input-hosts').value),
        port: document.getElementById('input-port').value,
        scan_type: document.getElementById('select-scan-type').value,
        site: document.getElementById('select-scan-site').value  // Site à assigner
    };

    try {
        const result = await apiCall('/api/add_hosts', 'POST', data);
        showNotification(result.message || t('scan_hosts'), 'success');
        setTimeout(() => socket.emit('request_update'), 2000);
    } catch (error) { }
});

document.getElementById('btn-start-monitoring').addEventListener('click', async function () {
    const delai = parseInt(document.getElementById('input-delai').value);
    const nbHs = parseInt(document.getElementById('input-nb-hs').value);

    try {
        const result = await apiCall('/api/start_monitoring', 'POST', { delai, nb_hs: nbHs });
        showNotification(t('monitoring_started'), 'success');
        monitoringRunning = true;
        updateMonitoringStatus(true);
    } catch (error) { }
});

document.getElementById('btn-stop-monitoring').addEventListener('click', async function () {
    try {
        const result = await apiCall('/api/stop_monitoring', 'POST');
        showNotification(t('monitoring_stopped'), 'info');
        monitoringRunning = false;
        updateMonitoringStatus(false);
    } catch (error) { }
});

// Bouton toggle unique dans le header qui change selon l'état


async function handleRestore(event) {
    event.preventDefault();

    const fileInput = document.getElementById('backupFile');
    const file = fileInput.files[0];
    if (!file) {
        showNotification('Veuillez sélectionner un fichier', 'error');
        return;
    }

    if (!confirm(`${t('restore_desc')} ${t('confirm_restore') || 'Voulez-vous continuer ?'}`)) {
        return;
    }

    const formData = new FormData();
    formData.append('backup_file', file);

    try {
        const response = await fetch('/api/admin/restore', {
            method: 'POST',
            body: formData // Pas de Content-Type header, le navigateur le mettra (multipart/form-data)
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                alert(data.message);
                window.location.reload();
            }, 1500);
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        console.error('Erreur restauration:', error);
        showNotification('Erreur lors de la restauration', 'error');
    }
}

document.getElementById('btn-save-alerts').addEventListener('click', async function () {
    const alerts = {
        popup: document.getElementById('check-popup').checked,
        mail: document.getElementById('check-mail').checked,
        telegram: document.getElementById('check-telegram').checked,
        mail_recap: document.getElementById('check-mail-recap').checked,
        db_externe: document.getElementById('check-db-externe').checked,
        temp_alert: document.getElementById('check-temp-alert').checked,
        temp_seuil: parseInt(document.getElementById('input-temp-seuil').value) || 70,
        temp_seuil_warning: parseInt(document.getElementById('input-temp-seuil-warning').value) || 60
    };

    try {
        const result = await apiCall('/api/save_alerts', 'POST', alerts);
        showNotification(t('alerts_saved'), 'success');
    } catch (error) { }
});

document.getElementById('btn-clear-all').addEventListener('click', async function () {
    if (!confirm(t('confirm_delete_all'))) {
        return;
    }

    try {
        const result = await apiCall('/api/clear_all', 'POST');
        showNotification(t('all_hosts_deleted'), 'info');
        socket.emit('request_update');
    } catch (error) { }
});

document.getElementById('btn-remove-duplicates').addEventListener('click', async function () {
    try {
        const result = await apiCall('/api/remove_duplicates', 'POST');
        if (result.duplicates_removed > 0) {
            showNotification(`${result.duplicates_removed} ${t('duplicates_removed')}`, 'success');
        } else {
            showNotification(t('no_duplicates'), 'info');
        }
        socket.emit('request_update');
    } catch (error) { }
});

document.getElementById('btn-export-csv').addEventListener('click', async function () {
    try {
        window.location.href = '/api/export_csv';
        showNotification(t('export_started'), 'success');
    } catch (error) {
        showNotification('Export error', 'error');
    }
});

document.getElementById('btn-import-csv').addEventListener('click', function () {
    document.getElementById('file-import-csv').click();
});

document.getElementById('file-import-csv').addEventListener('change', async function (e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/import_csv', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            showNotification(result.message || t('import_success'), 'success');
            socket.emit('request_update');
        } else {
            showNotification(result.error || 'Import error', 'error');
        }
    } catch (error) {
        showNotification('Import error', 'error');
    }

    e.target.value = '';
});


document.getElementById('btn-save-monitoring').addEventListener('click', async function () {
    const settings = {
        delai: parseInt(document.getElementById('input-delai').value) || 10,
        nb_hs: parseInt(document.getElementById('input-nb-hs').value) || 3
    };

    try {
        const result = await apiCall('/api/save_settings', 'POST', settings);
        showNotification(t('monitoring_saved') || 'Configuration sauvegardée', 'success');
        // Update monitoring status visually if running
        if (monitoringRunning) {
            updateMonitoringStatus(true); // Re-trigger update to reflect new delay?
            // Actually backend handles logic. Visually nothing changes drastically.
        }
    } catch (error) { }
});

document.getElementById('btn-save-settings').addEventListener('click', async function () {
    const settings = {
        delai: parseInt(document.getElementById('input-delai').value) || 10,
        nb_hs: parseInt(document.getElementById('input-nb-hs').value) || 3
    };

    try {
        const result = await apiCall('/api/save_settings', 'POST', settings);
        showNotification(t('settings_saved'), 'success');
    } catch (error) { }
});

// ==================== Export/Import Excel ====================
document.getElementById('btn-export-xls').addEventListener('click', async function () {
    try {
        window.location.href = '/api/export_xls';
        showNotification(t('export_xls_started'), 'success');
    } catch (error) {
        showNotification('Export error', 'error');
    }
});

document.getElementById('btn-import-xls').addEventListener('click', function () {
    document.getElementById('file-import-xls').click();
});

document.getElementById('file-import-xls').addEventListener('change', async function (e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/import_xls', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            showNotification(result.message || t('import_xls_success'), 'success');
            socket.emit('request_update');
        } else {
            showNotification(result.error || 'Import error', 'error');
        }
    } catch (error) {
        showNotification('Import error', 'error');
    }

    e.target.value = '';
});

// ==================== Network Scanner ====================
let scanDevicesFound = 0;

document.getElementById('btn-start-scan').addEventListener('click', async function () {
    try {
        // Récupérer les types de scan sélectionnés
        const scanTypes = [];
        if (document.getElementById('scan-type-hik').checked) scanTypes.push('hik');
        if (document.getElementById('scan-type-dahua').checked) scanTypes.push('dahua');
        if (document.getElementById('scan-type-onvif').checked) scanTypes.push('onvif');
        if (document.getElementById('scan-type-samsung').checked) scanTypes.push('samsung');
        if (document.getElementById('scan-type-avigilon').checked) scanTypes.push('avigilon');
        if (document.getElementById('scan-type-upnp').checked) scanTypes.push('upnp');
        if (document.getElementById('scan-type-xiaomi') && document.getElementById('scan-type-xiaomi').checked) scanTypes.push('xiaomi');
        if (document.getElementById('scan-type-snmp') && document.getElementById('scan-type-snmp').checked) scanTypes.push('server');
        if (document.getElementById('scan-type-ups') && document.getElementById('scan-type-ups').checked) scanTypes.push('ups');

        if (scanTypes.length === 0) {
            showNotification('Sélectionnez au moins un type de scan', 'warning');
            return;
        }

        // Reset UI
        scanDevicesFound = 0;
        document.getElementById('scan-results-body').innerHTML = '';
        document.getElementById('scan-devices-count').textContent = '0 périphérique(s)';

        // Démarrer le scan
        const result = await apiCall('/api/network_scan/start', 'POST', {
            scan_types: scanTypes,
            timeout: 15
        });

        if (result.success) {
            // Afficher UI de scan en cours
            document.getElementById('btn-start-scan').style.display = 'none';
            document.getElementById('btn-stop-scan').style.display = 'inline-flex';
            document.getElementById('scan-progress').style.display = 'flex';
            document.getElementById('scan-results-container').style.display = 'block';
            showNotification('Scan démarré', 'success');
        }
    } catch (error) {
        console.error('Erreur scan:', error);
        showNotification('Erreur lors du scan', 'error');
    }
});

document.getElementById('btn-stop-scan').addEventListener('click', async function () {
    try {
        await apiCall('/api/network_scan/stop', 'POST');
        showNotification('Scan arrêté', 'info');
        resetScanUI();
    } catch (error) {
        console.error('Erreur arrêt scan:', error);
    }
});

function resetScanUI() {
    document.getElementById('btn-start-scan').style.display = 'inline-flex';
    document.getElementById('btn-stop-scan').style.display = 'none';
    document.getElementById('scan-progress').style.display = 'none';
}

function addDeviceToScanResults(device) {
    const tbody = document.getElementById('scan-results-body');
    const row = tbody.insertRow(0); // Insérer en premier
    row.style.animation = 'fadeIn 0.3s ease-in';

    // Vérifier si l'hôte est déjà monitoré
    const currentHosts = window.hostsData || [];
    const isMonitored = currentHosts.some(h => h.ip === device.ip);

    // Type icon mapping
    const typeIcons = {
        'camera_hikvision': '📹',
        'camera_dahua': '📹',
        'camera_generic': '📹',
        'camera_samsung': '📹',
        'camera_avigilon': '📹',
        'camera_xiaomi': '📱',
        'upnp_device': '🌐',
        'switch': '🔀',
        'server': '🖥️',
        'ups': '🔋'
    };

    const icon = typeIcons[device.type] || '❓';
    const typeName = device.type.replace('camera_', '').replace('_', ' ');

    let actionBtn;
    if (isMonitored) {
        actionBtn = `<button class="btn btn-sm" style="background-color: #d97706; color: white;"
            onclick="addScannedDevice('${device.ip}', '${device.name || device.ip}', true)">
            ⚠️ Déjà présent
        </button>`;
    } else {
        actionBtn = `<button class="btn btn-sm btn-primary"
            onclick="addScannedDevice('${device.ip}', '${device.name || device.ip}', false)">
            ➕ Ajouter
        </button>`;
    }

    row.innerHTML = `
    <td><code>${device.ip}</code></td>
    <td>${icon} ${typeName}</td>
    <td>${device.manufacturer || '-'}</td>
    <td>${device.model || '-'}</td>
    <td>${device.name || '-'}</td>
    <td><span style="background: var(--accent-color); color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">${device.protocol}</span></td>
    <td>
        ${actionBtn}
    </td>
    `;

    scanDevicesFound++;
    document.getElementById('scan-devices-count').textContent = `${scanDevicesFound} périphérique(s)`;
}

// Fonction globale pour ajouter un périphérique découvert au monitoring
window.addScannedDevice = async function (ip, name, isDuplicate = false) {
    if (isDuplicate) {
        if (!confirm(`L'hôte ${ip} est déjà dans votre liste de monitoring.\nVoulez-vous vraiment l'ajouter en doublon ?`)) {
            return;
        }
    }
    try {
        const result = await apiCall('/api/add_hosts', 'POST', {
            ip: ip,
            hosts: 1,
            port: '80',
            scan_type: 'alive',
            site: ''
        });

        if (result.success) {
            showNotification(`${name} (${ip}) ajouté au monitoring`, 'success');
            // Optionnel: mettre à jour le nom
            if (name && name !== ip) {
                await apiCall('/api/update_host_name', 'POST', { ip: ip, name: name });
            }
        } else {
            showNotification('Erreur: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Erreur ajout périphérique:', error);
        showNotification('Erreur lors de l\'ajout', 'error');
    }
};

// WebSocket listeners pour le scanner
socket.on('scan_device_found', function (device) {
    addDeviceToScanResults(device);
});

socket.on('scan_status', function (data) {
    if (data.status === 'complete') {
        showNotification(`Scan terminé: ${scanDevicesFound} périphérique(s) trouvé(s)`, 'success');
        resetScanUI();
    } else if (data.status === 'error') {
        showNotification('Erreur durant le scan: ' + data.message, 'error');
        resetScanUI();
    }
});

// ==================== Host Actions ====================
async function deleteHost(ip) {
    if (!confirm(`${t('confirm_delete_host')} ${ip} ?`)) {
        return;
    }

    try {
        const response = await fetch('/api/delete_host', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ip: ip })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                showNotification(`${t('host_deleted')}: ${ip}`, 'info');
                // Force update immediately
                socket.emit('request_update');
            } else {
                showNotification(data.error || 'Erreur lors de la suppression', 'error');
            }
        } else {
            showNotification('Erreur serveur (' + response.status + ')', 'error');
        }
    } catch (error) {
        console.error('Erreur deleteHost:', error);
        showNotification('Erreur réseau', 'error');
    }
}

async function excludeHost(ip, isExcluded) {
    try {
        const endpoint = isExcluded ? '/api/include_host' : '/api/exclude_host';
        const message = isExcluded ? `${t('host_included')}: ${ip}` : `${t('host_excluded')}: ${ip}`;
        const type = isExcluded ? 'success' : 'info';

        const result = await apiCall(endpoint, 'POST', { ip });
        showNotification(message, type);
        socket.emit('request_update');
    } catch (error) { }
}

function editHostName(ip) {
    const ipClean = ip.replace(/\./g, '-');
    const displayEl = document.getElementById(`name-display-${ipClean}`);
    const inputEl = document.getElementById(`name-input-${ipClean}`);

    if (displayEl && inputEl) {
        displayEl.style.display = 'none';
        inputEl.style.display = 'block';
        inputEl.focus();
        inputEl.select();
    }
}

async function saveHostName(ip) {
    const ipClean = ip.replace(/\./g, '-');
    const displayEl = document.getElementById(`name-display-${ipClean}`);
    const inputEl = document.getElementById(`name-input-${ipClean}`);

    if (!inputEl || inputEl.style.display === 'none') return;

    const newName = inputEl.value.trim();

    try {
        const response = await fetch('/api/update_host_name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ip: ip, name: newName })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                if (displayEl) {
                    displayEl.textContent = newName || '-';
                    displayEl.style.display = 'inline-block';
                }
                if (inputEl) {
                    inputEl.style.display = 'none';
                }
                showNotification(`${t('name_modified')} ${ip}`, 'success');
                // Force update immediately
                socket.emit('request_update');
            } else {
                showNotification(data.error || 'Erreur mise à jour nom', 'error');
            }
        } else {
            showNotification('Erreur serveur (' + response.status + ')', 'error');
        }
    } catch (error) {
        console.error('Erreur saveHostName:', error);
        if (displayEl) displayEl.style.display = 'inline-block';
        if (inputEl) inputEl.style.display = 'none';
        showNotification('Erreur réseau', 'error');
    }
}

function editHostComment(ip) {
    const ipClean = ip.replace(/\./g, '-');
    const displayEl = document.getElementById(`comment-display-${ipClean}`);
    const inputEl = document.getElementById(`comment-input-${ipClean}`);

    if (displayEl && inputEl) {
        displayEl.style.display = 'none';
        inputEl.style.display = 'block';
        inputEl.focus();
        inputEl.select();
    }
}

async function saveHostComment(ip) {
    const ipClean = ip.replace(/\./g, '-');
    const displayEl = document.getElementById(`comment-display-${ipClean}`);
    const inputEl = document.getElementById(`comment-input-${ipClean}`);

    if (!inputEl || inputEl.style.display === 'none') return;

    const newComment = inputEl.value.trim();

    try {
        const result = await apiCall('/api/update_comment', 'POST', {
            ip: ip,
            comment: newComment
        });

        if (displayEl) {
            displayEl.textContent = newComment || '-';
            displayEl.style.display = 'inline-block';
        }
        if (inputEl) {
            inputEl.style.display = 'none';
        }

        showNotification(`${t('comment_modified') || 'Commentaire modifié'} ${ip}`, 'success');
        socket.emit('request_update');
    } catch (error) {
        if (displayEl) displayEl.style.display = 'inline-block';
        if (inputEl) inputEl.style.display = 'none';
    }
}

// ==================== Settings ====================
async function loadSettings() {
    try {
        const result = await apiCall('/api/get_settings');

        if (result.delai) {
            document.getElementById('input-delai').value = result.delai;
            document.getElementById('stat-delai').textContent = formatDelay(result.delai);
        }
        if (result.nb_hs) {
            document.getElementById('input-nb-hs').value = result.nb_hs;
        }

        if (result.alerts) {
            document.getElementById('check-popup').checked = result.alerts.popup || false;
            document.getElementById('check-mail').checked = result.alerts.mail || false;
            document.getElementById('check-telegram').checked = result.alerts.telegram || false;
            document.getElementById('check-mail-recap').checked = result.alerts.mail_recap || false;
            document.getElementById('check-db-externe').checked = result.alerts.db_externe || false;
            document.getElementById('check-temp-alert').checked = result.alerts.temp_alert || false;
            document.getElementById('input-temp-seuil').value = result.alerts.temp_seuil || 70;
            document.getElementById('input-temp-seuil-warning').value = result.alerts.temp_seuil_warning || 60;
        }

        if (typeof result.monitoring_running !== 'undefined') {
            monitoringRunning = result.monitoring_running;
            updateMonitoringStatus(result.monitoring_running);
        }

        if (result.smtp) {
            document.getElementById('smtp-server').value = result.smtp.server || '';
            document.getElementById('smtp-port').value = result.smtp.port || '587';
            document.getElementById('smtp-email').value = result.smtp.email || '';
            document.getElementById('smtp-recipients').value = result.smtp.recipients || '';
        }

        if (result.telegram) {
            document.getElementById('telegram-token').value = result.telegram.token || '';
            document.getElementById('telegram-chatid').value = result.telegram.chatid || '';
        }

        if (result.general) {
            document.getElementById('general-site').value = result.general.site || '';
            document.getElementById('general-theme').value = result.general.theme || 'nord';

            if (result.general.advanced_title) {
                const titleEl = document.getElementById('advanced-settings-title');
                const inputEl = document.getElementById('advanced-settings-title-input');
                if (titleEl) titleEl.textContent = result.general.advanced_title;
                if (inputEl) inputEl.textContent = result.general.advanced_title;
            }
        }

        if (result.version) {
            document.getElementById('system-version').textContent = result.version;
        }
    } catch (error) {
        console.error('Settings load error:', error);
    }
}

function editSectionTitle(id) {
    const displayEl = document.getElementById(id);
    const inputEl = document.getElementById(id + '-input');

    if (displayEl && inputEl) {
        displayEl.style.display = 'none';
        inputEl.style.display = 'block';
        inputEl.value = displayEl.textContent;
        inputEl.focus();
        inputEl.select();
    }
}

async function saveSectionTitle(id) {
    const displayEl = document.getElementById(id);
    const inputEl = document.getElementById(id + '-input');

    if (!inputEl || inputEl.style.display === 'none') return;

    const newTitle = inputEl.value.trim();
    if (!newTitle) {
        displayEl.style.display = 'block';
        inputEl.style.display = 'none';
        return;
    }

    try {
        // Pour l'instant on gère seulement advanced-settings-title
        const result = await apiCall('/api/update_general_setting', 'POST', {
            advanced_title: newTitle
        });

        if (displayEl) {
            displayEl.textContent = newTitle;
            displayEl.style.display = 'block';
        }
        if (inputEl) {
            inputEl.style.display = 'none';
        }

        showNotification(t('settings_saved') || 'Titre mis à jour', 'success');
    } catch (error) {
        if (displayEl) displayEl.style.display = 'block';
        if (inputEl) inputEl.style.display = 'none';
    }
}

// ==================== Utility Functions ====================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function toggleAllScanTypes(checked) {
    const checkboxes = [
        'scan-type-hik',
        'scan-type-dahua',
        'scan-type-onvif',
        'scan-type-samsung',
        'scan-type-avigilon',
        'scan-type-upnp',
        'scan-type-snmp',
        'scan-type-ups',
        'scan-type-xiaomi'
    ];

    checkboxes.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.checked = checked;
    });
}

function showBrowserNotification(title, body) {
    if (!("Notification" in window)) {
        return;
    }

    if (Notification.permission === "granted") {
        new Notification(title, {
            body: body,
            icon: '/static/favicon.ico',
            badge: '/static/favicon.ico',
            tag: 'scan-complete',
            requireInteraction: false
        });
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(function (permission) {
            if (permission === "granted") {
                new Notification(title, {
                    body: body,
                    icon: '/static/favicon.ico',
                    badge: '/static/favicon.ico',
                    tag: 'scan-complete'
                });
            }
        });
    }
}

if ("Notification" in window && Notification.permission === "default") {
    setTimeout(() => {
        Notification.requestPermission();
    }, 2000);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Génère une couleur unique par site basée sur son nom
function getSiteColor(siteName) {
    if (!siteName) return { bg: 'rgba(0, 0, 0, 0.3)', text: '#e4e4e4', badge: 'rgba(102, 126, 234, 0.2)' };

    let hash = 0;
    for (let i = 0; i < siteName.length; i++) {
        hash = siteName.charCodeAt(i) + ((hash << 5) - hash);
    }

    const hue = Math.abs(hash % 360);

    return {
        bg: `hsla(${hue}, 60%, 25%, 0.4)`,
        text: `hsl(${hue}, 70%, 65%)`,
        badge: `hsla(${hue}, 70%, 50%, 0.25)`,
        border: `hsla(${hue}, 60%, 50%, 0.3)`
    };
}


function getLatencyClass(latence) {
    if (!latence || latence === '-') return 'offline';

    const latenceStr = String(latence).toLowerCase();

    // Si c'est HS ou contient "hs"
    if (latenceStr === 'hs' || latenceStr.includes('hs')) {
        return 'offline';
    }

    // Extraire la valeur numérique
    const match = latenceStr.match(/[\d.]+/);
    if (!match) return 'good';

    const ms = parseFloat(match[0]);

    if (ms < 20) return 'excellent';      // Vert - Excellent (< 20ms)
    if (ms < 50) return 'good';           // Jaune clair - Bon (20-50ms)
    if (ms < 100) return 'warning';       // Orange - Attention (50-100ms)
    return 'critical';                     // Rouge - Critique (> 100ms)
}

// ==================== Auto-refresh ====================
setInterval(() => {
    socket.emit('request_update');
}, 10000);

// ==================== Accordions ====================
function toggleAccordion(id) {
    const content = document.getElementById('content-' + id);
    const icon = document.getElementById('icon-' + id);
    const header = icon.parentElement;

    if (content.classList.contains('active')) {
        content.classList.remove('active');
        icon.classList.remove('active');
        header.classList.remove('active');
    } else {
        content.classList.add('active');
        icon.classList.add('active');
        header.classList.add('active');
    }
}

// ==================== Configuration SMTP ====================
document.getElementById('form-smtp').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
        server: document.getElementById('smtp-server').value,
        port: document.getElementById('smtp-port').value,
        email: document.getElementById('smtp-email').value,
        password: document.getElementById('smtp-password').value,
        recipients: document.getElementById('smtp-recipients').value
    };

    try {
        const result = await apiCall('/api/save_smtp', 'POST', data);
        showNotification(t('smtp_saved'), 'success');
    } catch (error) { }
});

async function testSMTP() {
    try {
        const result = await apiCall('/api/test_smtp', 'POST', {});
        showNotification(result.message || t('test_email_sent'), 'success');
    } catch (error) { }
}

// ==================== Configuration Telegram ====================
document.getElementById('form-telegram').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
        token: document.getElementById('telegram-token').value,
        chatid: document.getElementById('telegram-chatid').value
    };

    try {
        const result = await apiCall('/api/save_telegram', 'POST', data);
        showNotification(t('telegram_saved'), 'success');
    } catch (error) { }
});

async function testTelegram() {
    try {
        const result = await apiCall('/api/test_telegram', 'POST', {});
        showNotification(result.message || t('telegram_test_sent'), 'success');
    } catch (error) { }
}

// ==================== Email Récapitulatif ====================
document.getElementById('form-mail-recap').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
        heure: document.getElementById('recap-heure').value,
        lundi: document.getElementById('recap-lundi').checked,
        mardi: document.getElementById('recap-mardi').checked,
        mercredi: document.getElementById('recap-mercredi').checked,
        jeudi: document.getElementById('recap-jeudi').checked,
        vendredi: document.getElementById('recap-vendredi').checked,
        samedi: document.getElementById('recap-samedi').checked,
        dimanche: document.getElementById('recap-dimanche').checked
    };

    try {
        const result = await apiCall('/api/save_mail_recap', 'POST', data);
        showNotification(t('recap_saved'), 'success');
    } catch (error) { }
});

async function sendTestRecap() {
    try {
        const result = await apiCall('/api/send_test_recap', 'POST', {});
        showNotification(result.message || t('recap_test_sent'), 'success');
    } catch (error) { }
}

async function loadMailRecapSettings() {
    try {
        const result = await apiCall('/api/get_mail_recap_settings');

        if (result.heure) {
            document.getElementById('recap-heure').value = result.heure;
        }

        document.getElementById('recap-lundi').checked = result.lundi || false;
        document.getElementById('recap-mardi').checked = result.mardi || false;
        document.getElementById('recap-mercredi').checked = result.mercredi || false;
        document.getElementById('recap-jeudi').checked = result.jeudi || false;
        document.getElementById('recap-vendredi').checked = result.vendredi || false;
        document.getElementById('recap-samedi').checked = result.samedi || false;
        document.getElementById('recap-dimanche').checked = result.dimanche || false;
    } catch (error) {
        console.error('Mail recap settings load error:', error);
    }
}

// ==================== Paramètres Généraux ====================
document.getElementById('form-general').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
        site: document.getElementById('general-site').value,
        license: '',
        theme: document.getElementById('general-theme').value
    };

    try {
        const result = await apiCall('/api/save_general', 'POST', data);
        showNotification(t('general_saved'), 'success');
    } catch (error) { }
});

// ==================== Licence ====================
document.getElementById('form-license').addEventListener('submit', async function (e) {
    e.preventDefault();

    const licenseKey = document.getElementById('license-key').value;

    const data = {
        site: document.getElementById('general-site').value,
        license: licenseKey,
        theme: document.getElementById('general-theme').value
    };

    try {
        const result = await apiCall('/api/save_general', 'POST', data);
        showNotification(t('license_saved'), 'success');
        loadLicenseInfo();
    } catch (error) { }
});

// Load settings when opening advanced modal
const btnAdvanced = document.querySelector('[onclick="openSectionModal(\'advanced\')"]');
if (btnAdvanced) {
    btnAdvanced.addEventListener('click', function () {
        loadSettings();
        loadMailRecapSettings();
        loadLicenseInfo();
    });
}
// Also load on DOM ready just in case
document.addEventListener('DOMContentLoaded', function () {
    loadSettings();
});

async function loadLicenseInfo() {
    try {
        const result = await apiCall('/api/get_license_info');

        const icon = document.getElementById('license-icon');
        const status = document.getElementById('license-status');
        const days = document.getElementById('license-days');
        const codeInput = document.getElementById('activation-code');

        if (result.activation_code) {
            codeInput.value = result.activation_code;
        }

        const isLicenseActive = result.active;

        const paidAlerts = ['check-mail', 'check-telegram', 'check-mail-recap', 'check-db-externe'];
        paidAlerts.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.disabled = !isLicenseActive;
                if (!isLicenseActive) {
                    el.checked = false;
                    el.parentElement.title = t('requires_license');
                    el.parentElement.style.opacity = "0.6";
                } else {
                    el.parentElement.title = "";
                    el.parentElement.style.opacity = "1";
                }
            }
        });

        if (isLicenseActive) {
            icon.textContent = '✅';
            status.textContent = t('license_active');
            days.textContent = `${result.days_remaining} ${t('days_remaining')}`;
            status.style.color = '#10b981';
        } else {
            icon.textContent = '❌';
            status.textContent = t('no_license');
            days.textContent = t('features_limited');
            status.style.color = '#ef4444';
        }
    } catch (error) {
        console.error('License info load error:', error);
    }
}

// ==================== Authentification ====================
document.getElementById('btn-logout').addEventListener('click', async function () {
    if (!confirm(t('confirm_logout'))) {
        return;
    }

    try {
        const result = await apiCall('/api/logout', 'POST');
        window.location.href = '/login';
    } catch (error) { }
});

document.getElementById('btn-change-password').addEventListener('click', function () {
    const modal = document.getElementById('modal-change-password');
    modal.style.display = 'flex';
});

document.getElementById('btn-cancel-change').addEventListener('click', function () {
    closeUserModal();
});

function closeUserModal() {
    const modal = document.getElementById('modal-change-password');
    modal.style.display = 'none';
    document.getElementById('form-change-password').reset();
    document.getElementById('form-change-user-password').reset();
}

function switchUserTab(tab) {
    // Masquer tous les contenus
    document.querySelectorAll('.user-tab-content').forEach(c => c.style.display = 'none');
    // Désactiver tous les onglets
    document.querySelectorAll('.user-tab').forEach(t => {
        t.style.background = 'white';
        t.style.color = '#374151';
        t.style.border = '1px solid #e5e7eb';
        t.classList.remove('active');
    });

    // Activer l'onglet sélectionné
    const activeTab = document.querySelector(`.user-tab[data-tab="${tab}"]`);
    if (tab === 'admin') {
        activeTab.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    } else {
        activeTab.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    }
    activeTab.style.color = 'white';
    activeTab.style.border = 'none';
    activeTab.classList.add('active');

    // Afficher le contenu correspondant
    document.getElementById(`tab-${tab}`).style.display = 'block';

    // Charger les infos utilisateur si onglet user
    if (tab === 'user') {
        loadUserCredentials();
    }
}

async function loadUserCredentials() {
    try {
        const result = await apiCall('/api/get_users');
        if (result.users) {
            const userAccount = result.users.find(u => u.role === 'user');
            if (userAccount) {
                document.getElementById('user-new-username').value = userAccount.username;
            }
        }
    } catch (error) {
        console.error('Erreur chargement utilisateurs:', error);
    }
}

document.getElementById('form-change-password').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
        old_password: document.getElementById('old-password').value,
        new_username: document.getElementById('new-username').value,
        new_password: document.getElementById('new-password').value
    };

    try {
        const result = await apiCall('/api/change_credentials', 'POST', data);
        showNotification(t('credentials_changed'), 'success');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    } catch (error) { }
});

document.getElementById('form-change-user-password').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
        role: 'user',
        new_username: document.getElementById('user-new-username').value,
        new_password: document.getElementById('user-new-password').value
    };

    try {
        const result = await apiCall('/api/change_user_credentials', 'POST', data);
        showNotification(t('user_credentials_changed') || 'Identifiants utilisateur modifiés', 'success');
        closeUserModal();
    } catch (error) { }
});

// ==================== User Info ====================
async function loadUserInfo() {
    try {
        const result = await apiCall('/api/user_info');
        if (result.username) {
            document.getElementById('system-user').textContent = result.username;
        }
    } catch (error) {
        console.error('User info load error:', error);
    }
}

// ==================== Gestion des utilisateurs ====================
async function loadUsersList() {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) {
        console.log('Users table body not found');
        return;
    }

    try {
        const result = await apiCall('/api/get_users');
        console.log('Users API result:', result);

        if (result.success && result.users && result.users.length > 0) {
            const currentUser = await getCurrentUsername();

            tbody.innerHTML = result.users.map(user => `
                <tr>
                    <td><strong>${user.username}</strong></td>
                    <td><span class="role-badge ${user.role}">${user.role === 'admin' ? '👑 Admin' : '👤 User'}</span></td>
                    <td>
                        <div class="user-actions">
                            <button class="btn btn-info btn-sm" onclick="changeUserPassword('${user.username}')">
                                🔑 <span data-i18n="change_password">Mot de passe</span>
                            </button>
                            ${user.username !== currentUser ? `
                                <button class="btn btn-warning btn-sm" onclick="changeUserRole('${user.username}', '${user.role}')">
                                    🔄 <span data-i18n="change_role">Rôle</span>
                                </button>
                                <button class="btn btn-danger btn-sm" onclick="deleteUser('${user.username}')">
                                    🗑️ <span data-i18n="delete">Supprimer</span>
                                </button>
                            ` : '<em style="color:#888;" data-i18n="current_user">(Vous)</em>'}
                        </div>
                    </td>
                </tr>
            `).join('');

            // Recharger les traductions pour les nouveaux éléments
            applyTranslations();
        } else if (result.users && result.users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#888;">Aucun utilisateur trouvé</td></tr>';
        } else {
            console.error('Unexpected response:', result);
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#f00;">Erreur de chargement</td></tr>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#f00;">Erreur: ' + error.message + '</td></tr>';
    }
}

async function getCurrentUsername() {
    try {
        const result = await apiCall('/api/user_info');
        return result.username || '';
    } catch {
        return '';
    }
}

async function addUser(username, password, role) {
    try {
        const result = await apiCall('/api/add_user', 'POST', {
            username: username,
            password: password,
            role: role
        });
        if (result.success) {
            showNotification(result.message, 'success');
            loadUsersList();
            return true;
        } else {
            showNotification(result.error || 'Erreur', 'error');
            return false;
        }
    } catch (error) {
        showNotification(error.message, 'error');
        return false;
    }
}

async function deleteUser(username) {
    const t = translations[currentLang];
    if (confirm(t.confirm_delete_user || `Êtes-vous sûr de vouloir supprimer l'utilisateur "${username}" ?`)) {
        try {
            const result = await apiCall('/api/delete_user', 'POST', { username: username });
            if (result.success) {
                showNotification(result.message, 'success');
                loadUsersList();
            } else {
                showNotification(result.error || 'Erreur', 'error');
            }
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }
}

async function changeUserPassword(username) {
    const t = translations[currentLang];
    const newPassword = prompt(t.enter_new_password || `Nouveau mot de passe pour "${username}" :`);
    if (newPassword && newPassword.trim()) {
        try {
            const result = await apiCall('/api/update_user_password', 'POST', {
                username: username,
                new_password: newPassword.trim()
            });
            if (result.success) {
                showNotification(result.message, 'success');
            } else {
                showNotification(result.error || 'Erreur', 'error');
            }
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }
}

async function changeUserRole(username, currentRole) {
    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    const t = translations[currentLang];
    const confirmMsg = t.confirm_change_role || `Changer le rôle de "${username}" de ${currentRole} à ${newRole} ?`;

    if (confirm(confirmMsg)) {
        try {
            const result = await apiCall('/api/update_user_role', 'POST', {
                username: username,
                role: newRole
            });
            if (result.success) {
                showNotification(result.message, 'success');
                loadUsersList();
            } else {
                showNotification(result.error || 'Erreur', 'error');
            }
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }
}

// Fonction globale pour gérer l'ajout d'utilisateur (appelée via onsubmit)
async function handleAddUser(e) {
    e.preventDefault();
    console.log('handleAddUser called!');

    const username = document.getElementById('new-user-username').value.trim();
    const password = document.getElementById('new-user-password').value;
    const role = document.getElementById('new-user-role').value;

    console.log('Adding user:', username, role);

    if (await addUser(username, password, role)) {
        document.getElementById('new-user-username').value = '';
        document.getElementById('new-user-password').value = '';
        document.getElementById('new-user-role').value = 'user';
    }

    return false; // Empêcher la soumission normale du formulaire
}

// Initial load
loadLanguage();
loadSettings();
loadLicenseInfo();
loadUserInfo();
loadMailRecapSettings();
loadUsersList();

// ==================== Navigation depuis le menu hamburger ====================
function closeMenu() {
    const sideMenu = document.getElementById('side-menu');
    const overlay = document.getElementById('menu-overlay');
    const hamburgerBtn = document.getElementById('hamburger-btn');

    if (sideMenu.classList.contains('active')) {
        sideMenu.classList.remove('active');
        overlay.classList.remove('active');
        hamburgerBtn.classList.remove('active');
    }
}

function switchSection(section) {
    // Fermer tous les modaux d'abord
    document.querySelectorAll('.section-modal').forEach(modal => {
        modal.classList.remove('active');
        setTimeout(() => {
            if (!modal.classList.contains('active')) modal.style.display = 'none';
        }, 300);
    });

    // Masquer toutes les sections de contenu inline (toujours, pour repartir de zéro)
    const allContentSections = ['content-accueil', 'content-sites', 'content-dashboards', 'content-backup', 'content-users', 'content-notifications'];
    allContentSections.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('active');
    });

    // Mettre à jour les highlights du menu (Sidebar + Header)
    document.querySelectorAll('.menu-nav-item, .header-nav-btn').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === section) {
            item.classList.add('active');
        }
    });

    // Gérer l'affichage de la section demandée
    const inlineSections = ['accueil', 'sites', 'dashboards', 'backup', 'notifications'];

    if (inlineSections.includes(section)) {
        const target = document.getElementById('content-' + section);
        if (target) {
            target.classList.add('active');
        }

        // Chargement des données au besoin
        if (section === 'sites') loadSites();
        if (section === 'dashboards') loadDashboards();
        if (section === 'users') loadUsersList();

        closeMenu();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        // C'est un modal (ajout, advanced, configuration)
        const modal = document.getElementById('modal-' + section);
        if (modal) {
            modal.style.display = 'flex';
            setTimeout(() => {
                modal.classList.add('active');
                if (section === 'advanced') {
                    loadUsersList();
                }
            }, 10);

            // Pour les modaux, on garde la section de fond visible (accueil par défaut si rien n'est actif)
            // Mais si on arrive d'une autre section, on l'a déjà masquée plus haut
            // Donc si on ouvre un modal, on doit s'assurer qu'UN fond reste visible (accueil)
            let backgroundActive = false;
            inlineSections.forEach(s => {
                if (document.getElementById('content-' + s).classList.contains('active')) backgroundActive = true;
            });
            if (!backgroundActive) {
                const home = document.getElementById('content-accueil');
                if (home) home.classList.add('active');
            }
        }
        closeMenu();

        // Scroll logic for modals
        const modalBody = modal ? modal.querySelector('.section-modal-body') : null;
        if (modalBody) {
            modalBody.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }
}

function closeSectionModal(section) {
    const modal = document.getElementById('modal-' + section);
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
    // Réactiver l'item de la section inline visible dans le menu
    let targetSection = 'accueil';
    ['sites', 'backup', 'users', 'notifications'].forEach(s => {
        const el = document.getElementById('content-' + s);
        if (el && el.classList.contains('active')) {
            targetSection = s;
        }
    });

    document.querySelectorAll('.menu-nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === targetSection) {
            item.classList.add('active');
        }
    });
}

// Fermer les modaux en cliquant sur l'overlay
document.querySelectorAll('.section-modal').forEach(modal => {
    modal.addEventListener('click', function (e) {
        if (e.target === this) {
            const sectionId = this.id.replace('modal-', '');
            closeSectionModal(sectionId);
        }
    });
});

// ==================== Host Settings ====================
async function openHostSettings(ip, name) {
    const modal = document.getElementById('modal-host-settings');
    const title = document.getElementById('host-settings-ip');
    const inputIp = document.getElementById('host-settings-ip-input');

    // Set title and hidden input
    if (title) title.textContent = (name && name !== 'undefined' && name !== '-') ? `${name} (${ip})` : ip;
    if (inputIp) inputIp.value = ip;

    // Show modal
    if (modal) {
        modal.style.display = 'flex';
        // Force reflow
        void modal.offsetWidth;
        modal.classList.add('active');
    }

    // Reset checkboxes while loading
    const emailCheck = document.getElementById('host-setting-email');
    const telegramCheck = document.getElementById('host-setting-telegram');
    if (emailCheck) emailCheck.checked = true;
    if (telegramCheck) telegramCheck.checked = true;

    // Load current settings
    try {
        const result = await apiCall(`/api/host/settings/${ip}`, 'GET');
        if (result.success && result.settings) {
            if (emailCheck) emailCheck.checked = result.settings.email;
            if (telegramCheck) telegramCheck.checked = result.settings.telegram;
        }
    } catch (e) {
        console.error('Erreur chargement settings host:', e);
        showNotification('Impossible de charger les paramètres', 'error');
    }
}

// Host Settings Form Submission
const formHostSettings = document.getElementById('form-host-settings');
if (formHostSettings) {
    formHostSettings.addEventListener('submit', async function (e) {
        e.preventDefault();
        const ip = document.getElementById('host-settings-ip-input').value;
        const email = document.getElementById('host-setting-email').checked;
        const telegram = document.getElementById('host-setting-telegram').checked;

        try {
            const result = await apiCall(`/api/host/settings/${ip}`, 'POST', {
                email: email,
                telegram: telegram
            });

            if (result.success) {
                showNotification(t('settings_saved') || 'Paramètres sauvegardés', 'success');
                closeSectionModal('host-settings');
                // Trigger an update request to refresh status if needed (though local list logic should handle it)
                socket.emit('request_update');
            } else {
                showNotification(result.error, 'error');
            }
        } catch (e) {
            showNotification('Erreur sauvegarde settings', 'error');
        }
    });
}

// ==================== Dashboards Management ====================
async function loadDashboards() {
    const list = document.getElementById('dashboards-list');
    if (!list) return;

    list.innerHTML = '<div class="loading-spinner">Chargement...</div>';

    try {
        const result = await apiCall('/api/dashboards', 'GET');
        if (result.success && result.dashboards) {
            if (result.dashboards.length === 0) {
                list.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">Aucun tableau de bord créé.</div>';
                return;
            }

            list.innerHTML = result.dashboards.map(d => `
                <div class="status-card" style="position: relative;">
                    <div style="font-size: 32px; margin-bottom: 10px;">📊</div>
                    <h3>${escapeHtml(d.name)}</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 15px;">
                        ${d.hosts ? d.hosts.length : 0} hôte(s)
                    </p>
                    <div style="display: flex; gap: 10px; justify-content: center;">
                        <button class="btn btn-primary btn-sm" onclick="openDashboardModal(${d.id})">Modifier</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteDashboard(${d.id})">Supprimer</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('Erreur loading dashboards:', e);
        list.innerHTML = '<div class="error-message">Erreur de chargement</div>';
    }
}

async function openDashboardModal(id = null) {
    const modal = document.getElementById('modal-dashboard');
    const form = document.getElementById('form-dashboard');
    const title = document.getElementById('dashboard-modal-title');

    // Reset form
    form.reset();
    document.getElementById('dashboard-id').value = '';
    document.getElementById('dashboard-hosts-list').innerHTML = '';

    if (id) {
        title.setAttribute('data-i18n', 'edit_dashboard');
        title.textContent = 'Modifier Tableau de Bord';
        document.getElementById('dashboard-id').value = id;

        // Load dashboard details
        try {
            const result = await apiCall(`/api/dashboards/${id}`, 'GET');
            if (result.success) {
                document.getElementById('dashboard-name').value = result.dashboard.name;
                populateDashboardHosts(result.dashboard.hosts);
            }
        } catch (e) {
            showNotification('Erreur chargement dashboard', 'error');
            return;
        }
    } else {
        title.setAttribute('data-i18n', 'create_dashboard');
        title.textContent = 'Créer Tableau de Bord';
        populateDashboardHosts([]);
    }

    modal.classList.add('active');
    modal.style.display = 'flex';
}

function populateDashboardHosts(selectedIps) {
    const tbody = document.getElementById('dashboard-hosts-list');
    if (!tbody) return;

    // Use the global hostsData loaded in admin.js
    tbody.innerHTML = hostsData.map(h => {
        const isChecked = selectedIps.includes(h.ip);
        return `
            <tr data-ip="${h.ip}" data-name="${(h.nom || '').toLowerCase()}" data-site="${(h.site || '').toLowerCase()}">
                <td><input type="checkbox" name="dashboard_hosts" value="${h.ip}" ${isChecked ? 'checked' : ''}></td>
                <td>${escapeHtml(h.ip)}</td>
                <td>${escapeHtml(h.nom || '-')}</td>
                <td>${escapeHtml(h.site || '-')}</td>
            </tr>
        `;
    }).join('');
}

function filterDashboardHosts() {
    const filter = document.getElementById('dashboard-hosts-search').value.toLowerCase();
    const rows = document.querySelectorAll('#dashboard-hosts-list tr');

    rows.forEach(row => {
        const ip = row.dataset.ip.toLowerCase();
        const name = row.dataset.name;
        const site = row.dataset.site;

        if (ip.includes(filter) || name.includes(filter) || site.includes(filter)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function toggleAllDashboardHosts(checkbox) {
    const checkboxes = document.querySelectorAll('input[name="dashboard_hosts"]');
    checkboxes.forEach(cb => {
        // Only toggle visible rows
        if (cb.closest('tr').style.display !== 'none') {
            cb.checked = checkbox.checked;
        }
    });
}

async function deleteDashboard(id) {
    if (!confirm('Voulez-vous vraiment supprimer ce tableau de bord ?')) return;

    try {
        const result = await apiCall(`/api/dashboards/${id}`, 'DELETE');
        if (result.success) {
            showNotification('Tableau de bord supprimé', 'success');
            loadDashboards();
            socket.emit('request_update');
        } else {
            showNotification(result.error, 'error');
        }
    } catch (e) {
        showNotification('Erreur suppression', 'error');
    }
}

// Form logic
const formDashboard = document.getElementById('form-dashboard');
if (formDashboard) {
    formDashboard.addEventListener('submit', async function (e) {
        e.preventDefault();

        const id = document.getElementById('dashboard-id').value;
        const name = document.getElementById('dashboard-name').value;

        const checkboxes = document.querySelectorAll('input[name="dashboard_hosts"]:checked');
        const hosts = Array.from(checkboxes).map(cb => cb.value);

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/dashboards/${id}` : '/api/dashboards';

        try {
            const result = await apiCall(url, method, { name, hosts });
            if (result.success) {
                showNotification('Tableau de bord enregistré', 'success');
                closeSectionModal('dashboard');
                loadDashboards();
                socket.emit('request_update');
            } else {
                showNotification(result.error, 'error');
            }
        } catch (e) {
            showNotification('Erreur enregistrement', 'error');
        }
    });
}
