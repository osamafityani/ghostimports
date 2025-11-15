"""Core GhostModule functionality with registry support."""

import sys
import importlib
import importlib.util
from typing import Optional, Dict, Any, List

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
                        all_modules = {**registry.builtin_modules, **registry.user_modules}
                        for alias, module_path in all_modules.items():
                            if module_path == self._module_name:
                                if alias in ipython.user_ns and isinstance(ipython.user_ns[alias], GhostModule):
                                    ipython.user_ns[alias] = self._module
                except:
                    pass
                    
            except ImportError as e:
                print(f"ghostloader: could not import '{self._module_name}' - {e}")
                print(f"   Try: pip install {self._module_name.split('.')[0]}")
                raise
        return self._module
    
    def __getattr__(self, name):
        return getattr(self._load(), name)
    
    def __dir__(self):
        return dir(self._load())
    
    def __repr__(self):
        if self._module is None:
            return f"<GhostModule '{self._module_name}' (not loaded)>"
        return repr(self._module)
    
    def __call__(self, *args, **kwargs):
        return self._load()(*args, **kwargs)


class UserDefinedGhost:
    """A ghost loader for user-defined imports from local files."""
    
    def __init__(self, alias: str, file_path: str, imports: List[str], inject_directly: bool = False):
        self._alias = alias
        self._file_path = file_path
        self._imports = imports
        self._inject_directly = inject_directly
        self._module = None
        self._loaded_items = {}
    
    def _load(self):
        """Load the user's file and import specified names."""
        if self._module is None:
            try:
                spec = importlib.util.spec_from_file_location(self._alias, self._file_path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Could not load {self._file_path}")
                
                self._module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self._module)
                
                for name in self._imports:
                    if hasattr(self._module, name):
                        self._loaded_items[name] = getattr(self._module, name)
                    else:
                        print(f"  '{name}' not found in {self._file_path}")
                
                print(f"ghostloader: imported {', '.join(self._loaded_items.keys())} from '{self._file_path}'")
                
                try:
                    from IPython import get_ipython
                    ipython = get_ipython()
                    if ipython is not None:
                        if self._inject_directly:
                            for name, obj in self._loaded_items.items():
                                ipython.user_ns[name] = obj
                        else:
                            for name, obj in self._loaded_items.items():
                                setattr(self, name, obj)
                except:
                    pass
                    
            except Exception as e:
                print(f"ghostloader: could not load user-defined module from '{self._file_path}' - {e}")
                raise
        
        return self._loaded_items
    
    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(f"'{self._alias}' has no attribute '{name}'")
        
        loaded = self._load()
        if name in loaded:
            return loaded[name]
        raise AttributeError(f"'{self._alias}' has no attribute '{name}'")
    
    def __dir__(self):
        self._load()
        return list(self._loaded_items.keys())
    
    def __repr__(self):
        if self._module is None:
            return f"<UserDefinedGhost '{self._file_path}' (not loaded)>"
        return f"<UserDefinedGhost '{self._file_path}' with {list(self._loaded_items.keys())}>"


