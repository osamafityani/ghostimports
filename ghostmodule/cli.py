import argparse
import sys
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
                print(f"  {alias:20} -> {config['file_path']}")
                print(f"  {' '*20}   [{imports_str}] [{mode}]")
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

def add_user_defined_cmd(alias, file_path, imports, permanent=False, direct=False):
    registry = get_registry()
    imports_list = [i.strip() for i in imports.split(',')]
    registry.register_user_defined(alias, file_path, imports_list, persist=permanent, inject_directly=direct)
    
    mode = "directly" if direct else f"via '{alias}'"
    if permanent:
        print(f"Saved user-defined imports {mode} permanently")
    else:
        print(f"Added user-defined imports {mode} (session only)")
        print("   Use --permanent to save across sessions")

def remove_user_defined_cmd(alias):
    registry = get_registry()
    if registry.remove_user_defined(alias):
        print(f"Removed user-defined '{alias}'")
    else:
        print(f"'{alias}' not found in user-defined modules")

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
    add_user_parser.add_argument('alias', help='Namespace alias (or "direct" for no alias)')
    add_user_parser.add_argument('file', help='Path to Python file')
    add_user_parser.add_argument('imports', help='Comma-separated list of names to import')
    add_user_parser.add_argument('--permanent', '-p', action='store_true',
                                help='Save permanently')
    add_user_parser.add_argument('--direct', '-d', action='store_true',
                                help='Inject directly without alias')
    
    remove_user_parser = subparsers.add_parser('remove-user', help='Remove user-defined imports')
    remove_user_parser.add_argument('alias', help='Alias to remove')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_modules(detailed=args.detailed)
    elif args.command == 'add':
        add_module_cmd(args.alias, args.module, permanent=args.permanent)
    elif args.command == 'remove':
        remove_module_cmd(args.alias)
    elif args.command == 'add-user':
        add_user_defined_cmd(args.alias, args.file, args.imports, 
                            permanent=args.permanent, direct=args.direct)
    elif args.command == 'remove-user':
        remove_user_defined_cmd(args.alias)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
