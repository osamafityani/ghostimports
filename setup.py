from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
import sys

def setup_ipython_startup():
    """Setup IPython startup script after installation."""
    try:
        from IPython.paths import get_ipython_dir
        
        ipython_dir = get_ipython_dir()
        startup_dir = os.path.join(ipython_dir, 'profile_default', 'startup')
        
        # Create startup directory if it doesn't exist
        os.makedirs(startup_dir, exist_ok=True)
        
        startup_file = os.path.join(startup_dir, '00-ghostimports.py')
        
        startup_code = '''# GhostImports auto-loader
try:
    from ghostimports import activate
    activate()
except ImportError:
    pass  # GhostImports not installed in this environment
'''
        
        with open(startup_file, 'w') as f:
            f.write(startup_code)
        
        print(f"\nGhostImports startup script installed at: {startup_file}")
        print("All Jupyter notebooks in this environment will now use ghostloader!\n")
        
    except Exception as e:
        print(f"\nCould not setup IPython startup script: {e}")
        print("You can manually run: python -m ghostimports.setup_ipython\n")

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        setup_ipython_startup()

class PostDevelopCommand(develop):
    def run(self):
        develop.run(self)
        setup_ipython_startup()

setup(
    name='ghostimports',
    version='0.2.0',
    description='Lazy-loading proxy modules for Jupyter notebooks',
    author='Osama Fityani',
    author_email='osamafitiani2001@gmail.com',
    packages=find_packages(),
    install_requires=[
        'ipython>=7.0.0',
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    entry_points={
        'console_scripts': [
            'ghostimports=ghostimports.cli:main',
        ],
    },
)
