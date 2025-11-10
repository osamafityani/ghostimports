import os
import sys

def setup():
    """Setup IPython startup script manually."""
    try:
        from IPython.paths import get_ipython_dir
        
        ipython_dir = get_ipython_dir()
        startup_dir = os.path.join(ipython_dir, 'profile_default', 'startup')
        
        # Create startup directory if it doesn't exist
        os.makedirs(startup_dir, exist_ok=True)
        
        startup_file = os.path.join(startup_dir, '00-ghostmodule.py')
        
        startup_code = '''# GhostModule auto-loader
try:
    from ghostmodule import activate
    activate()
except ImportError:
    pass  # GhostModule not installed in this environment
'''
        
        with open(startup_file, 'w') as f:
            f.write(startup_code)
        
        print(f"GhostModule startup script installed at: {startup_file}")
        print("All Jupyter notebooks will now use ghostloader!")
        return True
        
    except Exception as e:
        print(f"Error setting up IPython startup: {e}")
        return False

if __name__ == '__main__':
    setup()
