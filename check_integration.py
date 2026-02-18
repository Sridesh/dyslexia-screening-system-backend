import sys
import os

print("Starting debug...")
sys.path.append(os.getcwd())

try:
    print("Importing config...")
    from app.core import config
    print("Config imported.")

    print("Importing database...")
    from app.db import database
    print("Database imported.")
    
    print("Importing adaptive module...")
    from app.adaptive_testing_module import orchestration_engine
    print("Adaptive module imported.")

    print("Importing main app...")
    from app.main import app
    print("Main app imported.")
    
    print("Checking routes...")
    adaptive_route_found = False
    for route in app.routes:
        if route.path.startswith("/api/v1/adaptive"):
            adaptive_route_found = True
            break
            
    if adaptive_route_found:
        print("SUCCESS: Adaptive route found.")
    else:
        print("FAILURE: Adaptive route NOT found.")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
