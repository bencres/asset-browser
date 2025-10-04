from frontend.MainWindow import MainWindow
from backend.DataController import DataController

class Presenter:
    def __init__(self, win: MainWindow, dc: DataController):
        self.win = win
        self.dc = dc
        app = self._detect_application()
        self.adapter = self.setAdapter(app)

    def run(self):
        self.win.show()

    def _detect_application(self):
        pass

    def setAdapter(self, app):
        pass

    def loadAssets(self):
        pass

