# Correction des erreurs sur Raspberry Pi

## Problème 1: "Operation not permitted" lors des pings

### Solution A: Autoriser les pings sans privilèges root (RECOMMANDÉ)

```bash
# Méthode 1: Configurer les paramètres système
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"

# Pour rendre permanent, ajouter dans /etc/sysctl.conf:
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
```

### Solution B: Utiliser les capacités Linux

```bash
# Donner la capacité CAP_NET_RAW au binaire Python
sudo setcap cap_net_raw+ep $(which python3)

# Si vous utilisez pyenv (comme dans votre cas):
sudo setcap cap_net_raw+ep /home/dynag/.pyenv/versions/3.13.5/bin/python3.13
```

### Solution C: Lancer avec sudo (moins recommandé)

```bash
sudo python3 Pingu.py --headless
```

## Problème 2: "write() before start_response" (Flask)

Ce problème est causé par une route Flask qui ne retourne pas correctement une réponse.
Le code doit être corrigé dans `src/web_server.py`.

## Problème 3: Fichiers manquants (tab, tabG)

Ces fichiers de configuration seront créés automatiquement au premier lancement avec interface graphique,
ou peuvent être créés manuellement.

### Créer les fichiers de base:

```bash
cd ~/ping-u
python3 -c "
import pickle

# Créer tab (paramètres mail)
with open('tab', 'wb') as f:
    pickle.dump(['', '', '', ''], f)

# Créer tabG (paramètres généraux)
with open('tabG', 'wb') as f:
    pickle.dump(['MonSite', 'fr', 'light'], f)

# Créer tab4 (autres paramètres)
with open('tab4', 'wb') as f:
    pickle.dump([10, 3, False, False, False, False, False], f)

print('Fichiers de configuration créés avec succès!')
"
```

## Vérifications après corrections

1. Vérifier les permissions ping:
```bash
ping -c 1 8.8.8.8
```

2. Relancer l'application:
```bash
cd ~/ping-u
./start_headless.sh
```

3. Vérifier les logs:
```bash
tail -f pingu_headless.log
```

## Test rapide

```bash
# Appliquer la solution A
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"

# Créer les fichiers de config
cd ~/ping-u
python3 -c "import pickle; pickle.dump(['', '', '', ''], open('tab', 'wb')); pickle.dump(['MonSite', 'fr', 'light'], open('tabG', 'wb')); pickle.dump([10, 3, False, False, False, False, False], open('tab4', 'wb'))"

# Relancer
./stop_headless.sh
./start_headless.sh
```

