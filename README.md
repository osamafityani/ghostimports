# GhostImports

Lazy-loading proxy modules for Jupyter notebooks. Stop writing import statements and start coding.

## What is GhostImports?

GhostImports automatically makes common data science packages available in your Jupyter notebooks without explicit imports. Modules are only loaded when you first use them, so there's no performance penalty.
```python
# No imports needed
df = pd.read_csv("data.csv")      # pandas loads automatically
arr = np.array([1, 2, 3])         # numpy loads automatically
plt.plot(arr)                      # matplotlib loads automatically
```

## Features

- **Zero imports**: Use 80+ pre-configured modules without import statements
- **Lazy loading**: Modules only load when you actually use them
- **Both aliases and full names**: Use `pd` or `pandas`, both work
- **Extensible**: Add your own modules and custom functions
- **Persistent**: Configuration survives across sessions
- **User-defined imports**: Import from your own helper files

## Installation
```bash
pip install ghostimports
```

The installation automatically configures IPython to activate GhostImports in all notebooks.

### Manual Setup

If automatic setup didn't work:
```bash
python -m ghostimports.setup_ipython
```

## Quick Start

After installation, just start using modules in any Jupyter notebook:
```python
# All of these work immediately without imports
df = pd.read_csv("data.csv")
df = pandas.read_csv("data.csv")  # Full names work too

arr = np.random.randn(100)
arr = numpy.random.randn(100)     # Both work

plt.plot(arr)
sns.heatmap(data)
model = tf.keras.Sequential()
```

## Built-in Modules

GhostImports includes 80+ pre-configured modules across multiple categories:

### Data Science
- `pd`, `pandas` - pandas
- `np`, `numpy` - numpy
- `sp`, `scipy` - scipy

### Visualization
- `plt` - matplotlib.pyplot
- `sns`, `seaborn` - seaborn
- `px` - plotly.express
- `go` - plotly.graph_objects

### Machine Learning
- `tf`, `tensorflow` - tensorflow
- `torch`, `pytorch` - torch
- `keras` - keras
- `sk`, `sklearn` - sklearn

### Deep Learning
- `nn` - torch.nn
- `F` - torch.nn.functional
- `optim` - torch.optim

### NLP
- `nltk` - nltk
- `spacy` - spacy
- `transformers` - transformers

### Computer Vision
- `cv2` - cv2
- `PIL` - PIL
- `Image` - PIL.Image
- `skimage` - skimage

### Web & APIs
- `requests` - requests
- `bs4` - bs4
- `BeautifulSoup` - bs4.BeautifulSoup
- `flask` - flask
- `fastapi` - fastapi

### Utilities
- `re`, `regex` - re
- `os` - os
- `sys` - sys
- `pathlib` - pathlib
- `Path` - pathlib.Path
- `datetime`, `dt` - datetime
- `json` - json
- `pickle` - pickle

And many more. Use `ghostimports list --detailed` to see all available modules.

## CLI Commands

### List Modules
```bash
# Quick summary
ghostimports list

# Output:
# Built-in: 82 modules
# User-added: 3 modules
# User-defined: 2 namespaces

# Detailed list with all modules
ghostimports list --detailed

# Output shows all modules organized by category:
# Data Science:
#   pd                   -> pandas
#   numpy                -> numpy
# ...
```

### Add Module

Add a new module alias for the current session or permanently.
```bash
# Add for current session only
ghostimports add alt altair

# Add permanently (survives notebook restarts)
ghostimports add alt altair --permanent
ghostimports add alt altair -p

# Now use it in notebooks
# alt.Chart(data).mark_bar()
```

**Examples:**
```bash
# Add plotly express with custom alias
ghostimports add px plotly.express -p

# Add dask dataframe
ghostimports add dd dask.dataframe -p

# Add polars
ghostimports add pl polars -p
```

### Remove Module

Remove a user-added module.
```bash
# Remove by alias
ghostimports remove alt

# This only removes user-added modules, not built-in ones
```

### Add User-Defined Imports

Import functions from your own Python files.

#### Basic Usage (with alias)
```bash
# Import specific functions via an alias
ghostimports add-user ~/utils.py "helper,process_data" --alias utils

# Now use in notebooks:
# result = utils.helper(data)
# df = utils.process_data(raw_df)
```

#### Import All Functions
```bash
# Use * to import all public functions/classes
ghostimports add-user ~/utils.py "*" --alias utils

# Finds all functions that don't start with _
```

#### Direct Import (no alias)
```bash
# Import functions directly into namespace
ghostimports add-user ~/utils.py "helper,process_data" --direct

# Now use directly without alias:
# result = helper(data)
# df = process_data(raw_df)
```

