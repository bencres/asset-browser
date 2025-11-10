from uab.core.base_presenter import Presenter


class DesktopPresenter(Presenter):
    def __init__(self, view):
        super().__init__(view)

    def spawn_asset(self, asset: dict):
        self.widget.show_message(
            f"Spawning asset on desktop is not supported.", "info", 3000)
