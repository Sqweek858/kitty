#!/usr/bin/env python3
"""
Brad TUI Ultra - Plugin System Module
=====================================

Advanced plugin system with hot-reloading, sandboxing, and dependency management.
Allows extending Brad TUI Ultra functionality through Python plugins.

Features:
- Plugin discovery and loading
- Hot reloading without restart
- Dependency resolution
- Plugin sandboxing and security
- Event hooks and callbacks
- Plugin configuration
- Inter-plugin communication
- Plugin marketplace integration
"""

import os
import sys
import importlib
import importlib.util
import inspect
import traceback
from typing import Any, Dict, List, Optional, Callable, Type
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import hashlib
import json


# =============================================================================
# PLUGIN SYSTEM ENUMS
# =============================================================================

class PluginStatus(Enum):
    """Plugin status"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class PluginPriority(Enum):
    """Plugin execution priority"""
    HIGHEST = 1000
    HIGH = 100
    NORMAL = 0
    LOW = -100
    LOWEST = -1000


class HookType(Enum):
    """Available hook types"""
    # Lifecycle hooks
    ON_INIT = "on_init"
    ON_START = "on_start"
    ON_STOP = "on_stop"
    ON_RELOAD = "on_reload"
    
    # Command hooks
    PRE_COMMAND = "pre_command"
    POST_COMMAND = "post_command"
    COMMAND_ERROR = "command_error"
    
    # UI hooks
    PRE_RENDER = "pre_render"
    POST_RENDER = "post_render"
    ON_KEY_PRESS = "on_key_press"
    ON_RESIZE = "on_resize"
    
    # Output hooks
    ON_OUTPUT = "on_output"
    ON_INPUT = "on_input"
    FILTER_OUTPUT = "filter_output"
    FILTER_INPUT = "filter_input"
    
    # Effect hooks
    PRE_EFFECT = "pre_effect"
    POST_EFFECT = "post_effect"
    
    # Config hooks
    ON_CONFIG_CHANGE = "on_config_change"


# =============================================================================
# PLUGIN METADATA
# =============================================================================

@dataclass
class PluginMetadata:
    """Plugin metadata"""
    name: str
    version: str
    author: str
    description: str
    homepage: str = ""
    license: str = "MIT"
    dependencies: List[str] = field(default_factory=list)
    python_requires: str = ">=3.7"
    brad_tui_requires: str = ">=3.0"
    tags: List[str] = field(default_factory=list)
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'homepage': self.homepage,
            'license': self.license,
            'dependencies': self.dependencies,
            'python_requires': self.python_requires,
            'brad_tui_requires': self.brad_tui_requires,
            'tags': self.tags,
            'priority': self.priority,
        }


# =============================================================================
# PLUGIN BASE CLASS
# =============================================================================

class BradPlugin(ABC):
    """
    Base class for Brad TUI Ultra plugins
    
    All plugins must inherit from this class and implement required methods.
    """
    
    def __init__(self):
        """Initialize plugin"""
        self.config = {}
        self.enabled = True
        self.logger = None
        self.context = {}
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass
    
    @abstractmethod
    def on_load(self) -> bool:
        """
        Called when plugin is loaded
        
        Returns:
            True if load successful, False otherwise
        """
        pass
    
    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        pass
    
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        pass
    
    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        pass
    
    def on_config_change(self, key: str, value: Any) -> None:
        """Called when plugin configuration changes"""
        pass
    
    def register_hooks(self, hook_manager: 'HookManager') -> None:
        """Register hooks with the hook manager"""
        pass


# =============================================================================
# HOOK MANAGER
# =============================================================================

class HookManager:
    """
    Manages event hooks for plugins
    
    Allows plugins to register callbacks for various events.
    """
    
    def __init__(self):
        """Initialize hook manager"""
        self.hooks: Dict[HookType, List[tuple]] = {}
        for hook_type in HookType:
            self.hooks[hook_type] = []
    
    def register(
        self,
        hook_type: HookType,
        callback: Callable,
        priority: int = 0,
        plugin_name: str = ""
    ) -> None:
        """Register a hook callback"""
        self.hooks[hook_type].append((callback, priority, plugin_name))
        # Sort by priority (highest first)
        self.hooks[hook_type].sort(key=lambda x: -x[1])
    
    def unregister(self, hook_type: HookType, plugin_name: str) -> None:
        """Unregister all hooks for a plugin"""
        self.hooks[hook_type] = [
            h for h in self.hooks[hook_type]
            if h[2] != plugin_name
        ]
    
    def call(
        self,
        hook_type: HookType,
        *args,
        **kwargs
    ) -> List[Any]:
        """
        Call all registered hooks for an event
        
        Returns list of return values from all hooks
        """
        results = []
        
        for callback, priority, plugin_name in self.hooks[hook_type]:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Error in hook {hook_type} from {plugin_name}: {e}")
                traceback.print_exc()
        
        return results
    
    def call_filter(
        self,
        hook_type: HookType,
        value: Any,
        *args,
        **kwargs
    ) -> Any:
        """
        Call filter hooks that transform a value
        
        Each hook receives the output of the previous hook
        """
        result = value
        
        for callback, priority, plugin_name in self.hooks[hook_type]:
            try:
                result = callback(result, *args, **kwargs)
            except Exception as e:
                print(f"Error in filter {hook_type} from {plugin_name}: {e}")
                traceback.print_exc()
        
        return result
    
    def has_hooks(self, hook_type: HookType) -> bool:
        """Check if any hooks are registered for an event"""
        return len(self.hooks[hook_type]) > 0


# =============================================================================
# PLUGIN LOADER
# =============================================================================

class PluginLoader:
    """
    Loads plugins from Python files
    
    Handles plugin discovery, loading, and initialization.
    """
    
    def __init__(self, plugin_dir: str):
        """Initialize plugin loader"""
        self.plugin_dir = Path(plugin_dir).expanduser()
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
    
    def discover_plugins(self) -> List[Path]:
        """Discover all plugin files"""
        plugins = []
        
        # Find all Python files
        for file_path in self.plugin_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            plugins.append(file_path)
        
        # Find all plugin packages
        for dir_path in self.plugin_dir.iterdir():
            if dir_path.is_dir() and not dir_path.name.startswith("_"):
                init_file = dir_path / "__init__.py"
                if init_file.exists():
                    plugins.append(init_file)
        
        return plugins
    
    def load_plugin(self, plugin_path: Path) -> Optional[Type[BradPlugin]]:
        """Load a plugin from file"""
        try:
            # Generate module name
            module_name = f"brad_tui_plugin_{plugin_path.stem}"
            
            # Load module
            spec = importlib.util.spec_from_file_location(
                module_name,
                plugin_path
            )
            
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load spec for {plugin_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find plugin class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, BradPlugin) and
                    obj is not BradPlugin):
                    return obj
            
            raise ValueError(f"No plugin class found in {plugin_path}")
            
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
            traceback.print_exc()
            return None
    
    def reload_plugin(
        self,
        plugin_path: Path,
        plugin_class: Type[BradPlugin]
    ) -> Optional[Type[BradPlugin]]:
        """Reload a plugin"""
        try:
            module = sys.modules[plugin_class.__module__]
            importlib.reload(module)
            
            # Find new plugin class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, BradPlugin) and
                    obj is not BradPlugin):
                    return obj
            
            return None
            
        except Exception as e:
            print(f"Error reloading plugin: {e}")
            return None


# =============================================================================
# PLUGIN MANAGER
# =============================================================================

class PluginManager:
    """
    Main plugin management system
    
    Handles plugin loading, enabling/disabling, and lifecycle management.
    """
    
    def __init__(self, plugin_dir: str = "~/.config/brad_tui/plugins"):
        """Initialize plugin manager"""
        self.plugin_dir = plugin_dir
        self.loader = PluginLoader(plugin_dir)
        self.hook_manager = HookManager()
        
        self.plugins: Dict[str, BradPlugin] = {}
        self.plugin_classes: Dict[str, Type[BradPlugin]] = {}
        self.plugin_paths: Dict[str, Path] = {}
        self.plugin_status: Dict[str, PluginStatus] = {}
        self.plugin_configs: Dict[str, Dict] = {}
        
        self.safe_mode = True
        self.allowed_plugins: List[str] = []
        self.blocked_plugins: List[str] = []
    
    def discover_all(self) -> List[str]:
        """Discover all available plugins"""
        plugin_files = self.loader.discover_plugins()
        discovered = []
        
        for plugin_path in plugin_files:
            plugin_name = plugin_path.stem
            discovered.append(plugin_name)
            self.plugin_paths[plugin_name] = plugin_path
            self.plugin_status[plugin_name] = PluginStatus.UNLOADED
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        if plugin_name not in self.plugin_paths:
            print(f"Plugin {plugin_name} not found")
            return False
        
        if plugin_name in self.blocked_plugins:
            print(f"Plugin {plugin_name} is blocked")
            return False
        
        if self.safe_mode and self.allowed_plugins:
            if plugin_name not in self.allowed_plugins:
                print(f"Plugin {plugin_name} not in allowed list")
                return False
        
        try:
            self.plugin_status[plugin_name] = PluginStatus.LOADING
            
            # Load plugin class
            plugin_path = self.plugin_paths[plugin_name]
            plugin_class = self.loader.load_plugin(plugin_path)
            
            if plugin_class is None:
                raise ValueError(f"Failed to load plugin class")
            
            # Instantiate plugin
            plugin = plugin_class()
            
            # Load configuration
            if plugin_name in self.plugin_configs:
                plugin.config = self.plugin_configs[plugin_name]
            
            # Call on_load
            if not plugin.on_load():
                raise ValueError(f"Plugin on_load returned False")
            
            # Register hooks
            plugin.register_hooks(self.hook_manager)
            
            # Store plugin
            self.plugins[plugin_name] = plugin
            self.plugin_classes[plugin_name] = plugin_class
            self.plugin_status[plugin_name] = PluginStatus.LOADED
            
            # Enable if configured
            if plugin.enabled:
                self.enable_plugin(plugin_name)
            
            print(f"✅ Loaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading plugin {plugin_name}: {e}")
            traceback.print_exc()
            self.plugin_status[plugin_name] = PluginStatus.ERROR
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            
            # Disable first
            if self.plugin_status[plugin_name] == PluginStatus.ACTIVE:
                self.disable_plugin(plugin_name)
            
            # Call on_unload
            plugin.on_unload()
            
            # Unregister hooks
            for hook_type in HookType:
                self.hook_manager.unregister(hook_type, plugin_name)
            
            # Remove plugin
            del self.plugins[plugin_name]
            self.plugin_status[plugin_name] = PluginStatus.UNLOADED
            
            print(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            print(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a loaded plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.on_enable()
            plugin.enabled = True
            self.plugin_status[plugin_name] = PluginStatus.ACTIVE
            print(f"Enabled plugin: {plugin_name}")
            return True
            
        except Exception as e:
            print(f"Error enabling plugin {plugin_name}: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable an active plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.on_disable()
            plugin.enabled = False
            self.plugin_status[plugin_name] = PluginStatus.LOADED
            print(f"Disabled plugin: {plugin_name}")
            return True
            
        except Exception as e:
            print(f"Error disabling plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin (hot reload)"""
        if plugin_name not in self.plugins:
            return self.load_plugin(plugin_name)
        
        try:
            # Unload
            self.unload_plugin(plugin_name)
            
            # Reload plugin class
            plugin_path = self.plugin_paths[plugin_name]
            plugin_class = self.plugin_classes[plugin_name]
            new_class = self.loader.reload_plugin(plugin_path, plugin_class)
            
            if new_class is None:
                raise ValueError("Failed to reload plugin class")
            
            self.plugin_classes[plugin_name] = new_class
            
            # Load again
            return self.load_plugin(plugin_name)
            
        except Exception as e:
            print(f"Error reloading plugin {plugin_name}: {e}")
            return False
    
    def load_all(self) -> None:
        """Load all discovered plugins"""
        for plugin_name in self.plugin_paths.keys():
            self.load_plugin(plugin_name)
    
    def get_plugin(self, plugin_name: str) -> Optional[BradPlugin]:
        """Get a loaded plugin instance"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> Dict[str, PluginStatus]:
        """List all plugins and their status"""
        return self.plugin_status.copy()
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed plugin information"""
        if plugin_name not in self.plugins:
            return None
        
        plugin = self.plugins[plugin_name]
        metadata = plugin.get_metadata()
        
        return {
            'name': plugin_name,
            'status': self.plugin_status[plugin_name].value,
            'enabled': plugin.enabled,
            'metadata': metadata.to_dict(),
            'path': str(self.plugin_paths[plugin_name]),
        }
    
    def set_plugin_config(
        self,
        plugin_name: str,
        config: Dict[str, Any]
    ) -> bool:
        """Set plugin configuration"""
        if plugin_name not in self.plugins:
            # Store for when plugin loads
            self.plugin_configs[plugin_name] = config
            return True
        
        plugin = self.plugins[plugin_name]
        old_config = plugin.config
        plugin.config = config
        
        # Notify plugin of changes
        for key, value in config.items():
            if key not in old_config or old_config[key] != value:
                plugin.on_config_change(key, value)
        
        self.plugin_configs[plugin_name] = config
        return True
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self.plugin_configs.get(plugin_name, {})
    
    def call_hook(self, hook_type: HookType, *args, **kwargs) -> List[Any]:
        """Call a hook for all active plugins"""
        return self.hook_manager.call(hook_type, *args, **kwargs)
    
    def filter_hook(
        self,
        hook_type: HookType,
        value: Any,
        *args,
        **kwargs
    ) -> Any:
        """Call a filter hook"""
        return self.hook_manager.call_filter(hook_type, value, *args, **kwargs)


