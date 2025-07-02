"""
Configuration management for AlphaFold Core
Centralizes all configuration settings and paths
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """Centralized configuration for AlphaFold operations"""
    
    # Base directories
    base_dir: Path = field(default_factory=lambda: Path.cwd())
    data_dir: Path = field(default_factory=lambda: Path.cwd() / "data")
    results_dir: Path = field(default_factory=lambda: Path.cwd() / "results")
    logs_dir: Path = field(default_factory=lambda: Path.cwd() / "logs")
    
    # AlphaFold specific paths
    alphafold_output_dir: Path = field(default_factory=lambda: Path.cwd() / "alphafold_output")
    json_files_dir: Path = field(default_factory=lambda: Path.cwd() / "json_files")
    
    # API and external services
    uniprot_base_url: str = "https://rest.uniprot.org"
    max_retries: int = 3
    request_timeout: int = 30
    rate_limit_delay: tuple = (0.5, 2.0)  # (min, max) seconds
    
    # Analysis parameters
    default_iptm_threshold: float = 0.6
    default_ptm_threshold: float = 0.5
    default_ranking_threshold: float = 0.8
    
    # File patterns
    json_patterns: Dict[str, str] = field(default_factory=lambda: {
        "summary_confidences": "*_summary_confidences_0.json",
        "prediction_results": "*_prediction_results.json",
        "metrics": "*_metrics.json"
    })
    
    # Output formats
    supported_formats: list = field(default_factory=lambda: ["csv", "json", "fasta", "xlsx"])
    
    def __post_init__(self):
        """Ensure all directories exist"""
        for dir_path in [self.data_dir, self.results_dir, self.logs_dir, 
                        self.alphafold_output_dir, self.json_files_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'Config':
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Convert string paths to Path objects
        for key, value in config_data.items():
            if isinstance(value, str) and key.endswith('_dir'):
                config_data[key] = Path(value)
        
        return cls(**config_data)
    
    def to_yaml(self, config_path: str):
        """Save configuration to YAML file"""
        config_dict = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Path):
                config_dict[key] = str(value)
            else:
                config_dict[key] = value
        
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def get_file_path(self, file_type: str, filename: str) -> Path:
        """Get standardized file path based on type"""
        path_mapping = {
            'data': self.data_dir,
            'results': self.results_dir,
            'logs': self.logs_dir,
            'alphafold': self.alphafold_output_dir,
            'json': self.json_files_dir
        }
        
        base_path = path_mapping.get(file_type, self.base_dir)
        return base_path / filename


# Global configuration instance
config = Config() 