"""
JSON processor module for AlphaFold Core
Provides utilities for processing and splitting JSON files
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

from ..utils import setup_logging


class JSONProcessor:
    """Handles JSON file processing and splitting operations"""
    
    def __init__(self):
        self.logger = setup_logging()
    
    def load_json(self, file_path: Path) -> Optional[List[Dict[str, Any]]]:
        """Load JSON file containing AlphaFold job data"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                self.logger.info(f"Loaded {len(data)} jobs from {file_path}")
                return data
            else:
                self.logger.error(f"Expected list of jobs, got {type(data)}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading JSON file {file_path}: {e}")
            return None
    
    def save_json(self, data: List[Dict[str, Any]], file_path: Path, 
                  indent: int = 2) -> bool:
        """Save JSON data to file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=indent)
            self.logger.info(f"Saved {len(data)} jobs to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving JSON file {file_path}: {e}")
            return False
    
    def split_json_by_count(self, input_file: Path, output_dir: Path, 
                           jobs_per_file: int = 30, 
                           prefix: str = "alphafold_batch") -> List[Path]:
        """
        Split a large JSON file into smaller files with specified number of jobs per file
        
        Args:
            input_file: Path to input JSON file
            output_dir: Directory to save split files
            jobs_per_file: Number of jobs per output file (default: 30 for AlphaFold3 daily limit)
            prefix: Prefix for output file names
            
        Returns:
            List of paths to created files
        """
        # Load the input JSON
        jobs = self.load_json(input_file)
        if not jobs:
            return []
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Calculate number of files needed
        total_jobs = len(jobs)
        num_files = math.ceil(total_jobs / jobs_per_file)
        
        self.logger.info(f"Splitting {total_jobs} jobs into {num_files} files "
                        f"with {jobs_per_file} jobs per file")
        
        created_files = []
        
        for i in range(num_files):
            start_idx = i * jobs_per_file
            end_idx = min((i + 1) * jobs_per_file, total_jobs)
            
            # Extract jobs for this batch
            batch_jobs = jobs[start_idx:end_idx]
            
            # Create output filename
            output_file = output_dir / f"{prefix}_{i+1:03d}_of_{num_files:03d}.json"
            
            # Save batch
            if self.save_json(batch_jobs, output_file):
                created_files.append(output_file)
                self.logger.info(f"Created batch {i+1}/{num_files}: {len(batch_jobs)} jobs")
        
        self.logger.info(f"Successfully created {len(created_files)} split files")
        return created_files
    
    def split_json_by_size(self, input_file: Path, output_dir: Path, 
                          max_size_mb: float = 10.0,
                          prefix: str = "alphafold_batch") -> List[Path]:
        """
        Split a large JSON file into smaller files based on file size
        
        Args:
            input_file: Path to input JSON file
            output_dir: Directory to save split files
            max_size_mb: Maximum size per file in MB
            prefix: Prefix for output file names
            
        Returns:
            List of paths to created files
        """
        # Load the input JSON
        jobs = self.load_json(input_file)
        if not jobs:
            return []
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        current_batch = []
        current_batch_size = 0
        batch_num = 1
        
        max_size_bytes = max_size_mb * 1024 * 1024
        
        for job in jobs:
            # Estimate size of current job
            job_size = len(json.dumps(job))
            
            # If adding this job would exceed size limit, save current batch
            if current_batch and (current_batch_size + job_size) > max_size_bytes:
                output_file = output_dir / f"{prefix}_{batch_num:03d}.json"
                if self.save_json(current_batch, output_file):
                    created_files.append(output_file)
                    self.logger.info(f"Created batch {batch_num}: {len(current_batch)} jobs, "
                                   f"{current_batch_size / 1024 / 1024:.2f} MB")
                
                # Start new batch
                current_batch = [job]
                current_batch_size = job_size
                batch_num += 1
            else:
                # Add to current batch
                current_batch.append(job)
                current_batch_size += job_size
        
        # Save final batch
        if current_batch:
            output_file = output_dir / f"{prefix}_{batch_num:03d}.json"
            if self.save_json(current_batch, output_file):
                created_files.append(output_file)
                self.logger.info(f"Created final batch {batch_num}: {len(current_batch)} jobs, "
                               f"{current_batch_size / 1024 / 1024:.2f} MB")
        
        self.logger.info(f"Successfully created {len(created_files)} split files")
        return created_files
    
    def validate_alphafold_json(self, jobs: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate that JSON data follows AlphaFold format
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for i, job in enumerate(jobs):
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
                        if not isinstance(seq, dict) or 'proteinChain' not in seq:
                            errors.append(f"Job {i}, sequence {j}: Invalid sequence structure")
                        elif 'sequence' not in seq['proteinChain']:
                            errors.append(f"Job {i}, sequence {j}: Missing 'sequence' field")
        
        return len(errors) == 0, errors
    
    def merge_json_files(self, input_files: List[Path], output_file: Path) -> bool:
        """
        Merge multiple JSON files into a single file
        
        Args:
            input_files: List of input JSON file paths
            output_file: Path to output merged file
            
        Returns:
            True if successful, False otherwise
        """
        all_jobs = []
        
        for input_file in input_files:
            jobs = self.load_json(input_file)
            if jobs:
                all_jobs.extend(jobs)
                self.logger.info(f"Added {len(jobs)} jobs from {input_file}")
        
        if all_jobs:
            return self.save_json(all_jobs, output_file)
        else:
            self.logger.error("No jobs found in input files")
            return False
    
    def get_json_stats(self, file_path: Path) -> Dict[str, Any]:
        """
        Get statistics about a JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with statistics
        """
        jobs = self.load_json(file_path)
        if not jobs:
            return {}
        
        # Calculate statistics
        total_jobs = len(jobs)
        total_sequences = sum(len(job.get('sequences', [])) for job in jobs)
        
        # Calculate file size
        file_size = file_path.stat().st_size
        file_size_mb = file_size / 1024 / 1024
        
        # Validate jobs
        is_valid, errors = self.validate_alphafold_json(jobs)
        
        return {
            'total_jobs': total_jobs,
            'total_sequences': total_sequences,
            'file_size_bytes': file_size,
            'file_size_mb': file_size_mb,
            'is_valid': is_valid,
            'validation_errors': len(errors),
            'errors': errors
        } 