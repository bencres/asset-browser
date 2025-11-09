import subprocess
import os
import sys
import requests
import time
import threading
import uvicorn
from PySide6.QtWidgets import QApplication

from uab.frontend.main_widget import MainWidget
from uab.frontend.main_window import MainWindow
from uab.backend.server import app


def run():
    process = _start_server()
    try:
        result = _start_gui()
        return result
    finally:
        print("Shutting down server...")
        _stop_server(process)
        print("Server shut down.")


def _start_server():
    """Start the uvicorn FastAPI server in a background thread."""
    print(app.title)
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, reload=False)
    server = uvicorn.Server(config)

    def _run_server():
        print("Starting server thread...")
        server.run()
        print("Server stopped.")

    thread = threading.Thread(target=_run_server, daemon=True)
    thread.start()

    # Wait until server is reachable before continuing
    server_url = "http://127.0.0.1:8000"
    if not _wait_for_server(server_url, timeout=10):
        raise RuntimeError("Server failed to start in time.")

    print("Server started and reachable.")
    return server


def _stop_server(server):
    """Gracefully stop the server."""
    try:
        server.should_exit = True
    except Exception:
        pass  # Uvicorn server may already be down


def _start_gui():
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