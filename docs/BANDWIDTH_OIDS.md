# Documentation des OIDs pour la bande passante

## Vue d'ensemble

Le fichier `src/utils/snmp_helper.py` contient maintenant un dictionnaire complet `BANDWIDTH_OIDS` qui référence les OID SNMP pour la bande passante de tous les types d'équipements supportés.

## Types d'équipements supportés

### 1. **Linux (Ubuntu, Debian, etc.)**
- OIDs standards IF-MIB (RFC 2863)
- Compteurs 32 bits et 64 bits (High Capacity)
- Interfaces indexées (eth0, eth1, wlan0, etc.)

### 2. **Raspberry Pi**
- Utilise Net-SNMP (identique à Linux)
- Supporte tous les modèles (Pi 3, Pi 4, Pi 5, Pi Zero)
- OIDs standards IF-MIB

### 3. **Windows**
- Nécessite le service SNMP activé
- OIDs standards IF-MIB
- Compteurs 32 bits et 64 bits

### 4. **NAS (Synology, QNAP)**
- Synology : OIDs standards IF-MIB
- QNAP : OIDs standards IF-MIB
- Support des interfaces multiples

### 5. **Switches réseau**
- **Cisco** : IF-MIB + OIDs propriétaires
- **HP/Aruba** : IF-MIB standard
- **Dell** : IF-MIB standard
- **Ubiquiti** (EdgeSwitch, UniFi) : IF-MIB standard
- **MikroTik** (RouterOS) : IF-MIB standard
- **Netgear, D-Link, TP-Link, Zyxel** : IF-MIB standard

### 6. **Box Internet**
- **Freebox** (Free) : IF-MIB standard
- **Livebox** (Orange) : IF-MIB standard
- **Bbox** (Bouygues) : IF-MIB standard
- **SFR Box** : IF-MIB standard

### 7. **Serveurs**
- **Dell iDRAC** : IF-MIB standard
- **HP iLO** : IF-MIB standard
- **Supermicro IPMI** : IF-MIB standard

## OIDs principaux

### OIDs standards IF-MIB (utilisés par défaut)

| OID | Description | Usage |
|-----|-------------|-------|
| `1.3.6.1.2.1.2.2.1.10` | ifInOctets | Octets reçus (32 bits) + index interface |
| `1.3.6.1.2.1.2.2.1.16` | ifOutOctets | Octets envoyés (32 bits) + index interface |
| `1.3.6.1.2.1.31.1.1.1.6` | ifHCInOctets | Octets reçus (64 bits, High Capacity) + index |
| `1.3.6.1.2.1.31.1.1.1.10` | ifHCOutOctets | Octets envoyés (64 bits, High Capacity) + index |
| `1.3.6.1.2.1.2.2.1.5` | ifSpeed | Vitesse interface en bps + index |
| `1.3.6.1.2.1.31.1.1.1.15` | ifHighSpeed | Vitesse interface en Mbps + index |
| `1.3.6.1.2.1.2.2.1.2` | ifDescr | Description de l'interface + index |
| `1.3.6.1.2.1.2.2.1.8` | ifOperStatus | Statut opérationnel (1=up, 2=down) + index |

### Utilisation des index d'interface

Les OIDs de bande passante nécessitent un **index d'interface** à la fin de l'OID :

- **Exemple Linux** : `1.3.6.1.2.1.2.2.1.10.2` (eth0 est généralement l'interface 2)
- **Exemple Windows** : `1.3.6.1.2.1.2.2.1.10.1` (première interface réseau)
- **Exemple Raspberry Pi** : `1.3.6.1.2.1.2.2.1.10.2` (eth0) ou `.3` (wlan0)

## Utilisation dans le code

Le code existant utilise déjà ces OIDs de manière automatique :

### Méthode 1 : Récupération du trafic brut

```python
from src.utils.snmp_helper import snmp_helper

# Récupérer les compteurs de trafic pour une interface
traffic = await snmp_helper.get_interface_traffic("192.168.1.100", interface_index=2)
# Retourne: {'in': octets_in, 'out': octets_out, 'timestamp': time.time()}
```

### Méthode 2 : Calcul de la bande passante (débit)

```python
from src.utils.snmp_helper import snmp_helper

# Calculer la bande passante entre deux mesures
bandwidth = await snmp_helper.calculate_bandwidth(
    "192.168.1.100", 
    interface_index=2, 
    previous_data=previous_traffic
)
# Retourne: {'in_mbps': float, 'out_mbps': float, 'raw_data': current_data}
```

### Méthode 3 : Détection automatique de l'interface

```python
from src.utils.snmp_helper import snmp_helper

# Trouver automatiquement la meilleure interface
interface_index = await snmp_helper.find_best_interface("192.168.1.100")
print(f"Meilleure interface: {interface_index}")
```

## Note importante

**Tous les équipements listés utilisent les OIDs standards IF-MIB.**

La raison pour laquelle le dictionnaire `BANDWIDTH_OIDS` contient des entrées spécifiques par constructeur (comme `linux_if_in`, `raspberry_if_in`, `cisco_if_in`, etc.) est pour :

1. **Documentation** : Clarifier que ces OIDs fonctionnent sur ces équipements
2. **Extensibilité future** : Permettre d'ajouter facilement des OIDs propriétaires si nécessaire
3. **Cohérence** : Avoir une structure similaire à `TEMPERATURE_OIDS`

Le code actuel utilise directement les OIDs standards `ifHCInOctets` et `ifHCOutOctets` (ou `ifInOctets` et `ifOutOctets` en fallback) qui fonctionnent sur tous les équipements.

## Démarrage rapide

### Activer SNMP sur vos équipements

#### Linux (Ubuntu/Debian/Raspberry Pi)
```bash
sudo apt-get install snmpd
sudo nano /etc/snmp/snmpd.conf
# Modifier : agentAddress udp:161,udp6:[::1]:161
# Ajouter : rocommunity public 192.168.1.0/24
sudo systemctl restart snmpd
```

#### Windows
```
1. Panneau de configuration → Programmes → Activer ou désactiver des fonctionnalités Windows
2. Cocher "Protocole SNMP (Simple Network Management Protocol)"
3. Services → SNMP Service → Propriétés
4. Onglet "Sécurité" → Ajouter "public" avec droits READ ONLY
```

#### Synology NAS
```
1. Panneau de configuration → Terminal & SNMP
2. Activer le service SNMP
3. Nom de communauté : public
```

#### QNAP NAS
```
1. Panneau de configuration → Réseau & Fichier Services → SNMP
2. Activer SNMP
3. Communauté : public
```

## Test des OIDs

Utilisez l'utilitaire `snmpwalk` pour tester les OIDs :

```bash
# Lister toutes les interfaces
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.2.2.1.2

# Tester un OID spécifique (interface 2)
snmpget -v2c -c public 192.168.1.100 1.3.6.1.2.1.31.1.1.1.6.2
```

## Références

- [RFC 2863 - IF-MIB](https://datatracker.ietf.org/doc/html/rfc2863)
- [Net-SNMP Documentation](http://net-snmp.sourceforge.net/)
- [SNMP Wikipedia](https://fr.wikipedia.org/wiki/Simple_Network_Management_Protocol)
