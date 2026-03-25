import sys
import os

print("Checking paths...")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
print(f"Path: {sys.path[-1]}")

try:
    from app.adaptive_testing_module import config
    print(f"Config imported. Module count: {len(config.MODULES)}")
except Exception as e:
    print(f"Import failed: {e}")

print("Success!")