def activate(custom_aliases: Optional[Dict[str, str]] = None, 
             load_user_defined: bool = True):
    """
    Activate lazy loading in IPython/Jupyter notebooks.
    
    Args:
        custom_aliases: Optional dict of additional aliases to add.
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
        
        module_to_aliases = {}
        for alias, module_path in all_modules.items():
            if module_path not in module_to_aliases:
                module_to_aliases[module_path] = []
            module_to_aliases[module_path].append(alias)
        
        loaded = []
        shared_ghosts = {}
        
        for module_path, aliases in module_to_aliases.items():
            primary_alias = min(aliases, key=len)
            ghost = GhostModule(module_path, primary_alias, module_path)
            shared_ghosts[module_path] = ghost
            
            for alias in aliases:
                if alias not in namespace:
                    namespace[alias] = ghost
                    loaded.append(alias)
            
            base_module = module_path.split('.')[-1]
            if base_module not in all_modules and base_module not in namespace:
                namespace[base_module] = ghost
                loaded.append(base_module)
        
        if load_user_defined:
            for alias, config in registry.user_defined.items():
                inject_directly = config.get('inject_directly', False)
                
                if inject_directly:
                    ghost = UserDefinedGhost(
                        alias, 
                        config['file_path'], 
                        config['imports'],
                        inject_directly=True
                    )
                    ghost._load()
                    loaded.extend([f"{name} (user-defined)" for name in config['imports']])
                else:
                    if alias not in namespace and not alias.startswith('__direct__'):
                        namespace[alias] = UserDefinedGhost(
                            alias, 
                            config['file_path'], 
                            config['imports'],
                            inject_directly=False
                        )
                        loaded.append(f"{alias} (user-defined)")
        
        if loaded:
            print(f"ghostloader: activated for {len(loaded)} modules")
        
    except ImportError:
        pass


def add_module(alias: str, module_path: str):
    registry = get_registry()
    registry.register_user_module(alias, module_path, persist=False)
    
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ghost = GhostModule(module_path, alias, alias)
            ipython.user_ns[alias] = ghost
            
            base_module = module_path.split('.')[-1]
            if base_module != alias and base_module not in ipython.user_ns:
                ipython.user_ns[base_module] = ghost
            
            print(f"Added '{alias}' -> '{module_path}' to current session")
    except:
        pass


def save_module(alias: str, module_path: str):
    registry = get_registry()
    registry.register_user_module(alias, module_path, persist=True)
    add_module(alias, module_path)
    print(f"Saved '{alias}' -> '{module_path}' permanently")


def add_user_defined(alias: Optional[str], file_path: str, imports: List[str], inject_directly: bool = False):
    import importlib.util
    
    if imports == ['*'] or (len(imports) == 1 and imports[0] == '*'):
        try:
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            imports = [name for name in dir(module) 
                      if not name.startswith('_') 
                      and callable(getattr(module, name))]
            
            print(f"Found: {', '.join(imports)}")
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    
    if inject_directly and alias is None:
        alias = f"__direct__{file_path}"
    
    registry = get_registry()
    registry.register_user_defined(alias, file_path, imports, persist=False, inject_directly=inject_directly)
    
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ghost = UserDefinedGhost(alias, file_path, imports, inject_directly=inject_directly)
            
            if inject_directly:
                ghost._load()
                print(f"Added user-defined functions directly: {', '.join(imports)}")
            else:
                ipython.user_ns[alias] = ghost
                print(f"Added user-defined '{alias}' from {file_path}")
    except:
        pass


def save_user_defined(alias: Optional[str], file_path: str, imports: List[str], inject_directly: bool = False):
    import importlib.util
    
    if imports == ['*'] or (len(imports) == 1 and imports[0] == '*'):
        try:
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            imports = [name for name in dir(module) 
                      if not name.startswith('_') 
                      and callable(getattr(module, name))]
            
            print(f"Found: {', '.join(imports)}")
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    
    if inject_directly and alias is None:
        alias = f"__direct__{file_path}"
    
    registry = get_registry()
    registry.register_user_defined(alias, file_path, imports, persist=True, inject_directly=inject_directly)
    add_user_defined(alias, file_path, imports, inject_directly=inject_directly)
    print(f"Saved user-defined from '{file_path}' permanently")


def list_modules():
    registry = get_registry()
    available = registry.list_available()
    
    print("Available GhostModules:\n")
    
    if available['builtin']:
        print(f"Built-in ({len(available['builtin'])} modules):")
        print(f"  {', '.join(available['builtin'][:20])}")
        if len(available['builtin']) > 20:
            print(f"  ... and {len(available['builtin']) - 20} more")
    
    if available['user_added']:
        print(f"\nUser-added ({len(available['user_added'])} modules):")
        print(f"  {', '.join(available['user_added'])}")
    
    if available['user_defined']:
        print(f"\nUser-defined ({len(available['user_defined'])} namespaces):")
        for item in available['user_defined']:
            if item.startswith('direct:'):
                file_path = item[7:]
                config = registry.get_user_defined_by_path(file_path)
                if config:
                    imports = registry.user_defined[config]['imports']
                    print(f"  {file_path}: {', '.join(imports)} [direct]")
            else:
                config = registry.user_defined.get(item)
                if config:
                    print(f"  {item}: {', '.join(config['imports'])} [via {item}]")
    
    print("\nTip: Use 'ghostmodule list --detailed' for full list")
