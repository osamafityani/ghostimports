"""GhostModule - Lazy-loading proxy modules for Jupyter notebooks."""

from .core import (
    activate, 
    GhostModule, 
    add_module,
    save_module,
    add_user_defined,
    save_user_defined,
    list_modules
)
from .registry import get_registry
from .builtin_modules import BUILTIN_MODULES, CATEGORIES

_registry = get_registry()
if not _registry.builtin_modules:
    _registry.register_builtin(BUILTIN_MODULES)

__version__ = '0.2.0'
__all__ = [
    'activate',
    'GhostModule',
    'add_module',
    'save_module',
    'add_user_defined',
    'save_user_defined',
    'list_modules',
    'get_registry',
    'BUILTIN_MODULES',
    'CATEGORIES'
]
