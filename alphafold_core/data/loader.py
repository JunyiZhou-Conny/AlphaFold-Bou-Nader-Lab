"""
Data loader module for AlphaFold Core
Provides utilities for loading data from various sources
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Union, Dict, Any
import logging

from ..utils import setup_logging, load_dataframe, save_dataframe


class DataLoader:
    """Handles loading data from various file formats and sources"""
    
    def __init__(self):
        self.logger = setup_logging()
    
    def load_csv(self, file_path: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Load data from CSV file"""
        return load_dataframe(file_path, "csv")
    
    def load_excel(self, file_path: Union[str, Path], 
                  sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Load data from Excel file"""
        try:
            if sheet_name:
                return pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                return pd.read_excel(file_path)
        except Exception as e:
            self.logger.error(f"Error loading Excel file {file_path}: {e}")
            return None
    
    def load_json(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Load data from JSON file"""
        from ..utils import safe_json_load
        return safe_json_load(file_path)
    
    def load_fasta(self, file_path: Union[str, Path]) -> Dict[str, str]:
        """Load sequences from FASTA file"""
        sequences = {}
        try:
            with open(file_path, 'r') as f:
                current_id = None
                current_sequence = []
                
                for line in f:
                    line = line.strip()
                    if line.startswith('>'):
                        # Save previous sequence
                        if current_id:
                            sequences[current_id] = ''.join(current_sequence)
                        
                        # Start new sequence
                        current_id = line[1:]  # Remove '>'
                        current_sequence = []
                    else:
                        current_sequence.append(line)
                
                # Save last sequence
                if current_id:
                    sequences[current_id] = ''.join(current_sequence)
            
            self.logger.info(f"Loaded {len(sequences)} sequences from {file_path}")
            return sequences
            
        except Exception as e:
            self.logger.error(f"Error loading FASTA file {file_path}: {e}")
            return {}
    
    def save_fasta(self, sequences: Dict[str, str], file_path: Union[str, Path]):
        """Save sequences to FASTA file"""
        try:
            with open(file_path, 'w') as f:
                for seq_id, sequence in sequences.items():
                    f.write(f">{seq_id}\n{sequence}\n")
            self.logger.info(f"Saved {len(sequences)} sequences to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving FASTA file {file_path}: {e}")
            return False
    
    def load_multiple_files(self, file_paths: Dict[str, str], 
                          file_types: Dict[str, str]) -> Dict[str, Any]:
        """Load multiple files of different types"""
        loaded_data = {}
        
        for name, file_path in file_paths.items():
            file_type = file_types.get(name, 'auto')
            
            if file_type == 'csv':
                loaded_data[name] = self.load_csv(file_path)
            elif file_type == 'excel':
                loaded_data[name] = self.load_excel(file_path)
            elif file_type == 'json':
                loaded_data[name] = self.load_json(file_path)
            elif file_type == 'fasta':
                loaded_data[name] = self.load_fasta(file_path)
            else:
                # Auto-detect type
                if file_path.endswith('.csv'):
                    loaded_data[name] = self.load_csv(file_path)
                elif file_path.endswith(('.xlsx', '.xls')):
                    loaded_data[name] = self.load_excel(file_path)
                elif file_path.endswith('.json'):
                    loaded_data[name] = self.load_json(file_path)
                elif file_path.endswith(('.fasta', '.fa')):
                    loaded_data[name] = self.load_fasta(file_path)
                else:
                    self.logger.warning(f"Unknown file type for {file_path}")
        
        return loaded_data 