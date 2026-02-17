
import sys
import os
import json
from src import lic, secure_config
from src.utils.logger import get_logger

logger = get_logger(__name__)

print("--- Check License ---")
try:
    is_active = lic.verify_license()
    print(f"Is Active: {is_active}")
except Exception as e:
    print(f"Error verifies license: {e}")

print("\n--- Check Activation Code ---")
try:
    activation_code = lic.generate_activation_code()
    print(f"Activation Code: {activation_code}")
except Exception as e:
    print(f"Error generate activation code: {e}")

print("\n--- Check Secure Config (Telegram) ---")
try:
    token = secure_config.get_telegram_token()
    print(f"Telegram Token: {token[:5]}..." if token else "Telegram Token: None")
except Exception as e:
    print(f"Error secure config: {e}")
