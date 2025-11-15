"""Command-line interface for GhostModule management."""

import argparse
import sys
import importlib.util
from pathlib import Path
from .registry import get_registry
from .builtin_modules import CATEGORIES

def list_modules(detailed=False):
    registry = get_registry()
    
    if detailed:
        print("GhostModule Registry\n")
        print("=" * 60)
        
        for category, modules in CATEGORIES.items():
            print(f"\n{category}:")
            for alias, module_path in sorted(modules.items()):
                print(f"  {alias:20} -> {module_path}")
        
        user_modules = registry.user_modules
        if user_modules:
            print(f"\nUser-Added Modules:")
            for alias, module_path in sorted(user_modules.items()):
                print(f"  {alias:20} -> {module_path}")
        
        user_defined = registry.user_defined
        if user_defined:
            print(f"\nUser-Defined Imports:")
            for alias, config in sorted(user_defined.items()):
                imports_str = ', '.join(config['imports'])
                mode = "direct" if config.get('inject_directly', False) else f"via {alias}"
                display_alias = config['file_path'] if alias.startswith('__direct__') else alias
                print(f"  {display_alias:30} -> {config['file_path']}")
                print(f"  {' '*30}   [{imports_str}] [{mode}]")
    else:
        available = registry.list_available()
        print(f"Built-in: {len(available['builtin'])} modules")
        print(f"User-added: {len(available['user_added'])} modules")
        print(f"User-defined: {len(available['user_defined'])} namespaces")
        print("\nUse --detailed for full list")

def add_module_cmd(alias, module_path, permanent=False):
    registry = get_registry()
    registry.register_user_module(alias, module_path, persist=permanent)
    
    if permanent:
        print(f"Saved '{alias}' -> '{module_path}' permanently")
    else:
        print(f"Added '{alias}' -> '{module_path}' (session only)")
        print("   Use --permanent to save across sessions")

def remove_module_cmd(alias):
    registry = get_registry()
    if registry.remove_module(alias):
        print(f"Removed '{alias}'")
    else:
        print(f"'{alias}' not found in user modules")

def get_all_functions_from_file(file_path):
    """Extract all public functions/classes from a Python file."""
    try:
        spec = importlib.util.spec_from_file_location("temp_module", file_path)
        if spec is None or spec.loader is None:
            print(f"Could not load {file_path}")
            return []
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        public_names = [name for name in dir(module) 
                       if not name.startswith('_') 
                       and callable(getattr(module, name))]
        
        return public_names
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def add_user_defined_cmd(alias, file_path, imports, permanent=False, direct=False):
    registry = get_registry()
    
    if imports == '*':
        imports_list = get_all_functions_from_file(file_path)
        if not imports_list:
            print(f"No public functions found in {file_path}")
            return
        print(f"Found: {', '.join(imports_list)}")
    else:
        imports_list = [i.strip() for i in imports.split(',')]
    
    final_alias = None if direct else alias
    
    registry.register_user_defined(final_alias, file_path, imports_list, persist=permanent, inject_directly=direct)
    
    mode = "directly" if direct else f"via '{alias}'"
    if permanent:
        print(f"Saved user-defined imports {mode} permanently")
    else:
        print(f"Added user-defined imports {mode} (session only)")
        print("   Use --permanent to save across sessions")

def remove_user_defined_cmd(alias=None, file_path=None):
    registry = get_registry()
    
    if file_path:
        if registry.remove_user_defined_by_path(file_path):
            print(f"Removed user-defined imports from '{file_path}'")
        else:
            print(f"No user-defined imports found for '{file_path}'")
    elif alias:
        if registry.remove_user_defined(alias):
            print(f"Removed user-defined '{alias}'")
        else:
            print(f"'{alias}' not found in user-defined modules")
    else:
        print("Must provide either --alias or --file")

def clear_all_cmd():
    registry = get_registry()
    
    user_count = len(registry.user_modules)
    defined_count = len(registry.user_defined)
    
    if user_count == 0 and defined_count == 0:
        print("No user data to clear")
        return
    
    print(f"This will remove:")
    print(f"  - {user_count} user-added modules")
    print(f"  - {defined_count} user-defined imports")
    
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    if confirm in ['yes', 'y']:
        registry.clear_all_user_data()
        print("All user data cleared")
    else:
        print("Cancelled")

def main():
    parser = argparse.ArgumentParser(
        description='GhostModule - Lazy-loading module manager',
        prog='ghostmodule'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    list_parser = subparsers.add_parser('list', help='List available modules')
    list_parser.add_argument('--detailed', '-d', action='store_true',
                            help='Show detailed module list')
    
    add_parser = subparsers.add_parser('add', help='Add a new module')
    add_parser.add_argument('alias', help='Alias for the module')
    add_parser.add_argument('module', help='Module path')
    add_parser.add_argument('--permanent', '-p', action='store_true',
                           help='Save permanently')
    
    remove_parser = subparsers.add_parser('remove', help='Remove a user module')
    remove_parser.add_argument('alias', help='Alias to remove')
    
    add_user_parser = subparsers.add_parser('add-user', help='Add user-defined imports')
    add_user_parser.add_argument('file', help='Path to Python file')
    add_user_parser.add_argument('imports', help='Comma-separated list of names or "*" for all public functions')
    add_user_parser.add_argument('--alias', '-a', help='Namespace alias (not required for direct imports)')
    add_user_parser.add_argument('--permanent', '-p', action='store_true',
                                help='Save permanently')
    add_user_parser.add_argument('--direct', '-d', action='store_true',
                                help='Inject directly without alias')
    
    remove_user_parser = subparsers.add_parser('remove-user', help='Remove user-defined imports')
    remove_user_group = remove_user_parser.add_mutually_exclusive_group(required=True)
    remove_user_group.add_argument('--alias', '-a', help='Alias to remove')
    remove_user_group.add_argument('--file', '-f', help='File path to remove')
    
    clear_parser = subparsers.add_parser('clear', help='Remove all user-added modules and user-defined imports')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_modules(detailed=args.detailed)
    elif args.command == 'add':
        add_module_cmd(args.alias, args.module, permanent=args.permanent)
    elif args.command == 'remove':
        remove_module_cmd(args.alias)
    elif args.command == 'add-user':
        if not args.direct and not args.alias:
            print("Error: --alias is required unless using --direct")
            sys.exit(1)
        alias = args.alias if args.alias else None
        add_user_defined_cmd(alias, args.file, args.imports, 
                            permanent=args.permanent, direct=args.direct)
    elif args.command == 'remove-user':
        remove_user_defined_cmd(alias=args.alias, file_path=args.file)
    elif args.command == 'clear':
        clear_all_cmd()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
