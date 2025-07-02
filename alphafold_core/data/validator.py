"""
Data validator module for AlphaFold Core
Provides utilities for validating data quality and format
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import re
import os

from ..utils import setup_logging


class DataValidator:
    """Validates data quality and format"""
    
    def __init__(self):
        self.logger = setup_logging()
    
    def validate_protein_sequence(self, sequence: str) -> Dict[str, Any]:
        """Validate protein sequence format and content"""
        if not sequence:
            return {'valid': False, 'error': 'Empty sequence'}
        
        # Check for valid amino acid characters
        valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
        sequence_upper = sequence.upper()
        
        invalid_chars = set(sequence_upper) - valid_aa
        if invalid_chars:
            return {
                'valid': False, 
                'error': f'Invalid amino acids: {invalid_chars}',
                'invalid_chars': list(invalid_chars)
            }
        
        # Check sequence length
        if len(sequence) < 1:
            return {'valid': False, 'error': 'Sequence too short'}
        
        if len(sequence) > 10000:  # Arbitrary upper limit
            return {'valid': False, 'error': 'Sequence too long'}
        
        return {
            'valid': True,
            'length': len(sequence),
            'composition': {aa: sequence_upper.count(aa) for aa in valid_aa if aa in sequence_upper}
        }
    
    def validate_protein_id(self, protein_id: str) -> Dict[str, Any]:
        """Validate protein ID format"""
        if not protein_id:
            return {'valid': False, 'error': 'Empty protein ID'}
        
        # Common protein ID patterns
        patterns = {
            'uniprot': r'^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$',
            'pdb': r'^[0-9][A-Z0-9]{3}$',
            'refseq': r'^[A-Z]{2}_[0-9]{6}\.[0-9]+$',
            'genbank': r'^[A-Z]{1,2}[0-9]{5,6}$'
        }
        
        for db, pattern in patterns.items():
            if re.match(pattern, protein_id.upper()):
                return {'valid': True, 'database': db, 'id': protein_id}
        
        return {'valid': False, 'error': 'Unknown protein ID format'}
    
    def validate_dataframe(self, df: pd.DataFrame, 
                          required_columns: List[str] = None,
                          numeric_columns: List[str] = None) -> Dict[str, Any]:
        """Validate DataFrame structure and content"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check required columns
        if required_columns:
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                validation_result['valid'] = False
                validation_result['errors'].append(f'Missing required columns: {missing_columns}')
        
        # Check numeric columns
        if numeric_columns:
            for col in numeric_columns:
                if col in df.columns:
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        validation_result['warnings'].append(f'Column {col} is not numeric')
                    else:
                        # Check for NaN values
                        nan_count = df[col].isna().sum()
                        if nan_count > 0:
                            validation_result['warnings'].append(f'Column {col} has {nan_count} NaN values')
        
        # Basic statistics
        validation_result['stats'] = {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'duplicate_rows': df.duplicated().sum()
        }
        
        # Check for duplicate rows
        if validation_result['stats']['duplicate_rows'] > 0:
            validation_result['warnings'].append(f"Found {validation_result['stats']['duplicate_rows']} duplicate rows")
        
        return validation_result
    
    def validate_json_structure(self, data: Dict[str, Any], 
                              required_keys: List[str] = None,
                              schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate JSON structure and content"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required keys
        if required_keys:
            missing_keys = set(required_keys) - set(data.keys())
            if missing_keys:
                validation_result['valid'] = False
                validation_result['errors'].append(f'Missing required keys: {missing_keys}')
        
        # Check schema if provided
        if schema:
            for key, expected_type in schema.items():
                if key in data:
                    if not isinstance(data[key], expected_type):
                        validation_result['valid'] = False
                        validation_result['errors'].append(f'Key {key} should be {expected_type}, got {type(data[key])}')
        
        return validation_result
    
    def validate_alphafold_output(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AlphaFold output JSON structure"""
        required_keys = ['iptm', 'ptm', 'ranking_score']
        optional_keys = ['fraction_disordered', 'has_clash', 'num_recycles', 'chain_iptm', 'chain_ptm']
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        # Check required keys
        for key in required_keys:
            if key not in json_data:
                validation_result['valid'] = False
                validation_result['errors'].append(f'Missing required metric: {key}')
            else:
                value = json_data[key]
                if not isinstance(value, (int, float)):
                    validation_result['warnings'].append(f'Metric {key} is not numeric: {value}')
                else:
                    validation_result['metrics'][key] = value
        
        # Check optional keys
        for key in optional_keys:
            if key in json_data:
                validation_result['metrics'][key] = json_data[key]
        
        # Validate metric ranges
        if 'iptm' in validation_result['metrics']:
            iptm = validation_result['metrics']['iptm']
            if not (0 <= iptm <= 1):
                validation_result['warnings'].append(f'iPTM value {iptm} is outside expected range [0,1]')
        
        if 'ptm' in validation_result['metrics']:
            ptm = validation_result['metrics']['ptm']
            if not (0 <= ptm <= 1):
                validation_result['warnings'].append(f'pTM value {ptm} is outside expected range [0,1]')
        
        return validation_result
    
    def validate_file_paths(self, file_paths: List[str]) -> Dict[str, Any]:
        """Validate that file paths exist and are accessible"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'existing_files': [],
            'missing_files': []
        }
        
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                validation_result['existing_files'].append(str(path))
                
                # Check if file is readable
                if not path.is_file():
                    validation_result['warnings'].append(f'{path} exists but is not a file')
                elif not os.access(path, os.R_OK):
                    validation_result['warnings'].append(f'{path} exists but is not readable')
            else:
                validation_result['missing_files'].append(str(path))
                validation_result['valid'] = False
                validation_result['errors'].append(f'File not found: {path}')
        
        return validation_result
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a human-readable validation report"""
        report = []
        report.append("Data Validation Report")
        report.append("=" * 30)
        report.append("")
        
        if validation_results['valid']:
            report.append("✅ Validation PASSED")
        else:
            report.append("❌ Validation FAILED")
        
        if validation_results['errors']:
            report.append("\nErrors:")
            for error in validation_results['errors']:
                report.append(f"  - {error}")
        
        if validation_results['warnings']:
            report.append("\nWarnings:")
            for warning in validation_results['warnings']:
                report.append(f"  - {warning}")
        
        if 'stats' in validation_results:
            report.append("\nStatistics:")
            for key, value in validation_results['stats'].items():
                report.append(f"  - {key}: {value}")
        
        return "\n".join(report) 