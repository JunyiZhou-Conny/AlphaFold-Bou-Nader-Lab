"""
Utility functions for AlphaFold Core
Common functions used across multiple modules
"""

import logging
import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import time
import random
from functools import wraps


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup standardized logging for the application"""
    logger = logging.getLogger("alphafold_core")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds to execute")
        return result
    return wrapper


def safe_json_load(file_path: Union[str, Path]) -> Optional[Dict]:
    """Safely load JSON file with error handling"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return None


def safe_json_save(data: Dict, file_path: Union[str, Path], indent: int = 2):
    """Safely save data to JSON file with error handling"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {e}")
        return False


def find_json_files(directory: Union[str, Path], pattern: str = "*.json") -> List[Path]:
    """Find all JSON files matching pattern in directory"""
    directory = Path(directory)
    return list(directory.rglob(pattern))


def parse_job_name(file_path: Union[str, Path]) -> str:
    """Extract job name from AlphaFold output filename"""
    file_path = Path(file_path)
    stem = file_path.stem
    
    # Remove common suffixes
    suffixes_to_remove = [
        '_summary_confidences_0',
        '_prediction_results',
        '_metrics'
    ]
    
    for suffix in suffixes_to_remove:
        if stem.endswith(suffix):
            stem = stem[:-len(suffix)]
            break
    
    # Replace pipe character with dash for AlphaFold3 compatibility
    stem = stem.replace('|', '-')
    
    return stem


def rate_limited_request(func):
    """Decorator to add rate limiting to API requests"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Add random delay between requests
        time.sleep(random.uniform(0.5, 2.0))
        return func(*args, **kwargs)
    return wrapper


def validate_file_format(file_path: Union[str, Path], expected_formats: List[str]) -> bool:
    """Validate if file has expected format"""
    file_path = Path(file_path)
    return file_path.suffix.lower().lstrip('.') in expected_formats


