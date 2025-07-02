"""
AlphaFold Core Package

A hierarchical, modular framework for AlphaFold-related bioinformatics tasks.
Organized for maximum reusability and maintainability.
"""

__version__ = "1.0.0"
__author__ = "Conny"

from .config import Config
from .utils import setup_logging

# Core modules
from . import data
from . import analysis
from . import visualization
from . import pipeline

__all__ = [
    'Config',
    'setup_logging',
    'data',
    'analysis', 
    'visualization',
    'pipeline'
] 