#### Permanent User-Defined Imports
```bash
# Add permanently with --permanent or -p
ghostimports add-user ~/utils.py "*" --alias utils --permanent
ghostimports add-user ~/helpers.py "*" --direct -p
```

**Full Examples:**
```bash
# Import data processing utilities
ghostimports add-user ~/project/data_utils.py "clean_data,load_from_db" --alias data -p

# Import ML helper functions directly
ghostimports add-user ~/ml_helpers.py "train_model,evaluate,plot_results" --direct -p

# Import all functions from a module
ghostimports add-user ~/viz.py "*" --alias viz -p
```

### Remove User-Defined Imports

Remove user-defined imports by alias or file path.
```bash
# Remove by alias
ghostimports remove-user --alias utils
ghostimports remove-user -a utils

# Remove by file path (useful for direct imports)
ghostimports remove-user --file ~/utils.py
ghostimports remove-user -f ~/utils.py
```

### Clear All User Data

Remove all user-added modules and user-defined imports at once.
```bash
ghostimports clear

# Output:
# This will remove:
#   - 3 user-added modules
#   - 2 user-defined imports
# Are you sure? (yes/no): yes
# All user data cleared
```

This is useful for:
- Cleaning up experimental configurations
- Resetting to default state
- Removing all customizations before sharing environment

## Python API

You can also manage modules from within Python/notebooks.

### Adding Modules
```python
from ghostimports import add_module, save_module

# Add for current session
add_module('alt', 'altair')

# Save permanently
save_module('alt', 'altair')
save_module('dd', 'dask.dataframe')
```

### Adding User-Defined Imports
```python
from ghostimports import add_user_defined, save_user_defined

# With alias (session only)
add_user_defined('utils', '~/utils.py', ['helper', 'process'])

# Save permanently
save_user_defined('utils', '~/utils.py', ['helper', 'process'])

# Import all functions
save_user_defined('utils', '~/utils.py', ['*'])

# Direct injection (no alias)
save_user_defined(None, '~/utils.py', ['helper', 'process'], inject_directly=True)
```

### Listing Modules
```python
from ghostimports import list_modules

list_modules()

# Output:
# Available GhostImports:
# Built-in (82 modules): pd, np, plt, sns, ...
# User-added (3 modules): alt, dd, pl
# User-defined (2 namespaces): utils, viz
```

## Complete Usage Examples

### Example 1: Data Science Workflow
```python
# No imports needed!

# Load data
df = pd.read_csv("sales.csv")
df = pandas.read_parquet("large_data.parquet")  # Full name also works

# Process
df['total'] = df['price'] * df['quantity']
summary = df.groupby('category').sum()

# Visualize
plt.figure(figsize=(10, 6))
sns.barplot(data=summary, x='category', y='total')
plt.show()

# Statistical analysis
from scipy import stats
correlation = stats.pearsonr(df['price'], df['quantity'])
```

### Example 2: Machine Learning Pipeline
```python
# All these work without imports

# Prepare data
X = np.array(features)
y = np.array(labels)

# Split data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Build model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)
])

# Or PyTorch
model = nn.Sequential(
    nn.Linear(10, 64),
    nn.ReLU(),
    nn.Linear(64, 1)
)
```

### Example 3: Custom Helper Functions

Create a helper file:
```python
# ~/project/helpers.py

def load_data(path):
    """Load and clean data."""
    import pandas as pd
    df = pd.read_csv(path)
    df = df.dropna()
    return df

def train_model(X, y):
    """Train a simple model."""
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier()
    model.fit(X, y)
    return model

def plot_results(y_true, y_pred):
    """Plot confusion matrix."""
    from sklearn.metrics import confusion_matrix
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True)
    plt.show()
```

Add to GhostImports:
```bash
# Add all functions with an alias
ghostimports add-user ~/project/helpers.py "*" --alias h --permanent

# Or add them for direct use (without an alias)
ghostimports add-user ~/project/helpers.py "*" --direct --permanent
```

Use in notebooks:
```python
# With alias
df = h.load_data("train.csv")
model = h.train_model(X_train, y_train)
h.plot_results(y_test, predictions)

# With direct import
df = load_data("train.csv")
model = train_model(X_train, y_train)
plot_results(y_test, predictions)
```

### Example 4: Web Scraping
```python
# No imports!

# Fetch page
response = requests.get("https://example.com")

# Parse HTML
soup = BeautifulSoup(response.content, 'html.parser')
titles = soup.find_all('h2')

# Process data
data = [title.text for title in titles]
df = pd.DataFrame(data, columns=['title'])

# Save results
df.to_csv("results.csv", index=False)
```