def create_backup(file_path: Union[str, Path]) -> Path:
    """Create a backup of a file with timestamp"""
    file_path = Path(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    
    if file_path.exists():
        import shutil
        shutil.copy2(file_path, backup_path)
        logging.info(f"Created backup: {backup_path}")
    
    return backup_path


def merge_dataframes(df_list: List[pd.DataFrame], merge_on: str = None) -> pd.DataFrame:
    """Merge multiple dataframes with error handling"""
    if not df_list:
        return pd.DataFrame()
    
    if len(df_list) == 1:
        return df_list[0]
    
    try:
        if merge_on:
            result = df_list[0]
            for df in df_list[1:]:
                result = result.merge(df, on=merge_on, how='outer')
        else:
            result = pd.concat(df_list, ignore_index=True)
        
        return result
    except Exception as e:
        logging.error(f"Error merging dataframes: {e}")
        return pd.DataFrame()


def save_dataframe(df: pd.DataFrame, file_path: Union[str, Path], 
                  format: str = "csv", **kwargs):
    """Save dataframe in various formats with error handling"""
    file_path = Path(file_path)
    
    try:
        if format.lower() == "csv":
            df.to_csv(file_path, index=False, **kwargs)
        elif format.lower() == "json":
            df.to_json(file_path, orient='records', indent=2, **kwargs)
        elif format.lower() == "xlsx":
            df.to_excel(file_path, index=False, **kwargs)
        elif format.lower() == "parquet":
            df.to_parquet(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logging.info(f"Data saved to {file_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving data to {file_path}: {e}")
        return False


def load_dataframe(file_path: Union[str, Path], format: str = None) -> Optional[pd.DataFrame]:
    """Load dataframe from various formats with error handling"""
    file_path = Path(file_path)
    
    if format is None:
        format = file_path.suffix.lower().lstrip('.')
    
    try:
        if format == "csv":
            return pd.read_csv(file_path)
        elif format == "json":
            return pd.read_json(file_path)
        elif format == "xlsx":
            return pd.read_excel(file_path)
        elif format == "parquet":
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return None


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_nested_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """Flatten a nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_nested_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# ============================================================================
# NEW FUNCTIONS ADDED FOR MISSING FUNCTIONALITY
# ============================================================================

def validate_alphafold_json_structure(data: Union[Dict, List[Dict]]) -> Tuple[bool, List[str]]:
    """
    Validate AlphaFold JSON structure for compatibility
    
    Args:
        data: JSON data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if isinstance(data, list):
        jobs = data
    elif isinstance(data, dict):
        jobs = [data]
    else:
        return False, ["Data must be a dictionary or list of dictionaries"]
    
    for i, job in enumerate(jobs):
        if not isinstance(job, dict):
            errors.append(f"Job {i}: Must be a dictionary")
            continue
        
        # Check required fields
        required_fields = ['name', 'sequences', 'dialect', 'version']
        for field in required_fields:
            if field not in job:
                errors.append(f"Job {i}: Missing required field '{field}'")
        
        # Check sequences structure
        if 'sequences' in job:
            if not isinstance(job['sequences'], list):
                errors.append(f"Job {i}: 'sequences' must be a list")
            else:
                for j, seq in enumerate(job['sequences']):
                    if not isinstance(seq, dict):
                        errors.append(f"Job {i}, sequence {j}: Must be a dictionary")
                    elif 'proteinChain' not in seq:
                        errors.append(f"Job {i}, sequence {j}: Missing 'proteinChain' field")
                    elif 'sequence' not in seq['proteinChain']:
                        errors.append(f"Job {i}, sequence {j}: Missing 'sequence' field")
    
    return len(errors) == 0, errors


def test_file_structure(file_path: Union[str, Path], file_type: str = "auto") -> Dict[str, Any]:
    """
    Test the structure of various file types
    
    Args:
        file_path: Path to the file to test
        file_type: Type of file ('json', 'csv', 'fasta', 'auto')
        
    Returns:
        Dictionary with test results
    """
    file_path = Path(file_path)
    results = {
        'file_path': str(file_path),
        'file_type': file_type,
        'exists': file_path.exists(),
        'size_bytes': file_path.stat().st_size if file_path.exists() else 0,
        'is_valid': False,
        'errors': [],
        'warnings': [],
        'structure_info': {}
    }
    
    if not file_path.exists():
        results['errors'].append("File does not exist")
        return results
    
    # Auto-detect file type
    if file_type == "auto":
        if file_path.suffix.lower() == '.json':
            file_type = 'json'
        elif file_path.suffix.lower() == '.csv':
            file_type = 'csv'
        elif file_path.suffix.lower() in ['.fasta', '.fa', '.fas']:
            file_type = 'fasta'
        else:
            results['errors'].append(f"Unknown file type: {file_path.suffix}")
            return results
    
    try:
        if file_type == 'json':
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                results['structure_info']['type'] = 'list'
                results['structure_info']['count'] = len(data)
                if data:
                    results['structure_info']['sample_keys'] = list(data[0].keys()) if isinstance(data[0], dict) else []
            elif isinstance(data, dict):
                results['structure_info']['type'] = 'dict'
                results['structure_info']['keys'] = list(data.keys())
            else:
                results['errors'].append("JSON data must be a list or dictionary")
                return results
            
            # Validate AlphaFold structure if it looks like AlphaFold data
            if isinstance(data, list) and data and 'sequences' in data[0]:
                is_valid, validation_errors = validate_alphafold_json_structure(data)
                results['is_valid'] = is_valid
                results['errors'].extend(validation_errors)
            else:
                results['is_valid'] = True
        
        elif file_type == 'csv':
            df = pd.read_csv(file_path)
            results['structure_info']['rows'] = len(df)
            results['structure_info']['columns'] = list(df.columns)
            results['structure_info']['dtypes'] = df.dtypes.to_dict()
            results['is_valid'] = True
        
        elif file_type == 'fasta':
            sequence_count = 0
            total_length = 0
            sequence_lengths = []
            
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('>'):
                        sequence_count += 1
                    elif line and not line.startswith('>'):
                        total_length += len(line)
                        sequence_lengths.append(len(line))
            
            results['structure_info']['sequence_count'] = sequence_count
            results['structure_info']['total_length'] = total_length
            results['structure_info']['avg_length'] = total_length / sequence_count if sequence_count > 0 else 0
            results['structure_info']['min_length'] = min(sequence_lengths) if sequence_lengths else 0
            results['structure_info']['max_length'] = max(sequence_lengths) if sequence_lengths else 0
            results['is_valid'] = sequence_count > 0
        
        else:
            results['errors'].append(f"Unsupported file type: {file_type}")
    
    except Exception as e:
        results['errors'].append(f"Error testing file structure: {e}")
    
    return results


def rename_files_by_pattern(directory: Union[str, Path], 
                           pattern: str, 
                           replacement: str,
                           file_extension: str = None) -> List[Path]:
    """
    Rename files in a directory based on a regex pattern
    
    Args:
        directory: Directory containing files to rename
        pattern: Regex pattern to match
        replacement: Replacement string
        file_extension: Optional file extension filter
        
    Returns:
        List of renamed file paths
    """
    import re
    directory = Path(directory)
    renamed_files = []
    
    if not directory.exists():
        logging.error(f"Directory does not exist: {directory}")
        return renamed_files
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            if file_extension and not file_path.suffix.lower() == file_extension.lower():
                continue
            
            new_name = re.sub(pattern, replacement, file_path.name)
            if new_name != file_path.name:
                new_path = file_path.parent / new_name
                try:
                    file_path.rename(new_path)
                    renamed_files.append(new_path)
                    logging.info(f"Renamed: {file_path.name} -> {new_name}")
                except Exception as e:
                    logging.error(f"Error renaming {file_path.name}: {e}")
    
    return renamed_files


def organize_files_by_type(directory: Union[str, Path], 
                          create_subdirs: bool = True) -> Dict[str, List[Path]]:
    """
    Organize files in a directory by their type
    
    Args:
        directory: Directory to organize
        create_subdirs: Whether to create subdirectories for each file type
        
    Returns:
        Dictionary mapping file types to lists of file paths
    """
    directory = Path(directory)
    file_types = {}
    
    if not directory.exists():
        logging.error(f"Directory does not exist: {directory}")
        return file_types
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_type = file_path.suffix.lower().lstrip('.')
            if not file_type:
                file_type = 'no_extension'
            
            if file_type not in file_types:
                file_types[file_type] = []
            
            file_types[file_type].append(file_path)
    
    if create_subdirs:
        for file_type, files in file_types.items():
            if len(files) > 1:  # Only create subdir if multiple files
                subdir = directory / file_type
                subdir.mkdir(exist_ok=True)
                
                for file_path in files:
                    try:
                        new_path = subdir / file_path.name
                        file_path.rename(new_path)
                        logging.info(f"Moved {file_path.name} to {subdir}")
                    except Exception as e:
                        logging.error(f"Error moving {file_path.name}: {e}")
    
    return file_types


def count_sequence_lengths(fasta_file: Union[str, Path]) -> Dict[str, int]:
    """
    Count the length of each sequence in a FASTA file
    
    Args:
        fasta_file: Path to the FASTA file
        
    Returns:
        Dictionary with sequence IDs as keys and sequence lengths as values
    """
    fasta_file = Path(fasta_file)
    sequence_lengths = {}
    current_id = None
    current_sequence = ""
    
    try:
        with open(fasta_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    # If we have a previous sequence, save its length
                    if current_id:
                        sequence_lengths[current_id] = len(current_sequence)
                    # Start new sequence
                    current_id = line[1:]  # Remove the '>' character
                    current_sequence = ""
                else:
                    # Add to current sequence
                    current_sequence += line
        
        # Don't forget to add the last sequence
        if current_id:
            sequence_lengths[current_id] = len(current_sequence)
        
        logging.info(f"Counted lengths for {len(sequence_lengths)} sequences")
        return sequence_lengths
    
    except Exception as e:
        logging.error(f"Error counting sequence lengths: {e}")
        return {}


def extract_overlapping_proteins(excel_file: Union[str, Path], 
                                sheet_name: str = 'All Three Papers',
                                output_file: Union[str, Path] = "overlapping_proteins.fasta") -> bool:
    """
    Extract overlapping proteins from Excel file and save to FASTA
    
    Args:
        excel_file: Path to Excel file with protein data
        sheet_name: Name of the sheet containing overlapping proteins
        output_file: Path to output FASTA file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        if 'Protein Accession' not in df.columns or 'Amino Acid Sequence' not in df.columns:
            logging.error("Excel file must contain 'Protein Accession' and 'Amino Acid Sequence' columns")
            return False
        
        with open(output_file, 'w') as f:
            for _, row in df.iterrows():
                accession = row['Protein Accession']
                sequence = row['Amino Acid Sequence']
                f.write(f">{accession}\n")
                f.write(f"{sequence}\n")
        
        logging.info(f"Extracted {len(df)} overlapping proteins to {output_file}")
        return True
    
    except Exception as e:
        logging.error(f"Error extracting overlapping proteins: {e}")
        return False 