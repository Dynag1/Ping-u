# 🔧 Correction SNMP sur Raspberry Pi

## 📋 Problème

Le SNMP ne fonctionne pas sur Raspberry Pi en mode headless car les bibliothèques `pysnmp` nécessitent des dépendances supplémentaires.

---

## ✅ Solutions

### Solution 1 : Installer les dépendances SNMP (recommandé)

```bash
cd ~/ping-u

# Installer les dépendances SNMP
pip3 install --upgrade pysnmp pyasn1 pyasn1-modules pycryptodomex

# Redémarrer l'application
./stop_headless.sh
./start_headless.sh
```

### Solution 2 : Vérifier les versions

Si le problème persiste, vérifiez les versions :

```bash
pip3 list | grep -i snmp
pip3 list | grep -i asn1
```

**Versions recommandées** :
- `pysnmp` >= 6.0.0
- `pyasn1` >= 0.4.8, < 0.6.1
- `pyasn1-modules` >= 0.2.8
- `pycryptodomex` >= 3.15.0

### Solution 3 : Réinstaller complètement

```bash
cd ~/ping-u

# Désinstaller les anciennes versions
pip3 uninstall -y pysnmp pyasn1 pyasn1-modules pycryptodomex

# Réinstaller avec les bonnes versions
pip3 install pysnmp==6.0.0 pyasn1==0.5.1 pyasn1-modules==0.3.0 pycryptodomex==3.18.0

# Redémarrer
./stop_headless.sh
./start_headless.sh
```

---

## 🧪 Test SNMP

Pour tester si SNMP fonctionne :

```bash
cd ~/ping-u
python3 -c "
from src.utils.snmp_helper import snmp_helper
import asyncio

async def test():
    # Testez avec l'IP d'un équipement qui supporte SNMP
    temp = await snmp_helper.get_temperature('192.168.2.1')
    print(f'Température: {temp}')

asyncio.run(test())
"
```

---

## 🔍 Diagnostic des erreurs

### Erreur : "No module named 'pysnmp'"

```bash
pip3 install pysnmp
```

### Erreur : "module 'pyasn1' has no attribute 'v1'"

```bash
pip3 install --upgrade pyasn1==0.5.1
```

### Erreur : "ImportError: cannot import name 'DES' from 'Crypto.Cipher'"

```bash
pip3 uninstall pycrypto pycryptodome
pip3 install pycryptodomex
```

---

## 📝 Vérifier les logs

```bash
# Voir les erreurs SNMP dans les logs
tail -f ~/ping-u/logs/app.log | grep -i snmp

# Ou dans le log headless
tail -f ~/ping-u/pingu_headless.log | grep -i snmp
```

---

## ⚙️ Configuration SNMP des équipements

Pour que SNMP fonctionne, vos équipements (routeurs, switches, NAS, etc.) doivent :

1. **Avoir SNMP activé** (version 2c ou 3)
2. **Community string** : généralement `public` (lecture seule)
3. **Port SNMP** : 161 (UDP)

### Exemple : Activer SNMP sur un routeur

**Linux/NAS Synology** :
- Panneau de configuration → Terminal & SNMP → Onglet SNMP
- Cocher "Activer le service SNMP"
- SNMPv1, SNMPv2c : `public`

**Routeur** :
- Interface web → Administration → SNMP
- Activer SNMP v2c
- Community: `public`

---

## 🎯 Test de disponibilité SNMP

```bash
# Installer snmpwalk (si pas déjà installé)
sudo apt install snmp snmp-mibs-downloader

# Tester un équipement
snmpwalk -v2c -c public 192.168.2.1 system

# Tester la température (exemple pour Synology)
snmpwalk -v2c -c public 192.168.2.1 1.3.6.1.4.1.6574.1.2.0
```

---

## ❌ Désactiver SNMP (si vous ne l'utilisez pas)

Si vous ne souhaitez pas utiliser SNMP, vous pouvez le désactiver :

Le système fonctionnera normalement sans SNMP, mais vous n'aurez pas :
- La température des équipements
- Les débits réseau en temps réel

Le monitoring de base (ping, disponibilité) continuera de fonctionner.

---

## 📞 Support

Si le SNMP ne fonctionne toujours pas après avoir suivi ces étapes :

1. Vérifiez les logs : `tail -100 logs/app.log | grep -i snmp`
2. Vérifiez que l'équipement cible supporte SNMP
3. Testez avec `snmpwalk` pour confirmer la connectivité SNMP

---

**Note** : Le SNMP est optionnel. L'application fonctionne parfaitement sans, vous aurez simplement pas accès aux informations de température et débit réseau.

