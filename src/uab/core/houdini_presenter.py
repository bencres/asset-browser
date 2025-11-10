# Ignore failed import on desktop
try:
    import hou
except ImportError:
    pass
from uab.core.base_presenter import Presenter


class HoudiniPresenter(Presenter):
    def __init__(self, view):
        super().__init__(view)

    def spawn_asset(self, asset: dict):
        pass
