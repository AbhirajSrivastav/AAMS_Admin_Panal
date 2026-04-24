import sys
import traceback
import os

# Suppress TF logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

print("=== Diagnostic Start ===")
print("Python:", sys.executable)
print("CWD:", os.getcwd())

try:
    print("Step 1: Importing database...")
    from database import DatabaseManager
    print("Step 1: OK")

    print("Step 2: Creating DB...")
    db = DatabaseManager()
    print("Step 2: OK -", len(db.get_all_students()), "students")

    print("Step 3: Importing Flask...")
    from flask import Flask
    print("Step 3: OK")

    print("Step 4: Importing cv2...")
    import cv2
    print("Step 4: OK")

    print("Step 5: Importing RetinaFace...")
    from retinaface import RetinaFace
    print("Step 5: OK")

    print("Step 6: Importing app module...")
    import importlib
    import app as app_module
    print("Step 6: OK - Flask app:", app_module.app)

    print("Step 7: Testing API route registration...")
    rules = [str(r) for r in app_module.app.url_map.iter_rules()]
    print("Routes:", rules)
    print("Step 7: OK")

    print("=== ALL CHECKS PASSED ===")

except Exception as e:
    print("=== ERROR ===")
    traceback.print_exc()
    sys.exit(1)

