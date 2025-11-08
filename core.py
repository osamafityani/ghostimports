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
    def __init__(self, module_name, alias):
        self._module_name = module_name
        self._alias = alias
        self._module = None
    
    def _load(self):
        if self._module is None:
            self._module = importlib.import_module(self._module_name)
            print(f"Ghost Module: imported '{self._module_name}' as '{self._alias}'")
            if 'get_ipython' in dir():
                from IPython import get_ipython
                get_ipython().user_ns[self._alias] = self._module
        return self._module
    
    def __getattr__(self, name):
        return getattr(self._load(), name)
    
    def __dir__(self):
        return dir(self._load())
    
    def __repr__(self):
        return f"<GhostModule '{self._module_name}'>"

def activate():
    """Activate ghost loading in the calling namespace (notebook or script)."""
    frame = sys._getframe(1)
    namespace = frame.f_globals
    
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            namespace = ipython.user_ns
    except:
        pass
    
    for alias, module_name in ALIASES.items():
        if alias not in namespace:
            namespace[alias] = GhostModule(module_name, alias)
    
    print("Ghost loader activated!")
