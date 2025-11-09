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

# Global server reference
_server_instance = None
_server_thread = None


def run():
    is_houdini = _get_current_dcc() == "hou"
    
    server = _start_server()
    
    if is_houdini:
        # In Houdini, keep the server running and return the widget
        global _server_instance
        _server_instance = server
        result = _start_gui()
        return result
    else:
        # In desktop mode, clean up server when GUI closes
        try:
            result = _start_gui()
            return result
        finally:
            print("Shutting down server...")
            _stop_server(server)
            print("Server shut down.")


def _start_server():
    """Start the uvicorn FastAPI server in a background thread."""
    global _server_thread

    print(app.title)
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, reload=False)
    server = uvicorn.Server(config)

    def _run_server():
        print("Starting server thread...")
        server.run()
        print("Server stopped.")

    is_houdini = _get_current_dcc() == "hou"
    thread = threading.Thread(target=_run_server, daemon=(not is_houdini))
    thread.start()
    _server_thread = thread

    SERVER_URL = "http://127.0.0.1:8000"
    if not _wait_for_server(SERVER_URL, timeout=10):
        raise RuntimeError("Server failed to start in time.")

    print("Server started and reachable.")
    return server


def _stop_server(server):
    """Gracefully stop the server."""
    try:
        server.should_exit = True
    except Exception:
        pass  # Uvicorn server may already be down


def shutdown_server():
    """Manually shut down the server if needed."""
    global _server_instance
    if _server_instance:
        print("Shutting down server...")
        _stop_server(_server_instance)
        _server_instance = None
        print("Server shut down.")


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
    """Determine which environment the UAB is being run from."""
    try:
        import hou
        return "hou"
    except ImportError:
        return None


def _wait_for_server(url, timeout=5, tick=0.25):
    """Wait for the server to respond, ensuring that it's running."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code < 500:
                return True
        except Exception:
            time.sleep(tick)
    return False
