#!/usr/bin/env python3
"""
Universal Top Hits Analyzer for AlphaFold Pipeline Results

This script provides a flexible, parameterized workflow for analyzing and comparing
multiple AlphaFold pipeline datasets with configurable filtering criteria and output formats.

Author: AI Assistant
Date: 2024
"""

import os
import sys
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime

# Add the parent directory to the path to import alphafold_core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alphafold_core.data.fetcher import DataFetcher
from alphafold_core.analysis.comparison import DatasetComparator
from alphafold_core.visualization.plots import PlotGenerator
from alphafold_core.utils import setup_logging, validate_file_path

class UniversalTopHitsAnalyzer:
    """
    Universal analyzer for processing multiple AlphaFold pipeline datasets
    with configurable filtering and analysis options.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the analyzer with configuration.
        
        Args:
            config_path (str): Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = setup_logging(self.config.get('logging', {}))
        self.fetcher = DataFetcher()
        self.comparator = DatasetComparator()
        self.plot_generator = PlotGenerator()
        
        # Create output directories
        self.output_dir = Path(self.config.get('output_dir', 'universal_results'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / 'csv').mkdir(exist_ok=True)
        (self.output_dir / 'excel').mkdir(exist_ok=True)
        (self.output_dir / 'plots').mkdir(exist_ok=True)
        (self.output_dir / 'reports').mkdir(exist_ok=True)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            raise ValueError(f"Failed to load config from {config_path}: {e}")
    
    def process_dataset(self, dataset_config: dict) -> pd.DataFrame:
        """
        Process a single dataset according to its configuration.
        
        Args:
            dataset_config (dict): Dataset-specific configuration
            
        Returns:
            pd.DataFrame: Processed dataset
        """
        dataset_name = dataset_config['name']
        file_path = dataset_config['file_path']
        
        self.logger.info(f"Processing dataset: {dataset_name}")
        
        # Load data
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        # Apply filters
        filters = dataset_config.get('filters', {})
        df = self._apply_filters(df, filters, dataset_name)
        
        # Extract target proteins
        target_col = dataset_config.get('target_protein_column', 'target_protein')
        if target_col not in df.columns:
            # Try to find target protein column
            possible_cols = [col for col in df.columns if 'target' in col.lower() or 'protein' in col.lower()]
            if possible_cols:
                target_col = possible_cols[0]
                self.logger.warning(f"Using {target_col} as target protein column for {dataset_name}")
            else:
                raise ValueError(f"Could not find target protein column in {dataset_name}")
        
        # Ensure target_protein column exists
        if target_col != 'target_protein':
            df = df.rename(columns={target_col: 'target_protein'})
        
        # Add dataset identifier
        df['source_dataset'] = dataset_name
        
        self.logger.info(f"Processed {dataset_name}: {len(df)} entries")
        return df
    
    def _apply_filters(self, df: pd.DataFrame, filters: dict, dataset_name: str) -> pd.DataFrame:
        """
        Apply filtering criteria to the dataset.
        
        Args:
            df (pd.DataFrame): Input dataframe
            filters (dict): Filter configuration
            dataset_name (str): Name of the dataset for logging
            
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        original_len = len(df)
        
        for filter_type, filter_config in filters.items():
            if filter_type == 'quality_thresholds':
                df = self._apply_quality_filters(df, filter_config, dataset_name)
            elif filter_type == 'column_filters':
                df = self._apply_column_filters(df, filter_config, dataset_name)
            elif filter_type == 'custom_filters':
                df = self._apply_custom_filters(df, filter_config, dataset_name)
        
        filtered_len = len(df)
        self.logger.info(f"Applied filters to {dataset_name}: {original_len} -> {filtered_len} entries")
        
        return df
    
    def _apply_quality_filters(self, df: pd.DataFrame, filters: dict, dataset_name: str) -> pd.DataFrame:
        """Apply quality-based filters."""
        for metric, threshold in filters.items():
            if metric in df.columns:
                if isinstance(threshold, dict):
                    min_val = threshold.get('min', -np.inf)
                    max_val = threshold.get('max', np.inf)
                    df = df[(df[metric] >= min_val) & (df[metric] <= max_val)]
                else:
                    # Assume minimum threshold
                    df = df[df[metric] >= threshold]
                self.logger.debug(f"Applied {metric} filter to {dataset_name}")
        
        return df
    
    def _apply_column_filters(self, df: pd.DataFrame, filters: dict, dataset_name: str) -> pd.DataFrame:
        """Apply column-based filters."""
        for column, conditions in filters.items():
            if column in df.columns:
                if isinstance(conditions, dict):
                    for operator, value in conditions.items():
                        if operator == 'equals':
                            df = df[df[column] == value]
                        elif operator == 'not_equals':
                            df = df[df[column] != value]
                        elif operator == 'contains':
                            df = df[df[column].astype(str).str.contains(str(value), na=False)]
                        elif operator == 'not_contains':
                            df = df[~df[column].astype(str).str.contains(str(value), na=False)]
                        elif operator == 'in':
                            df = df[df[column].isin(value)]
                        elif operator == 'not_in':
                            df = df[~df[column].isin(value)]
                else:
                    # Simple value filter
                    df = df[df[column] == conditions]
        
        return df
    
    def _apply_custom_filters(self, df: pd.DataFrame, filters: dict, dataset_name: str) -> pd.DataFrame:
        """Apply custom filter expressions."""
        for filter_name, expression in filters.items():
            try:
                # Evaluate the expression in the context of the dataframe
                mask = df.eval(expression)
                df = df[mask]
                self.logger.debug(f"Applied custom filter '{filter_name}' to {dataset_name}")
            except Exception as e:
                self.logger.warning(f"Failed to apply custom filter '{filter_name}' to {dataset_name}: {e}")
        
        return df
    
    def merge_datasets(self, datasets: Dict[str, pd.DataFrame], merge_strategy: str = 'outer') -> pd.DataFrame:
        """
        Merge multiple datasets into a single DataFrame with clean formatting.
        
        Args:
            datasets (dict): Dictionary of {dataset_name: DataFrame}
            merge_strategy (str): 'outer', 'inner', or 'left'
        
        Returns:
            pd.DataFrame: Merged dataset with clean column structure
        """
        if len(datasets) == 0:
            return pd.DataFrame()
        
        # Start with the first dataset
        dataset_names = list(datasets.keys())
        merged_df = datasets[dataset_names[0]].copy()
        
        # For multiple datasets, merge them one by one
        if len(datasets) > 1:
            for dataset_name in dataset_names[1:]:
                df = datasets[dataset_name].copy()
                
                # Merge on target_protein
                if merge_strategy == 'outer':
                    merged_df = pd.merge(merged_df, df, on='target_protein', how='outer', suffixes=('', f'_{dataset_name}'))
                elif merge_strategy == 'inner':
                    merged_df = pd.merge(merged_df, df, on='target_protein', how='inner', suffixes=('', f'_{dataset_name}'))
                else:  # left
                    merged_df = pd.merge(merged_df, df, on='target_protein', how='left', suffixes=('', f'_{dataset_name}'))
        
        # Clean up the merged DataFrame
        # Remove duplicate source_dataset columns if they exist
        source_cols = [col for col in merged_df.columns if col == 'source_dataset']
        if len(source_cols) > 1:
            # Keep the first one, drop the rest
            for col in source_cols[1:]:
                merged_df = merged_df.drop(columns=[col])
        
        # Reorder columns to put target_protein first, then source_dataset, then other columns
        cols = ['target_protein']
        if 'source_dataset' in merged_df.columns:
            cols.append('source_dataset')
        
        # Add remaining columns
        remaining_cols = [col for col in merged_df.columns if col not in cols]
        cols.extend(remaining_cols)
        
        merged_df = merged_df[cols]
        
        # Fill NaN values with appropriate defaults
        merged_df = merged_df.fillna('')
        
        return merged_df
    
    def run_analysis(self):
        """Run the complete analysis workflow."""
        self.logger.info("Starting universal top hits analysis")
        
        # Process all datasets
        datasets = {}
        for dataset_config in self.config['datasets']:
            try:
                df = self.process_dataset(dataset_config)
                datasets[dataset_config['name']] = df
            except Exception as e:
                self.logger.error(f"Failed to process dataset {dataset_config['name']}: {e}")
                continue
        
        if not datasets:
            self.logger.error("No datasets were successfully processed")
            return
        
        # Merge datasets
        merge_strategy = self.config.get('merge_strategy', 'outer')
        merged_df = self.merge_datasets(datasets, merge_strategy)
        
        # Save merged dataset
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as CSV
        csv_path = self.output_dir / 'csv' / f'merged_datasets_{timestamp}.csv'
        merged_df.to_csv(csv_path, index=False)
        self.logger.info(f"Saved merged dataset to {csv_path}")
        
        # Save as Excel
        excel_path = self.output_dir / 'excel' / f'merged_datasets_{timestamp}.xlsx'
        merged_df.to_excel(excel_path, index=False)
        self.logger.info(f"Saved merged dataset to {excel_path}")
        
        # Generate analysis reports
        self._generate_analysis_reports(datasets, merged_df, timestamp)
        
        # Generate visualizations
        self._generate_visualizations(datasets, merged_df, timestamp)
        
        self.logger.info("Analysis completed successfully")
    
    def _generate_analysis_reports(self, datasets: Dict[str, pd.DataFrame], merged_df: pd.DataFrame, timestamp: str):
        """Generate analysis reports."""
        report_path = self.output_dir / 'reports' / f'analysis_report_{timestamp}.txt'
        
        with open(report_path, 'w') as f:
            f.write("Universal Top Hits Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Dataset summaries
            f.write("Dataset Summaries:\n")
            f.write("-" * 20 + "\n")
            for name, df in datasets.items():
                f.write(f"{name}: {len(df)} entries\n")
            f.write(f"\nMerged dataset: {len(merged_df)} entries\n\n")
            
            # Overlap analysis
            if len(datasets) > 1:
                f.write("Overlap Analysis:\n")
                f.write("-" * 20 + "\n")
                
                # Get unique proteins from each dataset
                protein_sets = {}
                for name, df in datasets.items():
                    protein_sets[name] = set(df['target_protein'].dropna())
                
                # Calculate overlaps
                dataset_names = list(protein_sets.keys())
                for i, name1 in enumerate(dataset_names):
                    for j, name2 in enumerate(dataset_names[i+1:], i+1):
                        overlap = len(protein_sets[name1] & protein_sets[name2])
                        union = len(protein_sets[name1] | protein_sets[name2])
                        jaccard = overlap / union if union > 0 else 0
                        
                        f.write(f"{name1} vs {name2}:\n")
                        f.write(f"  Overlap: {overlap} proteins\n")
                        f.write(f"  Jaccard similarity: {jaccard:.3f}\n\n")
        
        self.logger.info(f"Generated analysis report: {report_path}")
    
    def _generate_visualizations(self, datasets: Dict[str, pd.DataFrame], merged_df: pd.DataFrame, timestamp: str):
        """Generate visualization plots."""
        plots_dir = self.output_dir / 'plots'
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Dataset size comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        dataset_names = list(datasets.keys())
        dataset_sizes = [len(df) for df in datasets.values()]
        
        bars = ax.bar(dataset_names, dataset_sizes)
        ax.set_title('Dataset Size Comparison', fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Entries')
        ax.set_xlabel('Dataset')
        
        # Add value labels on bars
        for bar, size in zip(bars, dataset_sizes):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01*max(dataset_sizes),
                   str(size), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(plots_dir / f'dataset_sizes_{timestamp}.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Overlap analysis (if multiple datasets)
        if len(datasets) > 1:
            try:
                # Create Venn diagram
                from matplotlib_venn import venn2, venn3
                
                protein_sets = {}
                for name, df in datasets.items():
                    protein_sets[name] = set(df['target_protein'].dropna())
                
                if len(datasets) == 2:
                    fig, ax = plt.subplots(figsize=(8, 8))
                    venn2([protein_sets[dataset_names[0]], protein_sets[dataset_names[1]]], 
                          set_labels=dataset_names, ax=ax)
                    ax.set_title('Protein Overlap Analysis', fontsize=14, fontweight='bold')
                    plt.tight_layout()
                    plt.savefig(plots_dir / f'venn_diagram_{timestamp}.png', dpi=300, bbox_inches='tight')
                    plt.close()
                
                elif len(datasets) == 3:
                    fig, ax = plt.subplots(figsize=(10, 10))
                    venn3([protein_sets[dataset_names[0]], protein_sets[dataset_names[1]], protein_sets[dataset_names[2]]], 
                          set_labels=dataset_names, ax=ax)
                    ax.set_title('Protein Overlap Analysis', fontsize=14, fontweight='bold')
                    plt.tight_layout()
                    plt.savefig(plots_dir / f'venn_diagram_{timestamp}.png', dpi=300, bbox_inches='tight')
                    plt.close()
                
            except ImportError:
                self.logger.warning("matplotlib_venn not available, skipping Venn diagram")
            except Exception as e:
                self.logger.warning(f"Failed to create Venn diagram: {e}")
        
        # 3. Quality metric distributions (if available)
        quality_metrics = ['iptm', 'ptm', 'ranking_score', 'pDockQ/mpDockQ']
        available_metrics = []
        
        for metric in quality_metrics:
            if any(metric in df.columns for df in datasets.values()):
                available_metrics.append(metric)
        
        if available_metrics:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            axes = axes.flatten()
            
            for i, metric in enumerate(available_metrics[:4]):
                ax = axes[i]
                
                for name, df in datasets.items():
                    if metric in df.columns:
                        # Remove non-numeric values
                        values = pd.to_numeric(df[metric], errors='coerce').dropna()
                        if len(values) > 0:
                            ax.hist(values, alpha=0.7, label=name, bins=20)
                
                ax.set_title(f'{metric} Distribution', fontweight='bold')
                ax.set_xlabel(metric)
                ax.set_ylabel('Frequency')
                ax.legend()
            
            # Hide empty subplots
            for i in range(len(available_metrics), 4):
                axes[i].set_visible(False)
            
            plt.tight_layout()
            plt.savefig(plots_dir / f'quality_distributions_{timestamp}.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        self.logger.info(f"Generated visualizations in {plots_dir}")


def create_example_config(output_path: str = 'example_config.yaml'):
    """Create an example configuration file."""
    config = {
        'output_dir': 'universal_results',
        'merge_strategy': 'outer',  # 'outer', 'inner', 'left'
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'datasets': [
            {
                'name': 'AF3',
                'file_path': 'path/to/af3_results.csv',
                'target_protein_column': 'target_protein',
                'filters': {
                    'quality_thresholds': {
                        'iptm': 0.5,
                        'ptm': 0.5,
                        'ranking_score': 0.7
                    },
                    'column_filters': {
                        'has_clash': {'equals': 0}
                    }
                }
            },
            {
                'name': 'AFP',
                'file_path': 'path/to/afp_results.csv',
                'target_protein_column': 'target_protein',
                'filters': {
                    'quality_thresholds': {
                        'iptm': 0.6,
                        'ptm': 0.6,
                        'pDockQ/mpDockQ': 0.2
                    }
                }
            },
            {
                'name': 'AFP_Jack',
                'file_path': 'path/to/afp_jack_results.csv',
                'target_protein_column': 'target_protein',
                'filters': {
                    'quality_thresholds': {
                        'iptm': 0.6,
                        'ptm': 0.6,
                        'pDockQ/mpDockQ': 0.2
                    }
                }
            }
        ]
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"Example configuration saved to {output_path}")


def main():
    """Main function to run the analyzer."""
    parser = argparse.ArgumentParser(description='Universal Top Hits Analyzer')
    parser.add_argument('config', help='Path to configuration YAML file')
    parser.add_argument('--create-example', action='store_true', 
                       help='Create an example configuration file')
    
    args = parser.parse_args()
    
    if args.create_example:
        create_example_config()
        return
    
    # Validate config file exists
    if not os.path.exists(args.config):
        print(f"Configuration file not found: {args.config}")
        print("Use --create-example to generate an example configuration file")
        return
    
    try:
        analyzer = UniversalTopHitsAnalyzer(args.config)
        analyzer.run_analysis()
        print(f"Analysis completed. Results saved to {analyzer.output_dir}")
    except Exception as e:
        print(f"Error running analysis: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 