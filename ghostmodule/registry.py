import json
import os
from pathlib import Path
from typing import Dict, Optional, List

class ModuleRegistry:
    """Manages the registry of available ghost modules."""
    
    def __init__(self):
        self.builtin_modules = {}
        self.user_modules = {}
        self.user_defined = {}
        self._load_builtin_modules()
        self._load_user_modules()
    
    def register_builtin(self, modules: Dict[str, str]):
        """Register built-in modules from builtin_modules.py"""
        self.builtin_modules.update(modules)
    
    def register_user_module(self, alias: str, module_path: str, persist: bool = True):
        """
        Register a user-added module.
        
        Args:
            alias: The name to use (e.g., 'pd' or 'pandas')
            module_path: The module to import (e.g., 'pandas')
            persist: If True, save to user config file
        """
        self.user_modules[alias] = module_path
        
        if persist:
            self._save_user_modules()
    
    def register_user_defined(self, alias: str, file_path: str, 
                             imports: List[str], persist: bool = True):
        """
        Register user-defined imports from their own files.
        
        Args:
            alias: Namespace to import into (e.g., 'utils')
            file_path: Path to the .py file
            imports: List of names to import (e.g., ['helper_func', 'MyClass'])
            persist: If True, save to user config
        """
        self.user_defined[alias] = {
            'file_path': file_path,
            'imports': imports
        }
        
        if persist:
            self._save_user_modules()
    
    def get_module_path(self, name: str) -> Optional[str]:
        """
        Get the module path for a given name.
        Checks user modules first, then built-in.
        
        Returns the module path or None if not found.
        """
        # Check user modules first (allows overriding built-ins)
        if name in self.user_modules:
            return self.user_modules[name]
        
        if name in self.builtin_modules:
            return self.builtin_modules[name]
        
        # If not found as alias, try as direct module name
        for alias, module_path in {**self.builtin_modules, **self.user_modules}.items():
            if module_path == name:
                return name
        
        return None
    
    def get_user_defined(self, name: str) -> Optional[Dict]:
        """Get user-defined import configuration."""
        return self.user_defined.get(name)
    
    def list_available(self) -> Dict[str, List[str]]:
        """List all available modules by category."""
        return {
            'builtin': sorted(self.builtin_modules.keys()),
            'user_added': sorted(self.user_modules.keys()),
            'user_defined': sorted(self.user_defined.keys())
        }
    
    def _get_config_path(self) -> Path:
        """Get path to user config file."""
        config_dir = Path.home() / '.ghostmodule'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'user_modules.json'
    
    def _load_builtin_modules(self):
        try:
            from .builtin_modules import BUILTIN_MODULES
            self.builtin_modules = BUILTIN_MODULES.copy()
        except ImportError:
            pass

    def _load_user_modules(self):
        """Load user modules from config file."""
        config_path = self._get_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    self.user_modules = data.get('modules', {})
                    self.user_defined = data.get('user_defined', {})
            except Exception as e:
                print(f"Could not load user modules: {e}")
    
    def _save_user_modules(self):
        """Save user modules to config file."""
        config_path = self._get_config_path()
        
        try:
            data = {
                'modules': self.user_modules,
                'user_defined': self.user_defined
            }
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save user modules: {e}")
    
    def remove_module(self, alias: str):
        """Remove a user-added module."""
        if alias in self.user_modules:
            del self.user_modules[alias]
            self._save_user_modules()
            return True
        return False
    
    def remove_user_defined(self, alias: str):
        """Remove a user-defined import."""
        if alias in self.user_defined:
            del self.user_defined[alias]
            self._save_user_modules()
            return True
        return False


_registry = ModuleRegistry()

def get_registry() -> ModuleRegistry:
    """Get the global registry instance."""
    return _registry
