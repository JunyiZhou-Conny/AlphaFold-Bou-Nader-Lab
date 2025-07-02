"""
Data module for AlphaFold Core
Handles data fetching, loading, processing, and management
"""

from .fetcher import ProteinSequenceFetcher, UniProtFetcher, SearchCriteria
from .processor import DataProcessor
from .json_processor import JSONProcessor
from .loader import DataLoader
from .validator import DataValidator

__all__ = [
    'ProteinSequenceFetcher',
    'UniProtFetcher',
    'SearchCriteria',
    'JSONProcessor',
    'DataProcessor',
    'DataLoader',
    'DataValidator'
] 