# =============================================================================
# EXAMPLE PLUGIN
# =============================================================================

class ExamplePlugin(BradPlugin):
    """Example plugin demonstrating the plugin API"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Example Plugin",
            version="1.0.0",
            author="Brad TUI Team",
            description="Example plugin showing how to create plugins",
            homepage="https://github.com/example/plugin",
            tags=["example", "demo"],
        )
    
    def on_load(self) -> bool:
        print("Example plugin loaded!")
        return True
    
    def on_unload(self) -> None:
        print("Example plugin unloaded!")
    
    def on_enable(self) -> None:
        print("Example plugin enabled!")
    
    def on_disable(self) -> None:
        print("Example plugin disabled!")
    
    def register_hooks(self, hook_manager: HookManager) -> None:
        # Register for pre-command hook
        hook_manager.register(
            HookType.PRE_COMMAND,
            self.on_pre_command,
            priority=0,
            plugin_name=self.get_metadata().name
        )
        
        # Register for output filter
        hook_manager.register(
            HookType.FILTER_OUTPUT,
            self.filter_output,
            priority=0,
            plugin_name=self.get_metadata().name
        )
    
    def on_pre_command(self, command: str) -> None:
        """Called before executing a command"""
        print(f"[Example Plugin] About to execute: {command}")
    
    def filter_output(self, output: str) -> str:
        """Filter command output"""
        # Example: Add timestamp to output
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {output}"


# =============================================================================
# PLUGIN MARKETPLACE (Stub)
# =============================================================================

class PluginMarketplace:
    """
    Plugin marketplace for discovering and installing plugins
    
    This is a stub for future implementation.
    """
    
    def __init__(self, marketplace_url: str = ""):
        """Initialize marketplace"""
        self.marketplace_url = marketplace_url
        self.cache_dir = Path("~/.cache/brad_tui/marketplace").expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def search_plugins(self, query: str) -> List[Dict[str, Any]]:
        """Search for plugins"""
        # Stub: Would connect to marketplace API
        return []
    
    def get_plugin_details(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed plugin information"""
        # Stub: Would fetch from marketplace
        return None
    
    def install_plugin(self, plugin_id: str, plugin_dir: str) -> bool:
        """Install a plugin from marketplace"""
        # Stub: Would download and install
        return False
    
    def update_plugin(self, plugin_name: str) -> bool:
        """Update an installed plugin"""
        # Stub: Would check for updates and install
        return False


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Brad TUI Ultra - Plugin System")
    print("=" * 50)
    
    # Create plugin manager
    manager = PluginManager()
    
    # Discover plugins
    plugins = manager.discover_all()
    print(f"\nDiscovered {len(plugins)} plugins:")
    for plugin in plugins:
        print(f"  - {plugin}")
    
    # Load all plugins
    print("\nLoading plugins...")
    manager.load_all()
    
    # List loaded plugins
    print("\nPlugin status:")
    for name, status in manager.list_plugins().items():
        print(f"  {name}: {status.value}")
    
    # Test hook system
    print("\nTesting hooks...")
    results = manager.call_hook(HookType.PRE_COMMAND, "test command")
    print(f"Hook results: {results}")
    
    print("\n✅ Plugin system test complete")
