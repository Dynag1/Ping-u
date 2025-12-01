# -*- coding: utf-8 -*-
"""
Module d'envoi d'emails avec templates HTML
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from src import db, var
from src.utils.logger import get_logger

logger = get_logger(__name__)



def get_email_template_alert(host_info, alert_type='down'):
    """
    Template HTML pour les alertes d'hôte
    alert_type: 'down' ou 'up'
    """
    
    # Couleurs selon le type d'alerte
    if alert_type == 'down':
        color = '#e74c3c'
        bg_color = '#fadbd8'
        icon = '❌'
        status_text = 'HORS LIGNE'
    else:
        color = '#27ae60'
        bg_color = '#d5f4e6'
        icon = '✅'
        status_text = 'EN LIGNE'
    
    ip = host_info.get('ip', 'N/A')
    nom = host_info.get('nom', ip)
    mac = host_info.get('mac', 'N/A')
    latence = host_info.get('latence', 'N/A')
    timestamp = datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
    site_name = var.nom_site if hasattr(var, 'nom_site') and var.nom_site else 'Votre réseau'
    
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alerte Réseau - Ping ü</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 0; text-align: center;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                {icon} Ping ü
                            </h1>
                            <p style="margin: 10px 0 0 0; color: #e3e8ff; font-size: 16px;">
                                Système de Monitoring Réseau
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Alert Badge -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px; text-align: center;">
                            <div style="background-color: {bg_color}; border-left: 5px solid {color}; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                                <h2 style="margin: 0 0 10px 0; color: {color}; font-size: 24px; font-weight: 700;">
                                    {icon} Hôte {status_text}
                                </h2>
                                <p style="margin: 0; color: #555555; font-size: 14px;">
                                    Alerte détectée le {timestamp}
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Host Information -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; overflow: hidden;">
                                <tr>
                                    <td colspan="2" style="padding: 15px; background-color: #667eea; color: #ffffff; font-weight: 700; font-size: 16px;">
                                        📊 Informations de l'hôte
                                    </td>
                                </tr>
                                <tr style="border-bottom: 1px solid #dee2e6;">
                                    <td style="padding: 15px; font-weight: 600; color: #495057; width: 40%;">
                                        🌐 Nom :
                                    </td>
                                    <td style="padding: 15px; color: #212529; font-weight: 500;">
                                        {nom}
                                    </td>
                                </tr>
                                <tr style="border-bottom: 1px solid #dee2e6;">
                                    <td style="padding: 15px; font-weight: 600; color: #495057;">
                                        🔢 Adresse IP :
                                    </td>
                                    <td style="padding: 15px; color: #212529; font-family: 'Courier New', monospace; font-weight: 600;">
                                        {ip}
                                    </td>
                                </tr>
                                <tr style="border-bottom: 1px solid #dee2e6;">
                                    <td style="padding: 15px; font-weight: 600; color: #495057;">
                                        📡 Adresse MAC :
                                    </td>
                                    <td style="padding: 15px; color: #212529; font-family: 'Courier New', monospace;">
                                        {mac}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px; font-weight: 600; color: #495057;">
                                        ⚡ Latence :
                                    </td>
                                    <td style="padding: 15px; color: #212529; font-weight: 500;">
                                        {latence}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Site Info -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px; text-align: center;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px;">
                                Site surveillé : <strong>{site_name}</strong>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 25px 30px; text-align: center; border-radius: 0 0 12px 12px;">
                            <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 12px;">
                                Ce message a été envoyé automatiquement par Ping ü
                            </p>
                            <p style="margin: 0; color: #adb5bd; font-size: 11px;">
                                © {datetime.now().year} Ping ü - Tous droits réservés
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html


def get_email_template_recap(hosts_data, stats):
    """
    Template HTML pour le récapitulatif périodique
    """
    timestamp = datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
    site_name = var.nom_site if hasattr(var, 'nom_site') and var.nom_site else 'Votre réseau'
    
    # Statistiques
    total_hosts = stats.get('total', 0)
    online_hosts = stats.get('online', 0)
    offline_hosts = stats.get('offline', 0)
    availability = stats.get('availability', 0)
    
    # Couleur selon la disponibilité
    if availability >= 95:
        status_color = '#27ae60'
        status_icon = '🟢'
        status_text = 'Excellent'
    elif availability >= 80:
        status_color = '#f39c12'
        status_icon = '🟡'
        status_text = 'Bon'
    else:
        status_color = '#e74c3c'
        status_icon = '🔴'
        status_text = 'Attention requise'
    
    # Générer les lignes du tableau
    rows_html = ""
    for host in hosts_data[:20]:  # Limiter à 20 hôtes
        ip = host.get('ip', 'N/A')
        nom = host.get('nom', ip)
        status = host.get('status', 'offline')
        latence = host.get('latence', 'N/A')
        
        if status == 'online':
            status_badge = '<span style="background-color: #d5f4e6; color: #27ae60; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">✓ EN LIGNE</span>'
        else:
            status_badge = '<span style="background-color: #fadbd8; color: #e74c3c; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">✗ HORS LIGNE</span>'
        
        rows_html += f"""
        <tr style="border-bottom: 1px solid #dee2e6;">
            <td style="padding: 12px 15px; color: #212529; font-weight: 500;">{nom}</td>
            <td style="padding: 12px 15px; color: #495057; font-family: 'Courier New', monospace;">{ip}</td>
            <td style="padding: 12px 15px; text-align: center;">{status_badge}</td>
            <td style="padding: 12px 15px; text-align: center; color: #495057;">{latence}</td>
        </tr>
        """
    
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Récapitulatif Réseau - Ping ü</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px; text-align: center;">
                <table role="presentation" style="max-width: 800px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 36px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                📊 Ping ü
                            </h1>
                            <p style="margin: 10px 0 0 0; color: #e3e8ff; font-size: 18px; font-weight: 500;">
                                Récapitulatif du Monitoring Réseau
                            </p>
                            <p style="margin: 8px 0 0 0; color: #b8c5ff; font-size: 14px;">
                                {timestamp}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Status Overview -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px;">
                            <div style="background: linear-gradient(135deg, {status_color}22 0%, {status_color}11 100%); border-left: 5px solid {status_color}; padding: 20px; border-radius: 8px; text-align: center;">
                                <h2 style="margin: 0 0 10px 0; color: {status_color}; font-size: 28px; font-weight: 700;">
                                    {status_icon} État du réseau : {status_text}
                                </h2>
                                <p style="margin: 0; color: #555555; font-size: 16px;">
                                    Disponibilité globale : <strong style="font-size: 24px; color: {status_color};">{availability}%</strong>
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Statistics Cards -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 0 10px 0 0; width: 33.33%;">
                                        <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                            <p style="margin: 0 0 8px 0; color: #ffffff; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Total</p>
                                            <p style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">{total_hosts}</p>
                                            <p style="margin: 8px 0 0 0; color: #d4e6f7; font-size: 12px;">Hôtes</p>
                                        </div>
                                    </td>
                                    <td style="padding: 0 5px; width: 33.33%;">
                                        <div style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%); padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                            <p style="margin: 0 0 8px 0; color: #ffffff; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">En ligne</p>
                                            <p style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">{online_hosts}</p>
                                            <p style="margin: 8px 0 0 0; color: #d5f4e6; font-size: 12px;">Actifs</p>
                                        </div>
                                    </td>
                                    <td style="padding: 0 0 0 10px; width: 33.33%;">
                                        <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                            <p style="margin: 0 0 8px 0; color: #ffffff; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Hors ligne</p>
                                            <p style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">{offline_hosts}</p>
                                            <p style="margin: 8px 0 0 0; color: #fadbd8; font-size: 12px;">Inactifs</p>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Hosts Table -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <h3 style="margin: 0 0 15px 0; color: #2c3e50; font-size: 20px; font-weight: 700;">
                                📋 Liste des hôtes surveillés
                            </h3>
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; overflow: hidden;">
                                <thead>
                                    <tr style="background-color: #667eea; color: #ffffff;">
                                        <th style="padding: 12px 15px; text-align: left; font-weight: 600; font-size: 14px;">Nom</th>
                                        <th style="padding: 12px 15px; text-align: left; font-weight: 600; font-size: 14px;">IP</th>
                                        <th style="padding: 12px 15px; text-align: center; font-weight: 600; font-size: 14px;">Statut</th>
                                        <th style="padding: 12px 15px; text-align: center; font-weight: 600; font-size: 14px;">Latence</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows_html}
                                </tbody>
                            </table>
                            {f'<p style="margin: 15px 0 0 0; color: #6c757d; font-size: 13px; text-align: center;">... et {len(hosts_data) - 20} autres hôtes</p>' if len(hosts_data) > 20 else ''}
                        </td>
                    </tr>
                    
                    <!-- Site Info -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px; text-align: center;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px;">
                                Site surveillé : <strong style="color: #495057; font-size: 16px;">{site_name}</strong>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 25px 30px; text-align: center; border-radius: 0 0 12px 12px;">
                            <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 12px;">
                                Ce rapport a été généré automatiquement par Ping ü
                            </p>
                            <p style="margin: 0; color: #adb5bd; font-size: 11px;">
                                © {datetime.now().year} Ping ü - Système de Monitoring Réseau
                            </p>
                            <p style="margin: 10px 0 0 0; color: #adb5bd; font-size: 11px;">
                                Pour toute question, contactez votre administrateur réseau
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html


def send_alert_email(host_info, alert_type='down'):
    """
    Envoie un email d'alerte pour un hôte
    """
    try:
        # Charger les paramètres SMTP
        smtp_params = db.lire_param_mail()
        if not smtp_params or len(smtp_params) < 5:
            logger.error("Paramètres SMTP non configurés")
            return False
        
        # Ordre correct des paramètres dans la DB (sFenetre.py):
        # [0]=email, [1]=password, [2]=port, [3]=server, [4]=recipients, [5]=telegram_chatid
        smtp_email = smtp_params[0]
        smtp_password = smtp_params[1]
        smtp_port = int(smtp_params[2])
        smtp_server = smtp_params[3]
        recipients = smtp_params[4]
        
        if not all([smtp_server, smtp_email, recipients]):
            logger.error("Configuration SMTP incomplète")
            return False
        
        # Créer le message
        message = MIMEMultipart('alternative')
        message['From'] = smtp_email
        message['To'] = recipients
        
        # Sujet selon le type d'alerte
        if alert_type == 'down':
            message['Subject'] = f"🚨 Alerte : Hôte {host_info.get('nom', host_info.get('ip'))} HORS LIGNE"
        else:
            message['Subject'] = f"✅ Hôte {host_info.get('nom', host_info.get('ip'))} DE RETOUR EN LIGNE"
        
        # Version texte simple
        text_body = f"""
