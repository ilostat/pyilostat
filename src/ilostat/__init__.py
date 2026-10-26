from importlib.metadata import version

from .cache import clean_cache, get_cache_dir
from .data import get_df
from .dictionary import get_dataset_dic, get_dic
from .metadata import get_metadata, get_toc
from .sdmx import get_sdmx

__version__ = version("ilostat")

__all__ = [
    "__version__",
    "get_dataset_dic",
    "get_df",
    "get_dic",
    "get_metadata",
    "get_toc",
    "clean_cache",
    "get_cache_dir", 
    "get_sdmx",
]