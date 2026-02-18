import sys
import os
import traceback

log_file = "debug_log.txt"

def log(msg):
    with open(log_file, "a") as f:
        f.write(msg + "\n")

log("Starting debug script...")
log(f"CWD: {os.getcwd()}")
log(f"Path: {sys.path}")

try:
    log("Attempting import app.simulations.sim_core...")
    sys.path.append(os.getcwd())
    import app.simulations.sim_core
    log("Import successful.")
except Exception as e:
    log(f"Import failed: {e}")
    log(traceback.format_exc())

log("Done.")