Alerte Ping ü - {alert_type.upper()}

Hôte : {host_info.get('nom', 'N/A')}
IP : {host_info.get('ip', 'N/A')}
MAC : {host_info.get('mac', 'N/A')}
Latence : {host_info.get('latence', 'N/A')}
Date : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}

Ce message a été envoyé automatiquement par Ping ü.
"""
        
        # Version HTML
        html_body = get_email_template_alert(host_info, alert_type)
        
        # Attacher les deux versions
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        message.attach(part1)
        message.attach(part2)
        
        # Envoyer l'email
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as server:
                server.login(smtp_email, smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.send_message(message)
        
        logger.info(f"Email d'alerte {alert_type} envoyé pour {host_info.get('ip')}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur envoi email alerte: {e}", exc_info=True)
        return False


def send_recap_email(hosts_data, test_mode=False):
    """
    Envoie un email récapitulatif
    """
    try:
        # Charger les paramètres SMTP
        smtp_params = db.lire_param_mail()
        if not smtp_params or len(smtp_params) < 5:
            logger.error("Paramètres SMTP non configurés")
            return False
        
        # Ordre correct des paramètres dans la DB (sFenetre.py):
        # [0]=email, [1]=password, [2]=port, [3]=server, [4]=recipients, [5]=telegram_chatid
        smtp_email = smtp_params[0]
        smtp_password = smtp_params[1]
        smtp_port = int(smtp_params[2])
        smtp_server = smtp_params[3]
        recipients = smtp_params[4]
        
        if not all([smtp_server, smtp_email, recipients]):
            logger.error("Configuration SMTP incomplète")
            return False
        
        # Calculer les statistiques
        total = len(hosts_data)
        online = sum(1 for h in hosts_data if h.get('status') == 'online')
        offline = total - online
        availability = round((online / total * 100) if total > 0 else 0, 1)
        
        stats = {
            'total': total,
            'online': online,
            'offline': offline,
            'availability': availability
        }
        
        # Créer le message
        message = MIMEMultipart('alternative')
        message['From'] = smtp_email
        message['To'] = recipients
        
        if test_mode:
            message['Subject'] = f"🧪 TEST - Récapitulatif Ping ü - {availability}% disponibilité"
        else:
            message['Subject'] = f"📊 Récapitulatif Ping ü - {availability}% disponibilité - {datetime.now().strftime('%d/%m/%Y')}"
        
        # Version texte simple
        text_body = f"""
Récapitulatif Ping ü
Date : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}

STATISTIQUES :
- Total d'hôtes : {total}
- En ligne : {online}
- Hors ligne : {offline}
- Disponibilité : {availability}%

{'=' * 50}
LISTE DES HÔTES :
{'=' * 50}

"""
        for host in hosts_data[:20]:
            status_text = "✓ EN LIGNE" if host.get('status') == 'online' else "✗ HORS LIGNE"
            text_body += f"{host.get('nom', 'N/A')} - {host.get('ip', 'N/A')} - {status_text}\n"
        
        if len(hosts_data) > 20:
            text_body += f"\n... et {len(hosts_data) - 20} autres hôtes\n"
        
        text_body += "\nCe rapport a été généré automatiquement par Ping ü."
        
        # Version HTML
        html_body = get_email_template_recap(hosts_data, stats)
        
        # Attacher les deux versions
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        message.attach(part1)
        message.attach(part2)
        
        # Envoyer l'email
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as server:
                server.login(smtp_email, smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.send_message(message)
        
        logger.info(f"Email récapitulatif envoyé ({total} hôtes, {availability}% disponibilité)")
        return True
        
    except Exception as e:
        logger.error(f"Erreur envoi email récapitulatif: {e}", exc_info=True)
        return False

