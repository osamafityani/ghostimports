import sys
import importlib

ALIASES = {
    "pd": "pandas",
    "np": "numpy",
    "plt": "matplotlib.pyplot",
    "sns": "seaborn",
    "tf": "tensorflow",
    "torch": "torch",
}

class GhostModule:
    """A lazy-loading proxy that imports a module only when first accessed."""
    
    def __init__(self, module_name, alias):
        self._module_name = module_name
        self._alias = alias
        self._module = None
    
    def _load(self):
        """Load the actual module on first access."""
        if self._module is None:
            try:
                self._module = importlib.import_module(self._module_name)
                print(f"ghostloader: imported '{self._module_name}' as '{self._alias}'")
                
                # Replace the proxy with the real module in IPython namespace
                try:
                    from IPython import get_ipython
                    ipython = get_ipython()
                    if ipython is not None:
                        ipython.user_ns[self._alias] = self._module
                except:
                    pass
                    
            except ImportError as e:
                print(f"ghostloader: could not import '{self._module_name}' - {e}")
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


def activate(custom_aliases=None):
    """
    Activate lazy loading in IPython/Jupyter notebooks.
    
    Args:
        custom_aliases: Optional dict of additional aliases to add.
                       Format: {"alias": "module.path"}
    """
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        
        if ipython is None:
            # Not in IPython/Jupyter environment
            return
        
        namespace = ipython.user_ns
        
        # Merge custom aliases if provided
        aliases = ALIASES.copy()
        if custom_aliases:
            aliases.update(custom_aliases)
        
        # Inject GhostModule proxies
        loaded = []
        for alias, module_name in aliases.items():
            if alias not in namespace:
                namespace[alias] = GhostModule(module_name, alias)
                loaded.append(alias)
        
        if loaded:
            print(f"ghostloader: activated for {', '.join(loaded)}")
        
    except ImportError:
        # IPython not available
        pass
