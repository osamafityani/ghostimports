DATA_SCIENCE = {
    'pd': 'pandas',
    'np': 'numpy',
    'numpy': 'numpy',
    'sp': 'scipy',
    'scipy': 'scipy',
}


VISUALIZATION = {
    'plt': 'matplotlib.pyplot',
    'sns': 'seaborn',
    'seaborn': 'seaborn',
    'px': 'plotly.express',
    'go': 'plotly.graph_objects',
    'plotly': 'plotly',
}


MACHINE_LEARNING = {
    'tf': 'tensorflow',
    'tensorflow': 'tensorflow',
    'torch': 'torch',
    'pytorch': 'torch',
    'keras': 'keras',
    'sk': 'sklearn',
    'sklearn': 'sklearn',
}


DEEP_LEARNING = {
    'nn': 'torch.nn',
    'F': 'torch.nn.functional',
    'optim': 'torch.optim',
    'datasets': 'torchvision.datasets',
    'transforms': 'torchvision.transforms',
}


NLP = {
    'nltk': 'nltk',
    'spacy': 'spacy',
    'transformers': 'transformers',
    'tokenizers': 'tokenizers',
}


COMPUTER_VISION = {
    'cv2': 'cv2',
    'PIL': 'PIL',
    'Image': 'PIL.Image',
    'skimage': 'skimage',
}


WEB = {
    'requests': 'requests',
    'bs4': 'bs4',
    'BeautifulSoup': 'bs4.BeautifulSoup',
    'selenium': 'selenium',
    'flask': 'flask',
    'fastapi': 'fastapi',
}


DATA_HANDLING = {
    'json': 'json',
    'csv': 'csv',
    'pickle': 'pickle',
    'yaml': 'yaml',
    'pyarrow': 'pyarrow',
    'parquet': 'pyarrow.parquet',
}


DATABASE = {
    'sqlite3': 'sqlite3',
    'sqlalchemy': 'sqlalchemy',
    'pymongo': 'pymongo',
    'psycopg2': 'psycopg2',
}


TIME = {
    'datetime': 'datetime',
    'dt': 'datetime',
    'time': 'time',
    'arrow': 'arrow',
}


UTILITIES = {
    're': 're',
    'regex': 're',
    'os': 'os',
    'sys': 'sys',
    'pathlib': 'pathlib',
    'Path': 'pathlib.Path',
    'glob': 'glob',
    'shutil': 'shutil',
    'itertools': 'itertools',
    'collections': 'collections',
    'math': 'math',
    'random': 'random',
    'tqdm': 'tqdm',
}


STATISTICS = {
    'stats': 'scipy.stats',
    'statsmodels': 'statsmodels',
    'sm': 'statsmodels.api',
}


BUILTIN_MODULES = {}
for category in [
    DATA_SCIENCE, VISUALIZATION, MACHINE_LEARNING, DEEP_LEARNING,
    NLP, COMPUTER_VISION, WEB, DATA_HANDLING, DATABASE,
    TIME, UTILITIES, STATISTICS
]:
    BUILTIN_MODULES.update(category)


CATEGORIES = {
    'Data Science': DATA_SCIENCE,
    'Visualization': VISUALIZATION,
    'Machine Learning': MACHINE_LEARNING,
    'Deep Learning': DEEP_LEARNING,
    'NLP': NLP,
    'Computer Vision': COMPUTER_VISION,
    'Web & APIs': WEB,
    'Data Handling': DATA_HANDLING,
    'Database': DATABASE,
    'Time & Date': TIME,
    'Utilities': UTILITIES,
    'Statistics': STATISTICS,
}
