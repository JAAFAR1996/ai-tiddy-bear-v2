"""Plugin Architecture for AI Teddy Bear

This module provides a secure plugin system for extending functionality
while maintaining child safety and security compliance.
"""

import importlib
import inspect
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Type


class PluginType(Enum):
    """Types of plugins supported by the system"""
    AI_SERVICE = "AI_SERVICE"
    CUSTOM = "CUSTOM"
    AUDIO_PROCESSOR = "AUDIO_PROCESSOR"
    LANGUAGE_PROCESSOR = "LANGUAGE_PROCESSOR"
    SECURITY_VALIDATOR = "SECURITY_VALIDATOR"


class PluginStatus(Enum):
    """Plugin status states"""
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"
    DISABLED = "DISABLED"


@dataclass
class PluginManifest:
    """Plugin manifest containing metadata"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    entry_point: str
    dependencies: List[str] = None
    min_python_version: str = "3.8"
    child_safe: bool = True
    security_validated: bool = False

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class PluginInterface(ABC):
    """Base interface that all plugins must implement"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration"""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the plugin's main functionality"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources when plugin is disabled"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Get plugin version"""
        pass


class PluginValidationError(Exception):
    """Exception raised when plugin validation fails"""
    pass


class PluginSecurityError(Exception):
    """Exception raised when plugin security check fails"""
    pass


class PluginValidator:
    """Validates plugins for security and child safety compliance"""
    
    FORBIDDEN_IMPORTS = {
        'subprocess', 'os.system', 'eval', 'exec', 'compile',
        'socket', 'urllib', 'requests', 'http', 'ftplib',
        '__import__', 'importlib.import_module'
    }
    
    FORBIDDEN_KEYWORDS = {
        'subprocess', 'system', 'popen', 'shell',
        'network', 'internet', 'download', 'upload'
    }
    
    def validate_plugin(self, plugin_path: Path) -> bool:
        """Validate plugin for security and compliance"""
        try:
            # Check file extension
            if not plugin_path.suffix == '.py':
                raise PluginValidationError("Plugin must be a Python file")
            
            # Read and analyze source code
            with open(plugin_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Check for forbidden imports and keywords
            if self._contains_forbidden_content(source_code):
                raise PluginSecurityError("Plugin contains forbidden functionality")
            
            # Validate syntax
            try:
                compile(source_code, plugin_path, 'exec')
            except SyntaxError as e:
                raise PluginValidationError(f"Plugin syntax error: {e}")
            
            return True
            
        except Exception as e:
            raise PluginValidationError(f"Plugin validation failed: {e}")
    
    def _contains_forbidden_content(self, source_code: str) -> bool:
        """Check if source code contains forbidden functionality"""
        source_lower = source_code.lower()
        
        # Check for forbidden imports
        for forbidden in self.FORBIDDEN_IMPORTS:
            if f"import {forbidden}" in source_lower or f"from {forbidden}" in source_lower:
                return True
        
        # Check for forbidden keywords
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in source_lower:
                return True
        
        return False


class PluginManager:
    """Manages plugin loading, validation, and execution"""
    
    def __init__(self, plugins_dir: str = "./plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self.validator = PluginValidator()
        
        # Ensure plugins directory exists
        self.plugins_dir.mkdir(exist_ok=True)
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name"""
        try:
            plugin_path = self.plugins_dir / f"{plugin_name}.py"
            manifest_path = self.plugins_dir / f"{plugin_name}_manifest.json"
            
            if not plugin_path.exists():
                raise FileNotFoundError(f"Plugin file not found: {plugin_path}")
            
            # Validate plugin security
            if not self.validator.validate_plugin(plugin_path):
                raise PluginSecurityError(f"Plugin {plugin_name} failed security validation")
            
            # Load manifest if exists
            manifest = self._load_manifest(manifest_path)
            
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load plugin spec: {plugin_name}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class that implements PluginInterface
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                raise PluginValidationError("No valid plugin class found")
            
            # Create plugin instance
            plugin_instance = plugin_class()
            
            # Store plugin information
            self.plugins[plugin_name] = {
                'instance': plugin_instance,
                'manifest': manifest,
                'status': PluginStatus.INACTIVE,
                'module': module
            }
            
            return True
            
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def activate_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """Activate a loaded plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin_info = self.plugins[plugin_name]
            plugin_instance = plugin_info['instance']
            
            # Initialize plugin
            if plugin_instance.initialize(config or {}):
                plugin_info['status'] = PluginStatus.ACTIVE
                return True
            else:
                plugin_info['status'] = PluginStatus.ERROR
                return False
                
        except Exception as e:
            print(f"Failed to activate plugin {plugin_name}: {e}")
            self.plugins[plugin_name]['status'] = PluginStatus.ERROR
            return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin_info = self.plugins[plugin_name]
            plugin_instance = plugin_info['instance']
            
            plugin_instance.cleanup()
            plugin_info['status'] = PluginStatus.INACTIVE
            return True
            
        except Exception as e:
            print(f"Failed to deactivate plugin {plugin_name}: {e}")
            return False
    
    def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """Execute a plugin's main functionality"""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin {plugin_name} not found")
        
        plugin_info = self.plugins[plugin_name]
        if plugin_info['status'] != PluginStatus.ACTIVE:
            raise RuntimeError(f"Plugin {plugin_name} is not active")
        
        return plugin_info['instance'].execute(*args, **kwargs)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins with their status"""
        return [
            {
                'name': name,
                'status': info['status'].value,
                'manifest': info['manifest'].__dict__ if info['manifest'] else None
            }
            for name, info in self.plugins.items()
        ]
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[str]:
        """Get plugins of a specific type"""
        return [
            name for name, info in self.plugins.items()
            if info['manifest'] and info['manifest'].plugin_type == plugin_type
        ]
    
    def _load_manifest(self, manifest_path: Path) -> Optional[PluginManifest]:
        """Load plugin manifest from JSON file"""
        if not manifest_path.exists():
            return None
        
        try:
            import json
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return PluginManifest(
                name=data['name'],
                version=data['version'],
                description=data['description'],
                author=data['author'],
                plugin_type=PluginType(data['plugin_type']),
                entry_point=data['entry_point'],
                dependencies=data.get('dependencies', []),
                min_python_version=data.get('min_python_version', '3.8'),
                child_safe=data.get('child_safe', True),
                security_validated=data.get('security_validated', False)
            )
        except Exception as e:
            print(f"Failed to load manifest {manifest_path}: {e}")
            return None
    
    def _find_plugin_class(self, module) -> Optional[Type[PluginInterface]]:
        """Find the main plugin class in a module"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (obj != PluginInterface and 
                issubclass(obj, PluginInterface) and 
                obj.__module__ == module.__name__):
                return obj
        return None


def create_plugin_manager(path: str = "./plugins") -> PluginManager:
    """Create a new plugin manager instance"""
    return PluginManager(path)


def create_plugin_manifest(
    name: str,
    version: str,
    description: str,
    author: str,
    plugin_type: PluginType,
    entry_point: str,
    **kwargs
) -> PluginManifest:
    """Create a new plugin manifest"""
    return PluginManifest(
        name=name,
        version=version,
        description=description,
        author=author,
        plugin_type=plugin_type,
        entry_point=entry_point,
        **kwargs
    )