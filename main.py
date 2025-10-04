"""
Starts the server and opens the gui.
"""
import subprocess
import os
import sys

from PySide6.QtWidgets import (
    QApplication
)

from core.Presenter import Presenter
from frontend.MainWindow import MainWindow
from backend.DataController import DataController

SERVER_URL = "http://127.0.0.1:8000"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

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
    data_controller_model = DataController(SERVER_URL)
    main_window_view = MainWindow()
    presenter = Presenter(main_window_view, data_controller_model)
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
