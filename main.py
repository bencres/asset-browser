"""
Starts the server and opens the gui.
"""
import subprocess
import os
import sys

from PySide6.QtWidgets import (
    QApplication
)

from core.presenter import Presenter
from backend.asset_service import AssetService
from frontend.window import Window

SERVER_URL = "http://127.0.0.1:8000"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
# WARNING: this is specific to my machine for testing purposes.
# TODO: implement user selection of local assets directory.
LOCAL_ASSETS_DIR = "/Users/dev/Assets"

UVICORN_COMMAND = ["uvicorn", "server:app", "--reload"]

uvicorn_process = None
exit_code = None

try:
    print("Starting FastAPI server...")
    uvicorn_process = subprocess.Popen(
        UVICORN_COMMAND,
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # Server needs a sec to start
    import time
    time.sleep(1)
    print("FastAPI server process started. Continuing with GUI launch.")

    app = QApplication(sys.argv)
    model = AssetService(SERVER_URL, LOCAL_ASSETS_DIR)
    view = Window()
    presenter = Presenter(view, model)
    presenter.run()
    exit_code = app.exec()

except Exception as e:
    print(f"An error occurred during application launch: {e}", file=sys.stderr)
finally:
    if uvicorn_process and uvicorn_process.poll() is None:
        print("Terminating FastAPI server process...")
        uvicorn_process.terminate()
        uvicorn_process.wait(timeout=5)
        if uvicorn_process.poll() is None:
            uvicorn_process.kill()
        print("FastAPI server process terminated.")

    if exit_code:
        sys.exit(exit_code)
    else:
        sys.exit()
