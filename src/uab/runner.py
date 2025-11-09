import subprocess
import os
import sys
import requests
import time
from PySide6.QtWidgets import QApplication

from uab.frontend.main_widget import MainWidget
from uab.frontend.main_window import MainWindow


def run():
    process = start_server()
    try:
        result = start_gui()
        return result
    finally:
        print("Shutting down server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Server shut down.")


def start_server():
    """Start the uvicorn FastAPI server and return the process handle."""
    SERVER_URL = "http://127.0.0.1:8000"
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

    if not os.path.exists(BACKEND_DIR):
        raise RuntimeError(f"Backend directory missing: {BACKEND_DIR}")

    uvicorn_cmd = [sys.executable, "-m", "uvicorn", "server:app", "--reload"]

    print("Starting server...")
    process = subprocess.Popen(
        uvicorn_cmd,
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if not _wait_for_server(SERVER_URL + "/assets", timeout=10):
        process.terminate()
        raise RuntimeError("Server failed to start in time.")

    print("Server started and reachable.")
    return process


def start_gui():
    """Launch the GUI appropriately depending on environment."""
    print("Starting GUI...")
    match _get_current_dcc():
        case "hou":
            return MainWidget()
        case _:
            pass
    app = QApplication(sys.argv)
    win = MainWindow(MainWidget())
    win.show()
    exit_code = app.exec()
    return exit_code


def _get_current_dcc():
    try:
        import hou
        return "hou"
    except ImportError:
        return None


def _wait_for_server(url, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code < 500:
                return True
        except Exception:
            time.sleep(0.25)
    return False
