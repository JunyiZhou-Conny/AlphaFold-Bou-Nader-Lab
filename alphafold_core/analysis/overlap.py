"""
Overlap analysis module for AlphaFold Core
Handles analysis of protein overlaps between different datasets
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Union
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

from ..config import config
from ..utils import setup_logging, load_dataframe, save_dataframe


class OverlapAnalyzer:
    """Analyzes overlaps between different protein datasets"""
    
    def __init__(self):
        self.logger = setup_logging()
    
    def calculate_overlap(self, set1: Set, set2: Set) -> Dict[str, Union[int, float]]:
        """Calculate overlap statistics between two sets"""
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return {
            'set1_size': len(set1),
            'set2_size': len(set2),
            'intersection_size': len(intersection),
            'union_size': len(union),
            'jaccard_similarity': len(intersection) / len(union) if union else 0,
            'overlap_percentage_set1': len(intersection) / len(set1) * 100 if set1 else 0,
            'overlap_percentage_set2': len(intersection) / len(set2) * 100 if set2 else 0
        }
    
    def analyze_multiple_datasets(self, datasets: Dict[str, Set], 
                                dataset_names: Optional[List[str]] = None) -> pd.DataFrame:
        """Analyze overlaps between multiple datasets"""
        if dataset_names is None:
            dataset_names = list(datasets.keys())
        
        results = []
        
        for i, name1 in enumerate(dataset_names):
            for j, name2 in enumerate(dataset_names[i+1:], i+1):
                overlap_stats = self.calculate_overlap(datasets[name1], datasets[name2])
                overlap_stats['dataset1'] = name1
                overlap_stats['dataset2'] = name2
                results.append(overlap_stats)
        
        return pd.DataFrame(results)
    
    def analyze_from_dataframes(self, dataframes: Dict[str, pd.DataFrame], 
                              id_columns: Dict[str, str]) -> pd.DataFrame:
        """Analyze overlaps from multiple dataframes"""
        datasets = {}
        
        for name, df in dataframes.items():
            id_col = id_columns.get(name, 'protein_id')
            if id_col in df.columns:
                datasets[name] = set(df[id_col].dropna().unique())
            else:
                self.logger.warning(f"Column {id_col} not found in dataset {name}")
        
        return self.analyze_multiple_datasets(datasets)
    
    def analyze_from_files(self, file_paths: Dict[str, str], 
                          id_columns: Dict[str, str]) -> pd.DataFrame:
        """Analyze overlaps from multiple files"""
        dataframes = {}
        
        for name, file_path in file_paths.items():
            df = load_dataframe(file_path)
            if df is not None:
                dataframes[name] = df
            else:
                self.logger.error(f"Failed to load file: {file_path}")
        
        return self.analyze_from_dataframes(dataframes, id_columns)
    
    def create_overlap_matrix(self, datasets: Dict[str, Set]) -> pd.DataFrame:
        """Create a matrix showing overlap percentages between all datasets"""
        dataset_names = list(datasets.keys())
        matrix = pd.DataFrame(index=dataset_names, columns=dataset_names)
        
        for i, name1 in enumerate(dataset_names):
            for j, name2 in enumerate(dataset_names):
                if i == j:
                    matrix.loc[name1, name2] = 100.0  # Self-overlap
                else:
                    overlap_stats = self.calculate_overlap(datasets[name1], datasets[name2])
                    matrix.loc[name1, name2] = overlap_stats['overlap_percentage_set1']
        
        return matrix
    
    def find_unique_proteins(self, datasets: Dict[str, Set], 
                           dataset_name: str) -> Set:
        """Find proteins unique to a specific dataset"""
        target_set = datasets[dataset_name]
        other_sets = [datasets[name] for name in datasets if name != dataset_name]
        
        if not other_sets:
            return target_set
        
        other_union = set().union(*other_sets)
        return target_set - other_union
    
    def find_common_proteins(self, datasets: Dict[str, Set]) -> Set:
        """Find proteins common to all datasets"""
        if not datasets:
            return set()
        
        return set.intersection(*datasets.values())
    
    def save_overlap_results(self, overlap_df: pd.DataFrame, 
                           output_prefix: str = "overlap_analysis") -> Dict[str, str]:
        """Save overlap analysis results to multiple formats"""
        output_files = {}
        
        # Save detailed results
        csv_file = f"{output_prefix}_detailed.csv"
        save_dataframe(overlap_df, csv_file)
        output_files['detailed_csv'] = csv_file
        
        # Save summary statistics
        summary_stats = {
            'total_comparisons': len(overlap_df),
            'average_jaccard': overlap_df['jaccard_similarity'].mean(),
            'max_jaccard': overlap_df['jaccard_similarity'].max(),
            'min_jaccard': overlap_df['jaccard_similarity'].min(),
            'average_overlap_percentage': overlap_df[['overlap_percentage_set1', 'overlap_percentage_set2']].mean().mean()
        }
        
        summary_file = f"{output_prefix}_summary.json"
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary_stats, f, indent=2)
        output_files['summary_json'] = summary_file
        
        self.logger.info(f"Overlap analysis results saved to {csv_file} and {summary_file}")
        return output_files
    
    def plot_overlap_heatmap(self, overlap_matrix: pd.DataFrame, 
                           output_file: str = "overlap_heatmap.png",
                           figsize: Tuple[int, int] = (10, 8)):
        """Create a heatmap visualization of overlaps"""
        plt.figure(figsize=figsize)
        
        sns.heatmap(overlap_matrix, annot=True, cmap='Blues', fmt='.1f',
                   cbar_kws={'label': 'Overlap Percentage (%)'})
        plt.title('Protein Overlap Analysis')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Overlap heatmap saved to {output_file}")
    
    def plot_venn_diagram(self, datasets: Dict[str, Set], 
                         output_file: str = "venn_diagram.png",
                         figsize: Tuple[int, int] = (10, 8)):
        """Create a Venn diagram for up to 3 datasets"""
        if len(datasets) > 3:
            self.logger.warning("Venn diagrams are limited to 3 datasets")
            return
        
        try:
            from matplotlib_venn import venn2, venn3
            
            plt.figure(figsize=figsize)
            
            if len(datasets) == 2:
                dataset_names = list(datasets.keys())
                venn2([datasets[dataset_names[0]], datasets[dataset_names[1]]], 
                     set_labels=dataset_names)
            elif len(datasets) == 3:
                dataset_names = list(datasets.keys())
                venn3([datasets[dataset_names[0]], datasets[dataset_names[1]], datasets[dataset_names[2]]], 
                     set_labels=dataset_names)
            
            plt.title('Protein Overlap Venn Diagram')
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Venn diagram saved to {output_file}")
            
        except ImportError:
            self.logger.error("matplotlib_venn not installed. Install with: pip install matplotlib-venn")
    
    def analyze_sequence_length_distribution(self, datasets: Dict[str, pd.DataFrame], 
                                          sequence_columns: Dict[str, str]) -> pd.DataFrame:
        """Analyze sequence length distributions across datasets"""
        length_stats = []
        
        for dataset_name, df in datasets.items():
            seq_col = sequence_columns.get(dataset_name, 'sequence')
            if seq_col in df.columns:
                lengths = df[seq_col].str.len().dropna()
                
                stats = {
                    'dataset': dataset_name,
                    'count': len(lengths),
                    'mean_length': lengths.mean(),
                    'median_length': lengths.median(),
                    'std_length': lengths.std(),
                    'min_length': lengths.min(),
                    'max_length': lengths.max(),
                    'q25': lengths.quantile(0.25),
                    'q75': lengths.quantile(0.75)
                }
                length_stats.append(stats)
        
        return pd.DataFrame(length_stats) 