"""Core GhostModule functionality with registry support."""

import sys
import importlib
import importlib.util
from typing import Optional, Dict, Any

from .registry import get_registry

class GhostModule:
    """A lazy-loading proxy that imports a module only when first accessed."""
    
    def __init__(self, module_name: str, alias: str, registry_entry: str):
        self._module_name = module_name
        self._alias = alias
        self._registry_entry = registry_entry
        self._module = None
    
    def _load(self):
        """Load the actual module on first access."""
        if self._module is None:
            try:
                self._module = importlib.import_module(self._module_name)
                print(f"ghostloader: imported '{self._module_name}' as '{self._alias}'")
                
                try:
                    from IPython import get_ipython
                    ipython = get_ipython()
                    if ipython is not None:
                        registry = get_registry()
                        
                        # Replace both the alias and full module name with real module
                        # Find all aliases that point to this module
                        all_modules = {**registry.builtin_modules, **registry.user_modules}
                        for alias, module_path in all_modules.items():
                            if module_path == self._module_name:
                                # Only replace if it's still a GhostModule (not already replaced)
                                if alias in ipython.user_ns and isinstance(ipython.user_ns[alias], GhostModule):
                                    ipython.user_ns[alias] = self._module
                except:
                    pass
                    
            except ImportError as e:
                print(f"ghostloader: could not import '{self._module_name}' - {e}")
                print(f"Try: pip install {self._module_name.split('.')[0]}")
                raise
        return self._module
    
    def __getattr__(self, name):
        """Proxy attribute access to the real module."""
        return getattr(self._load(), name)
    
    def __dir__(self):
        """Proxy dir() to the real module."""
        return dir(self._load())
    
    def __repr__(self):
        """Show that this is a GhostModule proxy."""
        if self._module is None:
            return f"<GhostModule '{self._module_name}' (not loaded)>"
        return repr(self._module)
    
    def __call__(self, *args, **kwargs):
        """Support calling the module directly if it's callable."""
        return self._load()(*args, **kwargs)


