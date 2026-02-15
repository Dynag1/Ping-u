
import requests
import subprocess
import time
import sys
import os
import signal

BASE_URL = "http://localhost:9090"
LOGIN_URL = f"{BASE_URL}/api/login"
HOSTS_URL = f"{BASE_URL}/api/hosts"
# L'ajout se fait souvent via POST /api/add_hosts dans scan_routes
ADD_URL = f"{BASE_URL}/api/add_hosts"

USERNAME = "admin"
PASSWORD = "a" # Default
# Mais on l'a reset à admin123
PASSWORD_RESET = "admin123"

def check_server_up(timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(BASE_URL, timeout=2)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            print(".", end="", flush=True)
    return False

def run_test():
    print("--- Démarrage des tests Headless Pingu ---")
    
    # 1. STOP existing instance
    print("🛑 Arrêt instance existante...")
    subprocess.run([sys.executable, "Pingu.py", "--stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    # 2. START headless
    print("🚀 Démarrage Pingu headless...")
    # On lance en background
    # Rediriger stdout/stderr vers un fichier pour debug
    proc = subprocess.Popen([sys.executable, "Pingu.py", "--start"], 
                           stdout=open("logs/headless_out.log", "w"), 
                           stderr=subprocess.STDOUT)
    
    print("⏳ Attente du serveur (max 30s)...", end="")
    if not check_server_up():
        print("\n❌ Le serveur n'a pas démarré !")
        # cat_log()
        stop_server()
        sys.exit(1)
    print("\n✅ Serveur accessible !")

    session = requests.Session()

    # 3. LOGIN
    print(f"🔑 Tentative de login ({USERNAME})...")
    # Essayer le mdp par défaut 'a' puis 'admin123'
    logged_in = False
    for pwd in [PASSWORD, PASSWORD_RESET]:
        try:
            # API login expects JSON
            resp = session.post(LOGIN_URL, json={"username": USERNAME, "password": pwd}, allow_redirects=False)
            
            if resp.status_code == 200 and resp.json().get('success'):
                print(f"✅ Login réussi avec mot de passe: {pwd}")
                logged_in = True
                break
        except Exception as e:
            print(f"❌ Erreur login: {e}")
    
    if not logged_in:
        print("❌ Login échoué avec tous les mots de passe.")
        stop_server()
        sys.exit(1)

    # 4. LIST HOSTS (Initial)
    print("📋 Récupération liste initiale...")
    try:
        resp = session.get(HOSTS_URL)
        hosts = resp.json()
        print(f"   Hosts trouvés: {len(hosts)}")
        initial_count = len(hosts)
    except Exception as e:
         print(f"❌ Erreur récupération hôtes: {e}")
         initial_count = 0

    # 5. ADD HOST (8.8.8.8)
    test_ip = "8.8.8.8"
    print(f"➕ Ajout hôte de test: {test_ip}...")
    try:
        payload = {
            "ip": test_ip,
            "hosts": 1, 
            "port": "80", 
            "scan_type": "alive", # Doit être lowercase pour correspondre à scan_routes
            "site": "TestSite"
        }
        resp = session.post(ADD_URL, json=payload)
        if resp.status_code == 200 and resp.json().get('success'):
            print("✅ Commande ajout envoyée.")
        else:
            print(f"❌ Echec commande ajout: {resp.text}")
    except Exception as e:
        print(f"❌ Exception ajout: {e}")

    # 6. WAIT & VERIFY
    print("⏳ Attente du scan (10s)...")
    time.sleep(10)
    
    print("📋 Vérification liste finale...")
    found = False
    try:
        resp = session.get(HOSTS_URL)
        hosts = resp.json()
        print(f"   Hosts trouvés: {len(hosts)}")
        
        for h in hosts:
            if h.get('ip') == test_ip:
                print(f"✅ Hôte {test_ip} TROUVÉ dans la liste ! (Status: {h.get('status', 'N/A')})")
                found = True
                break
        
        if not found:
            print(f"❌ Hôte {test_ip} NON trouvé après 10s.")
            print("   Liste actuelle:", [h.get('ip') for h in hosts])
    except Exception as e:
         print(f"❌ Erreur récupération hôtes finale: {e}")

    # 7. CLEANUP
    stop_server()
    
    if found:
        print("\n🎉 TOUS LES TESTS PASSÉS AVEC SUCCÈS")
        sys.exit(0)
    else:
        print("\n💥 ECHEC DU TEST D'AJOUT")
        sys.exit(1)

def stop_server():
    print("🛑 Arrêt du serveur...")
    subprocess.run([sys.executable, "Pingu.py", "--stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def cat_log():
    try:
        with open("logs/headless_out.log", "r") as f:
            print(f.read())
    except:
        pass

if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        stop_server()
