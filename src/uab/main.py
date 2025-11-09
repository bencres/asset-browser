"""
Starts the server and opens the gui.
"""
import subprocess
import os
import sys
import requests
import time

from PySide6.QtWidgets import (
    QApplication
)

from uab.core.presenter import Presenter
from uab.backend.asset_service import AssetService

SERVER_URL = "http://127.0.0.1:8000"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if not os.path.exists(BACKEND_DIR):
    raise RuntimeError(f"Backend directory does not exist! {BACKEND_DIR}")
# WARNING: this is specific to my machine for testing purposes.
# TODO: implement user selection of local assets directory.
LOCAL_ASSETS_DIR = "/Users/dev/Assets"

UVICORN_COMMAND = ["uvicorn", "server:app", "--reload"]

def wait_for_server(url, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code < 500:
                return True
        except Exception:
            time.sleep(0.25)
    return False

uvicorn_process = None
exit_code = None

try:
    print("Starting server...")
    uvicorn_process = subprocess.Popen(
        UVICORN_COMMAND,
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if not wait_for_server(SERVER_URL + "/assets"):
        raise RuntimeError("Server failed to start.")
    print("Server process started. Continuing with GUI launch...")
    

    app = QApplication(sys.argv)
    model = AssetService(SERVER_URL, LOCAL_ASSETS_DIR)
    presenter = Presenter(model)
    print("GUI launched.")
    exit_code = app.exec()

except Exception as e:
    print(f"An error occurred during application launch: {e}", file=sys.stderr)
finally:
    if uvicorn_process and uvicorn_process.poll() is None:
        print("Terminating server process...")
        uvicorn_process.terminate()
        uvicorn_process.wait(timeout=5)
        if uvicorn_process.poll() is None:
            uvicorn_process.kill()
        print("Server process terminated.")

    if exit_code:
        sys.exit(exit_code)
    else:
        sys.exit()
