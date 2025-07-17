from enum import Enum


class PluginType(Enum):
    AI_SERVICE = "AI_SERVICE"
    CUSTOM = "CUSTOM"


def create_plugin_manager(path) -> PluginManager:
    pass


def create_plugin_manifest(
    name,
    version,
    description,
    author,
    plugin_type,
    entry_point,
):
    pass
