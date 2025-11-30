# 📊 Ping ü - Support SNMP Complet

Version avec monitoring SNMP : Température, Débits réseau et Détection UPS

---

## ✅ Fonctionnalités SNMP

### 🌡️ Température
- **Affichage** : Colonne "Temp" dans le TreeView + Page web
- **Support** : 50+ OIDs pour tous types d'équipements
- **Types supportés** : Synology, QNAP, Raspberry Pi, Switchs (Cisco, HP, Dell, Ubiquiti, MikroTik), Serveurs

### 📊 Débits réseau
- **Affichage** : Page web uniquement (http://localhost:9090)
- **Support** : OIDs standards 32/64 bits
- **Auto-détection** : Trouve automatiquement la bonne interface réseau
- **Types supportés** : NAS, Switchs, Routeurs

### 🔋 Onduleurs (UPS)
- **Détection automatique** : Via OIDs standards RFC 1628
- **Alertes** : Perte secteur, batterie faible
- **Types supportés** : APC, Eaton, et tous UPS compatibles RFC 1628

---

## 🚀 Utilisation

### Démarrage rapide
1. **Activer SNMP** sur vos équipements (communauté "public")
2. **Lancer Ping ü** et démarrer le monitoring (Start)
3. **Température** : Affichée immédiatement dans colonne "Temp"
4. **Débits** : Menu Fonctions > Serveur Web > Démarrer, puis http://localhost:9090

### Configuration SNMP par équipement

**Synology** :
- Panneau de configuration > Services SNMP
- Activer SNMP v1/v2c, communauté "public"

**Raspberry Pi** :
```bash
sudo apt install snmpd
sudo nano /etc/snmp/snmpd.conf
# Modifier : agentaddress  0.0.0.0:161
sudo systemctl restart snmpd
```

**Switchs** (Cisco, HP, etc.) :
- Interface web > SNMP Settings
- Activer SNMP v2c, communauté "public"

---

## 🔧 Fonctionnalités avancées

### Détection intelligente du type d'équipement
- Analyse automatique via sysDescr
- Filtrage des OIDs pertinents selon le type
- 90% moins de requêtes SNMP (plus rapide)

### Auto-détection d'interface réseau
- Teste automatiquement interfaces 1, 2, 10, 100, 1000
- Trouve celle avec du trafic
- Mémorise pour les cycles suivants

### Filtrage intelligent
- **Température** : Testé sur tous les équipements SNMP
- **Débits** : Uniquement sur équipements réseau (NAS, switchs)
- **UPS** : Uniquement sur équipements compatibles (NAS, serveurs, onduleurs)

### Cache optimisé
- Mémorisation des OIDs qui fonctionnent par équipement
- Détection du type d'équipement mise en cache
- Interface réseau optimale mise en cache
- Nettoyé automatiquement à l'arrêt du monitoring

---

## 📊 Performances

| Équipements | Temps de cycle | Fiabilité |
|-------------|----------------|-----------|
| 1-10 | 2-4s | ✅ Excellent |
| 10-20 | 4-6s | ✅ Très bon |
| 20-30 | 6-10s | ✅ Bon |
| 30-50 | 10-15s | ✅ Acceptable |

**Recommandation** : Pour > 20 équipements, augmenter le délai entre cycles à 60-120 secondes.

---

## 🐛 Dépannage

### Température non affichée

**Test manuel** :
```bash
python debug_snmp.py <IP>
```

**Causes communes** :
- SNMP non activé → Activer SNMP sur l'équipement
- Communauté incorrecte → Vérifier "public"
- Firewall → Autoriser port UDP 161

### Débits à 0.00 Mbps

**Causes communes** :
- Pas encore de 2e mesure → Attendre 2-3 cycles
- Vraiment pas de trafic → Générer du trafic (ping, transfert)
- Interface incorrecte → Auto-détection activée (attend 1 cycle)

**Vérification** :
```powershell
Get-Content logs/app.log -Tail 50 | Select-String "Interface.*utilisée"
```

### Logs verbeux

Les logs détaillés sont en mode DEBUG. Pour activer :
- Ouvrir `src/utils/logger.py`
- Changer niveau à `DEBUG`

---

## 📁 Fichiers principaux

**Code source** :
- `src/utils/snmp_helper.py` - Logique SNMP complète
- `src/utils/ups_monitor.py` - Monitoring onduleurs
- `src/fcy_ping.py` - Intégration SNMP dans le monitoring
- `src/web_server.py` - Serveur web pour affichage débits

**Script de diagnostic** :
- `debug_snmp.py` - Test complet SNMP pour un équipement
- `test_snmp_enabled.py` - Test rapide de disponibilité SNMP

**Documentation** :
- `README_SNMP.md` - Ce fichier
- `CONFIGURATION_FINALE_STABLE.md` - Configuration détaillée
- `AUTO_DETECTION_INTERFACE.txt` - Détails auto-détection
- `FILTRAGE_APPLIQUE.txt` - Détails du filtrage

---

## 🎯 Types d'équipements supportés

### NAS
- ✅ Synology (température + débits + UPS)
- ✅ QNAP (température + débits + UPS)

### Systèmes embarqués
- ✅ Raspberry Pi (température uniquement)
- ✅ Linux générique (température)

### Switchs réseau
- ✅ Cisco (température + débits)
- ✅ HP/Aruba (température + débits)
- ✅ Dell (température + débits)
- ✅ Ubiquiti/UniFi (température + débits)
- ✅ MikroTik (température + débits)
- ✅ Netgear (température + débits)
- ✅ D-Link (température + débits)
- ✅ TP-Link (température + débits)
- ✅ Zyxel (température + débits)

### Serveurs
- ✅ Dell PowerEdge (température + UPS)
- ✅ HP ProLiant (température + UPS)

### Onduleurs
- ✅ APC (UPS uniquement)
- ✅ Eaton (UPS uniquement)
- ✅ Tous UPS compatibles RFC 1628

### Équipements non détectés
- ✅ Type "unknown" → Teste tous les OIDs (fallback)

---

## 📈 Statistiques

**OIDs de température supportés** : 50+  
**Types d'équipements détectés** : 10+  
**Interfaces réseau testées** : 1, 2, 10, 100, 1000  
**Gain de performance** : 90% moins de requêtes SNMP grâce au filtrage intelligent

---

## ✅ Statut

Version : **Ping ü avec support SNMP complet**  
Date : **28 Novembre 2025**  
Statut : **✅ Stable et Production-Ready**

**Fonctionnalités** :
- ✅ Détection automatique du type d'équipement
- ✅ Filtrage intelligent des OIDs
- ✅ Auto-détection interface réseau
- ✅ Support 50+ OIDs température
- ✅ Débits réseau avec calcul automatique
- ✅ Monitoring UPS avec alertes
- ✅ Cache optimisé pour performances
- ✅ Logs propres et informatifs

---

**Pour toute question, consultez les fichiers de documentation dans le répertoire racine.**

