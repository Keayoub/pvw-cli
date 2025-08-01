__version__ = "1.0.6"

# Import main client modules
from .client import *
from .cli import *

__all__ = [
    "__version__",
    # Client modules
    "PurviewClient",
    # CLI modules  
    "cli",
    "account",
    "entity", 
    "glossary",
    "lineage",
    "search",
    "scan",
    "types",
    "relationship",
    "management",
    "policystore",
    "insight",
    "share",
    "collections",
    "data_product",
]