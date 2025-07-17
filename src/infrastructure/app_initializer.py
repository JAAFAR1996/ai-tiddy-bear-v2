from src.infrastructure.config.settings import get_settings
from src.infrastructure.di.container import Container
from src.infrastructure.di.di_components.wiring_config import FullWiringConfig
from src.infrastructure.logging_config import get_logger


class AppInitializer:
    def __init__(self):
        self._settings = None
        self._container = None
        self._logger = None

    def get_settings(self):
        if self._settings is None:
            self._settings = get_settings()
        return self._settings

    def get_container(self):
        if self._container is None:
            self._container = Container()
        return self._container

    def wire_container(self, app_container: Container):
        app_container.wire(modules=FullWiringConfig.modules)

    def get_logger(self, name: str, component: str):
        if self._logger is None:
            self._logger = get_logger(name, component)
        return self._logger