class UserDefinedGhost:
    """A ghost loader for user-defined imports from local files."""
    
    def __init__(self, alias: str, file_path: str, imports: list):
        self._alias = alias
        self._file_path = file_path
        self._imports = imports
        self._loaded = {}
    
    def _load(self):
        """Load the user's file and import specified names."""
        if not self._loaded:
            try:
                # Load the module from file path
                spec = importlib.util.spec_from_file_location(self._alias, self._file_path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Could not load {self._file_path}")
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Extract requested imports
                for name in self._imports:
                    if hasattr(module, name):
                        self._loaded[name] = getattr(module, name)
                    else:
                        print(f"'{name}' not found in {self._file_path}")
                
                print(f"ghostloader: imported {', '.join(self._loaded.keys())} from '{self._alias}'")
                
                # Replace in namespace
                try:
                    from IPython import get_ipython
                    ipython = get_ipython()
                    if ipython is not None:
                        # Create a simple namespace object
                        ns = type('UserModule', (), self._loaded)()
                        ipython.user_ns[self._alias] = ns
                except:
                    pass
                    
            except Exception as e:
                print(f"ghostloader: could not load user-defined module '{self._alias}' - {e}")
                raise
        
        return self._loaded
    
    def __getattr__(self, name):
        """Access imported names."""
        loaded = self._load()
        if name in loaded:
            return loaded[name]
        raise AttributeError(f"'{self._alias}' has no attribute '{name}'")
    
    def __dir__(self):
        """List available imports."""
        return list(self._load().keys())
    
    def __repr__(self):
        if not self._loaded:
            return f"<UserDefinedGhost '{self._alias}' (not loaded)>"
        return f"<UserDefinedGhost '{self._alias}' with {list(self._loaded.keys())}>"


def activate(custom_aliases: Optional[Dict[str, str]] = None, 
             load_user_defined: bool = True):
    """
    Activate lazy loading in IPython/Jupyter notebooks.
    
    Args:
        custom_aliases: Optional dict of additional aliases to add.
                       Format: {"alias": "module.path"}
        load_user_defined: Whether to load user-defined imports
    """
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        
        if ipython is None:
            return
        
        namespace = ipython.user_ns
        registry = get_registry()
        
        if custom_aliases:
            for alias, module_path in custom_aliases.items():
                registry.register_user_module(alias, module_path, persist=False)
        
        all_modules = {**registry.builtin_modules, **registry.user_modules}
        
        # Build a reverse mapping: module_path -> list of aliases
        module_to_aliases = {}
        for alias, module_path in all_modules.items():
            if module_path not in module_to_aliases:
                module_to_aliases[module_path] = []
            module_to_aliases[module_path].append(alias)
        
        # Inject GhostModule proxies for all aliases AND full module names
        loaded = []
        shared_ghosts = {}  # Cache GhostModule instances per module_path
        
        for module_path, aliases in module_to_aliases.items():
            # Create one shared GhostModule for this module_path
            # Use the first (shortest) alias as the display name
            primary_alias = min(aliases, key=len)
            ghost = GhostModule(module_path, primary_alias, module_path)
            shared_ghosts[module_path] = ghost
            
            # Inject the same ghost instance for ALL aliases pointing to this module
            for alias in aliases:
                if alias not in namespace:
                    namespace[alias] = ghost
                    loaded.append(alias)
            
            # Also inject using the full module path as a name (if not already an alias)
            # Extract the base module name (e.g., 'pandas' from 'pandas' or last part of 'matplotlib.pyplot')
            base_module = module_path.split('.')[-1]
            if base_module not in all_modules and base_module not in namespace:
                namespace[base_module] = ghost
                loaded.append(base_module)
        
        # Load user-defined imports
        if load_user_defined:
            for alias, config in registry.user_defined.items():
                if alias not in namespace:
                    namespace[alias] = UserDefinedGhost(
                        alias, 
                        config['file_path'], 
                        config['imports']
                    )
                    loaded.append(f"{alias} (user-defined)")
        
        if loaded:
            print(f"ghostloader: activated for {len(loaded)} modules")
        
    except ImportError:
        pass


def add_module(alias: str, module_path: str):
    """
    Add a new module to the registry (session-only by default).
    
    Usage:
        from ghostmodule import add_module
        add_module('alt', 'altair')  # Now 'alt' will work for altair
    """
    registry = get_registry()
    registry.register_user_module(alias, module_path, persist=False)
    
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ghost = GhostModule(module_path, alias, alias)
            ipython.user_ns[alias] = ghost
            
            # Also add the full module name if different
            base_module = module_path.split('.')[-1]
            if base_module != alias and base_module not in ipython.user_ns:
                ipython.user_ns[base_module] = ghost
            
            print(f"✅ Added '{alias}' → '{module_path}' to current session")
    except:
        pass


def save_module(alias: str, module_path: str):
    """
    Save a module to permanent user registry.
    
    Usage:
        from ghostmodule import save_module
        save_module('alt', 'altair')  # Persists across sessions
    """
    registry = get_registry()
    registry.register_user_module(alias, module_path, persist=True)
    
    # Also add to current session
    add_module(alias, module_path)
    print(f"💾 Saved '{alias}' → '{module_path}' permanently")


def add_user_defined(alias: str, file_path: str, imports: list):
    """
    Add user-defined imports from a local file (session-only).
    
    Usage:
        from ghostmodule import add_user_defined
        add_user_defined('utils', '/path/to/utils.py', ['helper', 'MyClass'])
        # Now you can use: utils.helper() or utils.MyClass()
    """
    registry = get_registry()
    registry.register_user_defined(alias, file_path, imports, persist=False)
    
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ipython.user_ns[alias] = UserDefinedGhost(alias, file_path, imports)
            print(f"✅ Added user-defined '{alias}' from {file_path}")
    except:
        pass


def save_user_defined(alias: str, file_path: str, imports: list):
    """
    Save user-defined imports permanently.
    
    Usage:
        from ghostmodule import save_user_defined
        save_user_defined('utils', '~/my_utils.py', ['helper'])
    """
    registry = get_registry()
    registry.register_user_defined(alias, file_path, imports, persist=True)
    
    add_user_defined(alias, file_path, imports)
    print(f"Saved user-defined '{alias}' permanently")


def list_modules():
    """List all available ghost modules."""
    registry = get_registry()
    available = registry.list_available()
    
    print("Available GhostModules:\n")
    
    if available['builtin']:
        print(f"Built-in ({len(available['builtin'])} modules):")
        print(f"{', '.join(available['builtin'][:20])}")
        if len(available['builtin']) > 20:
            print(f"  ... and {len(available['builtin']) - 20} more")
    
    if available['user_added']:
        print(f"\nUser-added ({len(available['user_added'])} modules):")
        print(f"{', '.join(available['user_added'])}")
    
    if available['user_defined']:
        print(f"\nUser-defined ({len(available['user_defined'])} namespaces):")
        print(f"{', '.join(available['user_defined'])}")
    
    print("\nTip: Use 'ghostmodule list --detailed' for full list")
