"""
Pymavi - Python SDK for the Mavi Video AI Platform
"""

__version__ = "0.1.0"

from .client import MaviClient
from .exceptions import MaviError

__all__ = ["MaviClient", "MaviError"] 