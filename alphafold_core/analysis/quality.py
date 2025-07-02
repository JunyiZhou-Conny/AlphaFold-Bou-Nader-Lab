"""
Quality analysis module for AlphaFold Core
Handles quality assessment and filtering of AlphaFold predictions
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns

from ..config import config
from ..utils import setup_logging, load_dataframe, save_dataframe


class QualityAnalyzer:
    """Analyzes quality metrics of AlphaFold predictions"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.default_thresholds = {
            'iptm': 0.6,
            'ptm': 0.5,
            'ranking_score': 0.8
        }
    
    def assess_prediction_quality(self, metrics_df: pd.DataFrame,
                                thresholds: Dict[str, float] = None) -> Dict[str, Any]:
        """Assess the quality of AlphaFold predictions"""
        if thresholds is None:
            thresholds = self.default_thresholds
        
        assessment = {
            'total_predictions': len(metrics_df),
            'quality_breakdown': {},
            'thresholds_used': thresholds,
            'summary_stats': {}
        }
        
        # Calculate quality breakdown
        for metric, threshold in thresholds.items():
            if metric in metrics_df.columns:
                high_quality = metrics_df[metric] >= threshold
                assessment['quality_breakdown'][metric] = {
                    'high_quality_count': high_quality.sum(),
                    'high_quality_percentage': (high_quality.sum() / len(metrics_df)) * 100,
                    'threshold': threshold,
                    'mean_value': metrics_df[metric].mean(),
                    'median_value': metrics_df[metric].median(),
                    'std_value': metrics_df[metric].std()
                }
        
        # Calculate overall quality score
        quality_scores = []
        for metric, threshold in thresholds.items():
            if metric in metrics_df.columns:
                score = (metrics_df[metric] >= threshold).astype(int)
                quality_scores.append(score)
        
        if quality_scores:
            overall_quality = pd.concat(quality_scores, axis=1).mean(axis=1)
            assessment['overall_quality'] = {
                'mean_score': overall_quality.mean(),
                'high_quality_count': (overall_quality >= 0.5).sum(),
                'high_quality_percentage': (overall_quality >= 0.5).mean() * 100
            }
        
        # Summary statistics
        numeric_columns = metrics_df.select_dtypes(include=[np.number]).columns
        assessment['summary_stats'] = {
            'numeric_columns': list(numeric_columns),
            'missing_values': metrics_df.isnull().sum().to_dict(),
            'correlations': metrics_df[numeric_columns].corr().to_dict() if len(numeric_columns) > 1 else {}
        }
        
        return assessment
    
    def filter_high_quality_predictions(self, metrics_df: pd.DataFrame,
                                      thresholds: Dict[str, float] = None,
                                      filter_type: str = 'all') -> pd.DataFrame:
        """Filter predictions based on quality thresholds"""
        if thresholds is None:
            thresholds = self.default_thresholds
        
        filtered_df = metrics_df.copy()
        
        if filter_type == 'all':
            # All thresholds must be met
            for metric, threshold in thresholds.items():
                if metric in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[metric] >= threshold]
        
        elif filter_type == 'any':
            # At least one threshold must be met
            mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
            for metric, threshold in thresholds.items():
                if metric in filtered_df.columns:
                    mask |= filtered_df[metric] >= threshold
            filtered_df = filtered_df[mask]
        
        elif filter_type == 'majority':
            # Majority of thresholds must be met
            quality_scores = []
            for metric, threshold in thresholds.items():
                if metric in filtered_df.columns:
                    score = (filtered_df[metric] >= threshold).astype(int)
                    quality_scores.append(score)
            
            if quality_scores:
                overall_quality = pd.concat(quality_scores, axis=1).mean(axis=1)
                filtered_df = filtered_df[overall_quality >= 0.5]
        
        self.logger.info(f"Filtered from {len(metrics_df)} to {len(filtered_df)} predictions")
        return filtered_df
    
    def identify_outliers(self, metrics_df: pd.DataFrame,
                         columns: List[str] = None,
                         method: str = 'iqr') -> Dict[str, List[int]]:
        """Identify outliers in quality metrics"""
        if columns is None:
            columns = ['iptm', 'ptm', 'ranking_score']
        
        outliers = {}
        
        for column in columns:
            if column not in metrics_df.columns:
                continue
            
            data = metrics_df[column].dropna()
            
            if method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_indices = data[(data < lower_bound) | (data > upper_bound)].index
                outliers[column] = outlier_indices.tolist()
            
            elif method == 'zscore':
                z_scores = np.abs((data - data.mean()) / data.std())
                outlier_indices = data[z_scores > 3].index
                outliers[column] = outlier_indices.tolist()
        
        return outliers
    
    def generate_quality_report(self, metrics_df: pd.DataFrame,
                              output_file: str = "quality_report.txt") -> str:
        """Generate a comprehensive quality report"""
        assessment = self.assess_prediction_quality(metrics_df)
        
        report = []
        report.append("AlphaFold Quality Assessment Report")
        report.append("=" * 50)
        report.append("")
        
        # Overall statistics
        report.append(f"Total Predictions: {assessment['total_predictions']}")
        report.append("")
        
        # Quality breakdown by metric
        report.append("Quality Breakdown by Metric:")
        for metric, stats in assessment['quality_breakdown'].items():
            report.append(f"  {metric.upper()}:")
            report.append(f"    - High Quality: {stats['high_quality_count']} ({stats['high_quality_percentage']:.1f}%)")
            report.append(f"    - Threshold: {stats['threshold']}")
            report.append(f"    - Mean: {stats['mean_value']:.3f}")
            report.append(f"    - Median: {stats['median_value']:.3f}")
            report.append(f"    - Std: {stats['std_value']:.3f}")
            report.append("")
        
        # Overall quality
        if 'overall_quality' in assessment:
            report.append("Overall Quality Score:")
            report.append(f"  - Mean Score: {assessment['overall_quality']['mean_score']:.3f}")
            report.append(f"  - High Quality: {assessment['overall_quality']['high_quality_count']} ({assessment['overall_quality']['high_quality_percentage']:.1f}%)")
            report.append("")
        
        # Missing values
        if assessment['summary_stats']['missing_values']:
            report.append("Missing Values:")
            for column, count in assessment['summary_stats']['missing_values'].items():
                if count > 0:
                    report.append(f"  - {column}: {count}")
            report.append("")
        
        # Save report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        self.logger.info(f"Quality report saved to {output_file}")
        return '\n'.join(report)
    
    def plot_quality_distributions(self, metrics_df: pd.DataFrame,
                                 output_file: str = "quality_distributions.png",
                                 figsize: Tuple[int, int] = (15, 10)):
        """Create quality distribution plots"""
        numeric_columns = metrics_df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            self.logger.warning("No numeric columns found for plotting")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        for i, column in enumerate(numeric_columns[:4]):  # Plot up to 4 columns
            if i >= len(axes):
                break
            
            ax = axes[i]
            
            # Histogram
            ax.hist(metrics_df[column].dropna(), bins=30, alpha=0.7, edgecolor='black')
            ax.axvline(metrics_df[column].mean(), color='red', linestyle='--', label='Mean')
            ax.axvline(metrics_df[column].median(), color='green', linestyle='--', label='Median')
            
            # Add threshold line if it exists
            if column in self.default_thresholds:
                ax.axvline(self.default_thresholds[column], color='orange', 
                          linestyle='-', linewidth=2, label='Threshold')
            
            ax.set_title(f'{column.upper()} Distribution')
            ax.set_xlabel(column)
            ax.set_ylabel('Frequency')
            ax.legend()
        
        # Hide unused subplots
        for i in range(len(numeric_columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Quality distributions plot saved to {output_file}")
    
    def plot_quality_correlations(self, metrics_df: pd.DataFrame,
                                output_file: str = "quality_correlations.png",
                                figsize: Tuple[int, int] = (10, 8)):
        """Create correlation heatmap of quality metrics"""
        numeric_columns = metrics_df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) < 2:
            self.logger.warning("Need at least 2 numeric columns for correlation plot")
            return
        
        correlation_matrix = metrics_df[numeric_columns].corr()
        
        plt.figure(figsize=figsize)
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f')
        plt.title('Quality Metrics Correlation Matrix')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Quality correlations plot saved to {output_file}")
    
    def compare_quality_across_datasets(self, datasets: Dict[str, pd.DataFrame],
                                      output_file: str = "quality_comparison.png",
                                      figsize: Tuple[int, int] = (12, 8)):
        """Compare quality metrics across different datasets"""
        comparison_data = []
        
        for dataset_name, df in datasets.items():
            assessment = self.assess_prediction_quality(df)
            for metric, stats in assessment['quality_breakdown'].items():
                comparison_data.append({
                    'dataset': dataset_name,
                    'metric': metric,
                    'high_quality_percentage': stats['high_quality_percentage'],
                    'mean_value': stats['mean_value']
                })
        
        if not comparison_data:
            self.logger.warning("No data for comparison")
            return
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create comparison plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # High quality percentage comparison
        pivot_percentage = comparison_df.pivot(index='dataset', columns='metric', 
                                             values='high_quality_percentage')
        pivot_percentage.plot(kind='bar', ax=ax1)
        ax1.set_title('High Quality Percentage by Dataset')
        ax1.set_ylabel('Percentage (%)')
        ax1.legend(title='Metric')
        ax1.tick_params(axis='x', rotation=45)
        
        # Mean value comparison
        pivot_mean = comparison_df.pivot(index='dataset', columns='metric', 
                                       values='mean_value')
        pivot_mean.plot(kind='bar', ax=ax2)
        ax2.set_title('Mean Values by Dataset')
        ax2.set_ylabel('Mean Value')
        ax2.legend(title='Metric')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Quality comparison plot saved to {output_file}") 