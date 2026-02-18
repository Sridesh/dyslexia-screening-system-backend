import sys
import os
from datetime import datetime

sys.path.append(os.getcwd())

print("Importing engine...")
from app.adaptive_testing_module import orchestration_engine, config
print("Engine imported.")

try:
    print("Making items...")
    from app.simulations.simulate_ef_ads import make_synthetic_item_bank
    items, mod_ids = make_synthetic_item_bank()
    print(f"Items made: {len(items)}")

    print("Starting test...")
    res = orchestration_engine.start_new_test(1, mod_ids, items, datetime.utcnow())
    print("Test started.")
    print(f"First item: {res.first_item.id if res.first_item else 'None'}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Minimal test done.")
