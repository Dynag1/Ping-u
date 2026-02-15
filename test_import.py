import sys
import os
sys.path.append(os.getcwd())

try:
    from src.utils.headless_compat import QSortFilterProxyModel, AppColors
    print("Success: QSortFilterProxyModel and AppColors imported")
except Exception as e:
    print(f"Error: {e}")
