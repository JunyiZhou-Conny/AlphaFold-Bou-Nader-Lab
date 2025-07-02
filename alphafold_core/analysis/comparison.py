"""
Comparison analysis module for AlphaFold Core
Handles comparison of different AlphaFold datasets and results
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns

from ..config import config
from ..utils import setup_logging, load_dataframe, save_dataframe


class ComparisonAnalyzer:
    """Compares different AlphaFold datasets and results"""
    
    def __init__(self):
        self.logger = setup_logging()
    
    def compare_datasets(self, datasets: Dict[str, pd.DataFrame],
                        comparison_columns: List[str] = None) -> Dict[str, Any]:
        """Compare multiple datasets across specified columns"""
        if comparison_columns is None:
            # Use common numeric columns
            all_columns = set()
            for df in datasets.values():
                all_columns.update(df.select_dtypes(include=[np.number]).columns)
            comparison_columns = list(all_columns)
        
        comparison_results = {
            'datasets': list(datasets.keys()),
            'comparison_columns': comparison_columns,
            'summary_statistics': {},
            'correlations': {},
            'overlap_analysis': {}
        }
        
        # Calculate summary statistics for each dataset
        for dataset_name, df in datasets.items():
            comparison_results['summary_statistics'][dataset_name] = {}
            for column in comparison_columns:
                if column in df.columns:
                    data = df[column].dropna()
                    if len(data) > 0:
                        comparison_results['summary_statistics'][dataset_name][column] = {
                            'count': len(data),
                            'mean': data.mean(),
                            'median': data.median(),
                            'std': data.std(),
                            'min': data.min(),
                            'max': data.max()
                        }
        
        # Calculate correlations between datasets for each column
        for column in comparison_columns:
            column_data = {}
            for dataset_name, df in datasets.items():
                if column in df.columns:
                    column_data[dataset_name] = df[column].dropna()
            
            if len(column_data) > 1:
                # Create correlation matrix
                min_length = min(len(data) for data in column_data.values())
                if min_length > 0:
                    # Pad shorter series with NaN
                    padded_data = {}
                    for name, data in column_data.items():
                        if len(data) < min_length:
                            padded_data[name] = pd.concat([data, pd.Series([np.nan] * (min_length - len(data)))])
                        else:
                            padded_data[name] = data.head(min_length)
                    
                    correlation_df = pd.DataFrame(padded_data)
                    comparison_results['correlations'][column] = correlation_df.corr().to_dict()
        
        return comparison_results
    
    def compare_quality_metrics(self, datasets: Dict[str, pd.DataFrame],
                              quality_columns: List[str] = None) -> Dict[str, Any]:
        """Compare quality metrics across datasets"""
        if quality_columns is None:
            quality_columns = ['iptm', 'ptm', 'ranking_score']
        
        quality_comparison = {
            'datasets': list(datasets.keys()),
            'quality_metrics': quality_columns,
            'quality_summary': {},
            'threshold_analysis': {}
        }
        
        # Define quality thresholds
        thresholds = {
            'iptm': 0.6,
            'ptm': 0.5,
            'ranking_score': 0.8
        }
        
        for dataset_name, df in datasets.items():
            quality_comparison['quality_summary'][dataset_name] = {}
            quality_comparison['threshold_analysis'][dataset_name] = {}
            
            for metric in quality_columns:
                if metric in df.columns:
                    data = df[metric].dropna()
                    if len(data) > 0:
                        # Basic statistics
                        quality_comparison['quality_summary'][dataset_name][metric] = {
                            'count': len(data),
                            'mean': data.mean(),
                            'median': data.median(),
                            'std': data.std(),
                            'min': data.min(),
                            'max': data.max()
                        }
                        
                        # Threshold analysis
                        if metric in thresholds:
                            threshold = thresholds[metric]
                            above_threshold = (data >= threshold).sum()
                            quality_comparison['threshold_analysis'][dataset_name][metric] = {
                                'threshold': threshold,
                                'above_threshold_count': above_threshold,
                                'above_threshold_percentage': (above_threshold / len(data)) * 100
                            }
        
        return quality_comparison
    
    def compare_prediction_counts(self, datasets: Dict[str, pd.DataFrame],
                                id_columns: Dict[str, str] = None) -> Dict[str, Any]:
        """Compare prediction counts and overlaps between datasets"""
        if id_columns is None:
            id_columns = {name: 'job_name' for name in datasets.keys()}
        
        count_comparison = {
            'datasets': list(datasets.keys()),
            'prediction_counts': {},
            'overlaps': {},
            'unique_predictions': {}
        }
        
        # Count predictions in each dataset
        dataset_ids = {}
        for dataset_name, df in datasets.items():
            id_col = id_columns.get(dataset_name, 'job_name')
            if id_col in df.columns:
                ids = set(df[id_col].dropna().unique())
                dataset_ids[dataset_name] = ids
                count_comparison['prediction_counts'][dataset_name] = len(ids)
        
        # Calculate overlaps
        dataset_names = list(dataset_ids.keys())
        for i, name1 in enumerate(dataset_names):
            for j, name2 in enumerate(dataset_names[i+1:], i+1):
                overlap_key = f"{name1}_vs_{name2}"
                set1 = dataset_ids[name1]
                set2 = dataset_ids[name2]
                
                intersection = set1.intersection(set2)
                union = set1.union(set2)
                
                count_comparison['overlaps'][overlap_key] = {
                    'intersection_size': len(intersection),
                    'union_size': len(union),
                    'jaccard_similarity': len(intersection) / len(union) if union else 0,
                    'overlap_percentage_set1': len(intersection) / len(set1) * 100 if set1 else 0,
                    'overlap_percentage_set2': len(intersection) / len(set2) * 100 if set2 else 0
                }
        
        # Find unique predictions
        all_ids = set().union(*dataset_ids.values())
        for dataset_name, ids in dataset_ids.items():
            other_ids = set().union(*[dataset_ids[name] for name in dataset_names if name != dataset_name])
            unique_ids = ids - other_ids
            count_comparison['unique_predictions'][dataset_name] = {
                'unique_count': len(unique_ids),
                'unique_percentage': len(unique_ids) / len(ids) * 100 if ids else 0
            }
        
        return count_comparison
    
    def create_comparison_report(self, comparison_results: Dict[str, Any],
                               output_file: str = "comparison_report.txt") -> str:
        """Generate a comprehensive comparison report"""
        report = []
        report.append("Dataset Comparison Report")
        report.append("=" * 40)
        report.append("")
        
        # Dataset overview
        report.append(f"Datasets compared: {', '.join(comparison_results['datasets'])}")
        report.append("")
        
        # Summary statistics
        if 'summary_statistics' in comparison_results:
            report.append("Summary Statistics:")
            for dataset_name, stats in comparison_results['summary_statistics'].items():
                report.append(f"  {dataset_name}:")
                for column, column_stats in stats.items():
                    report.append(f"    {column}: mean={column_stats['mean']:.3f}, std={column_stats['std']:.3f}")
                report.append("")
        
        # Quality comparison
        if 'quality_summary' in comparison_results:
            report.append("Quality Metrics Comparison:")
            for dataset_name, quality_stats in comparison_results['quality_summary'].items():
                report.append(f"  {dataset_name}:")
                for metric, stats in quality_stats.items():
                    report.append(f"    {metric}: mean={stats['mean']:.3f}, median={stats['median']:.3f}")
                report.append("")
        
        # Prediction counts
        if 'prediction_counts' in comparison_results:
            report.append("Prediction Counts:")
            for dataset_name, count in comparison_results['prediction_counts'].items():
                report.append(f"  {dataset_name}: {count} predictions")
            report.append("")
        
        # Overlaps
        if 'overlaps' in comparison_results:
            report.append("Dataset Overlaps:")
            for overlap_key, overlap_stats in comparison_results['overlaps'].items():
                report.append(f"  {overlap_key}:")
                report.append(f"    - Intersection: {overlap_stats['intersection_size']}")
                report.append(f"    - Jaccard similarity: {overlap_stats['jaccard_similarity']:.3f}")
                report.append("")
        
        # Save report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        self.logger.info(f"Comparison report saved to {output_file}")
        return '\n'.join(report)
    
    def plot_comparison_summary(self, comparison_results: Dict[str, Any],
                              output_file: str = "comparison_summary.png",
                              figsize: Tuple[int, int] = (15, 12)):
        """Create comprehensive comparison visualization"""
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        # Plot 1: Prediction counts
        if 'prediction_counts' in comparison_results:
            datasets = list(comparison_results['prediction_counts'].keys())
            counts = list(comparison_results['prediction_counts'].values())
            
            axes[0].bar(datasets, counts)
            axes[0].set_title('Prediction Counts by Dataset')
            axes[0].set_ylabel('Number of Predictions')
            axes[0].tick_params(axis='x', rotation=45)
        
        # Plot 2: Quality metrics comparison
        if 'quality_summary' in comparison_results:
            quality_data = []
            for dataset_name, quality_stats in comparison_results['quality_summary'].items():
                for metric, stats in quality_stats.items():
                    quality_data.append({
                        'dataset': dataset_name,
                        'metric': metric,
                        'mean': stats['mean']
                    })
            
            if quality_data:
                quality_df = pd.DataFrame(quality_data)
                pivot_df = quality_df.pivot(index='dataset', columns='metric', values='mean')
                pivot_df.plot(kind='bar', ax=axes[1])
                axes[1].set_title('Mean Quality Metrics by Dataset')
                axes[1].set_ylabel('Mean Value')
                axes[1].legend(title='Metric')
                axes[1].tick_params(axis='x', rotation=45)
        
        # Plot 3: Overlap heatmap
        if 'overlaps' in comparison_results:
            # Create overlap matrix
            datasets = comparison_results['datasets']
            overlap_matrix = pd.DataFrame(index=datasets, columns=datasets)
            
            for i, dataset1 in enumerate(datasets):
                for j, dataset2 in enumerate(datasets):
                    if i == j:
                        overlap_matrix.loc[dataset1, dataset2] = 1.0
                    else:
                        overlap_key = f"{dataset1}_vs_{dataset2}"
                        if overlap_key in comparison_results['overlaps']:
                            overlap_matrix.loc[dataset1, dataset2] = comparison_results['overlaps'][overlap_key]['jaccard_similarity']
                        else:
                            overlap_key = f"{dataset2}_vs_{dataset1}"
                            if overlap_key in comparison_results['overlaps']:
                                overlap_matrix.loc[dataset1, dataset2] = comparison_results['overlaps'][overlap_key]['jaccard_similarity']
                            else:
                                overlap_matrix.loc[dataset1, dataset2] = 0.0
            
            sns.heatmap(overlap_matrix, annot=True, cmap='Blues', ax=axes[2])
            axes[2].set_title('Dataset Overlap Matrix')
        
        # Plot 4: Unique predictions
        if 'unique_predictions' in comparison_results:
            datasets = list(comparison_results['unique_predictions'].keys())
            unique_counts = [comparison_results['unique_predictions'][name]['unique_count'] for name in datasets]
            unique_percentages = [comparison_results['unique_predictions'][name]['unique_percentage'] for name in datasets]
            
            x = np.arange(len(datasets))
            width = 0.35
            
            ax1 = axes[3]
            ax2 = ax1.twinx()
            
            bars1 = ax1.bar(x - width/2, unique_counts, width, label='Unique Count', alpha=0.7)
            bars2 = ax2.bar(x + width/2, unique_percentages, width, label='Unique %', alpha=0.7, color='orange')
            
            ax1.set_xlabel('Dataset')
            ax1.set_ylabel('Unique Count', color='blue')
            ax2.set_ylabel('Unique Percentage (%)', color='orange')
            ax1.set_title('Unique Predictions by Dataset')
            ax1.set_xticks(x)
            ax1.set_xticklabels(datasets, rotation=45)
            
            # Add legends
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Comparison summary plot saved to {output_file}")
    
    def compare_sequence_lengths(self, datasets: Dict[str, pd.DataFrame],
                               sequence_columns: Dict[str, str] = None) -> Dict[str, Any]:
        """Compare sequence length distributions across datasets"""
        if sequence_columns is None:
            sequence_columns = {name: 'sequence' for name in datasets.keys()}
        
        length_comparison = {
            'datasets': list(datasets.keys()),
            'length_statistics': {},
            'length_distributions': {}
        }
        
        for dataset_name, df in datasets.items():
            seq_col = sequence_columns.get(dataset_name, 'sequence')
            if seq_col in df.columns:
                lengths = df[seq_col].str.len().dropna()
                
                if len(lengths) > 0:
                    length_comparison['length_statistics'][dataset_name] = {
                        'count': len(lengths),
                        'mean': lengths.mean(),
                        'median': lengths.median(),
                        'std': lengths.std(),
                        'min': lengths.min(),
                        'max': lengths.max(),
                        'q25': lengths.quantile(0.25),
                        'q75': lengths.quantile(0.75)
                    }
                    
                    length_comparison['length_distributions'][dataset_name] = lengths.tolist()
        
        return length_comparison
    
    def plot_sequence_length_comparison(self, length_comparison: Dict[str, Any],
                                      output_file: str = "sequence_length_comparison.png",
                                      figsize: Tuple[int, int] = (12, 8)):
        """Create sequence length comparison visualization"""
        if not length_comparison['length_distributions']:
            self.logger.warning("No sequence length data available for plotting")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Box plot
        length_data = []
        labels = []
        for dataset_name, lengths in length_comparison['length_distributions'].items():
            length_data.append(lengths)
            labels.append(dataset_name)
        
        ax1.boxplot(length_data, labels=labels)
        ax1.set_title('Sequence Length Distribution')
        ax1.set_ylabel('Sequence Length')
        ax1.tick_params(axis='x', rotation=45)
        
        # Histogram
        for dataset_name, lengths in length_comparison['length_distributions'].items():
            ax2.hist(lengths, bins=30, alpha=0.7, label=dataset_name, edgecolor='black')
        
        ax2.set_title('Sequence Length Histogram')
        ax2.set_xlabel('Sequence Length')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Sequence length comparison plot saved to {output_file}") 