### Example 5: Managing Multiple Projects
```bash
# Project 1: Data Science
ghostimports add polars polars -p
ghostimports add-user ~/ds_project/utils.py "*" --alias dsu -p

# Project 2: Web Development
ghostimports add fastapi fastapi -p
ghostimports add-user ~/web_project/auth.py "login,logout,verify" --alias auth -p

# Project 3: Computer Vision
ghostimports add albumentations albumentations -p
ghostimports add-user ~/cv_project/transforms.py "*" --direct -p

# Clean up when switching projects
ghostimports clear
```

## How It Works

1. **Installation**: Sets up IPython startup script at `~/.ipython/profile_default/startup/00-ghostimports.py`

2. **Startup**: When Jupyter starts, the startup script runs and calls `activate()`

3. **Activation**: GhostImports injects proxy objects into the notebook namespace for all configured modules

4. **First Use**: When you access a module (e.g., `pd.read_csv()`), the proxy:
   - Imports the real module using `importlib`
   - Replaces all related proxies with the real module
   - Returns the requested attribute

5. **Subsequent Uses**: Direct access to the real module with zero overhead

## Configuration Storage

All user configuration is stored in `~/.ghostimports/user_modules.json`:
```json
{
  "modules": {
    "alt": "altair",
    "dd": "dask.dataframe"
  },
  "user_defined": {
    "utils": {
      "file_path": "/home/user/utils.py",
      "imports": ["helper", "process"],
      "inject_directly": false
    },
    "__direct__/home/user/helpers.py": {
      "file_path": "/home/user/helpers.py",
      "imports": ["load_data", "train_model"],
      "inject_directly": true
    }
  }
}
```

## Troubleshooting

### Modules Not Loading
```bash
# Check if startup script exists
ls ~/.ipython/profile_default/startup/00-ghostimports.py

# If not, run setup manually
python -m ghostimports.setup_ipython
```

### Module Not Found
```python
# The module might not be installed
# GhostImports tells you what to install
pd.read_csv("data.csv")
# Output: ghostloader: could not import 'pandas' - No module named 'pandas'
#         Try: pip install pandas

# Install it
!pip install pandas

# Restart kernel and try again
```

### Checking What's Loaded
```python
from ghostimports import list_modules
list_modules()

# Or from CLI
ghostimports list --detailed
```

### Reset Everything
```bash
# Clear all user data
ghostimports clear

# Remove startup script
rm ~/.ipython/profile_default/startup/00-ghostimports.py

# Remove config
rm -rf ~/.ghostimports
```

## Uninstall
```bash
# Remove package
pip uninstall ghostimports

# Remove startup script
rm ~/.ipython/profile_default/startup/00-ghostimports.py

# Remove user config
rm -rf ~/.ghostimports
```

## Contributing

### Adding Built-in Modules

Want to add a popular package to the built-in list?

1. Fork the repository
2. Edit `ghostimports/builtin_modules.py`
3. Add to the appropriate category:
```python
MACHINE_LEARNING = {
    'xgb': 'xgboost',
    'xgboost': 'xgboost',
    # ... existing entries
}
```

4. Test it works
5. Submit a pull request

### Requesting Modules

Create an issue with:
- Module name and common aliases
- Category (Data Science, ML, Visualization, etc.)
- Or add it to the builtin-modules file and send a PR

## Best Practices

### Do's

- Use GhostImports for interactive notebook work
- Import helper functions from your utility files
- Use `ghostimport list` to see what's available

### Don'ts

- Don't use GhostImports in production Python scripts
- Don't rely on it for package distribution
- Don't forget to install the actual packages you use
- Don't import GhostImports itself unless configuring it

### Recommended Workflow
```python
# In notebooks: just use modules
df = pd.read_csv("data.csv")

# When sharing code: add explicit imports
import pandas as pd
df = pd.read_csv("data.csv")

# For custom utilities: use GhostImports
# ghostimports add-user ~/utils.py "*" --alias u -p
result = u.helper(data)
```

## FAQ

**Q: Does this slow down my notebooks?**  
A: No. Modules are only imported when first used, and after that it's direct access to the real module.

**Q: Can I use this in regular Python scripts?**  
A: GhostImports is designed for Jupyter notebooks. For scripts, use regular imports.

**Q: What if I want to see what's imported?**  
A: Ghostimports prints a message when each module loads: "ghostloader: imported 'pandas' as 'pd'"

**Q: Can I disable it temporarily?**  
A: Rename or remove `~/.ipython/profile_default/startup/00-ghostimports.py` and restart kernel.

**Q: Does it work with conda environments?**  
A: Yes! Install GhostImports in each conda environment where you want to use it.

**Q: Can I add the same function from multiple files?**  
A: Yes, if using direct imports. Each file maintains its own set of functions.

**Q: What happens if two direct imports have the same function name?**  
A: The last one loaded wins. Use aliases to avoid conflicts.
