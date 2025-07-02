"""
Plotting utilities for AlphaFold Core
Provides various plotting functions for data visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any

from ..config import config
from ..utils import setup_logging


class PlotGenerator:
    """Generates various plots for AlphaFold data visualization"""
    
    def __init__(self):
        self.logger = setup_logging()
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def plot_quality_metrics(self, df: pd.DataFrame,
                           quality_columns: List[str] = None,
                           output_file: str = "quality_metrics.png",
                           figsize: Tuple[int, int] = (15, 10)):
        """Create comprehensive quality metrics plots"""
        if quality_columns is None:
            quality_columns = ['iptm', 'ptm', 'ranking_score']
        
        # Filter to only include columns that exist
        available_columns = [col for col in quality_columns if col in df.columns]
        
        if not available_columns:
            self.logger.warning("No quality columns found in dataframe")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        # Plot 1: Histograms
        for i, column in enumerate(available_columns[:4]):
            if i < len(axes):
                axes[i].hist(df[column].dropna(), bins=30, alpha=0.7, edgecolor='black')
                axes[i].set_title(f'{column.upper()} Distribution')
                axes[i].set_xlabel(column)
                axes[i].set_ylabel('Frequency')
        
        # Hide unused subplots
        for i in range(len(available_columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Quality metrics plot saved to {output_file}")
    
    def plot_correlation_heatmap(self, df: pd.DataFrame,
                               columns: List[str] = None,
                               output_file: str = "correlation_heatmap.png",
                               figsize: Tuple[int, int] = (10, 8)):
        """Create correlation heatmap"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Filter to only include columns that exist
        available_columns = [col for col in columns if col in df.columns]
        
        if len(available_columns) < 2:
            self.logger.warning("Need at least 2 numeric columns for correlation heatmap")
            return
        
        correlation_matrix = df[available_columns].corr()
        
        plt.figure(figsize=figsize)
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f')
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Correlation heatmap saved to {output_file}")
    
    def plot_scatter_matrix(self, df: pd.DataFrame,
                          columns: List[str] = None,
                          output_file: str = "scatter_matrix.png",
                          figsize: Tuple[int, int] = (12, 12)):
        """Create scatter plot matrix"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Filter to only include columns that exist
        available_columns = [col for col in columns if col in df.columns]
        
        if len(available_columns) < 2:
            self.logger.warning("Need at least 2 numeric columns for scatter matrix")
            return
        
        # Limit to 6 columns for readability
        if len(available_columns) > 6:
            available_columns = available_columns[:6]
            self.logger.info(f"Limited to first 6 columns: {available_columns}")
        
        fig = sns.pairplot(df[available_columns].dropna(), diag_kind='hist')
        fig.fig.suptitle('Scatter Plot Matrix', y=1.02)
        fig.fig.set_size_inches(figsize)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Scatter matrix saved to {output_file}")
    
    def plot_box_plots(self, df: pd.DataFrame,
                      columns: List[str] = None,
                      output_file: str = "box_plots.png",
                      figsize: Tuple[int, int] = (12, 8)):
        """Create box plots for numeric columns"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Filter to only include columns that exist
        available_columns = [col for col in columns if col in df.columns]
        
        if not available_columns:
            self.logger.warning("No numeric columns found for box plots")
            return
        
        plt.figure(figsize=figsize)
        df[available_columns].boxplot()
        plt.title('Box Plots of Numeric Variables')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Box plots saved to {output_file}")
    
    def plot_sequence_length_distribution(self, df: pd.DataFrame,
                                        sequence_column: str = 'sequence',
                                        output_file: str = "sequence_length_dist.png",
                                        figsize: Tuple[int, int] = (12, 8)):
        """Plot sequence length distribution"""
        if sequence_column not in df.columns:
            self.logger.warning(f"Sequence column '{sequence_column}' not found")
            return
        
        lengths = df[sequence_column].str.len().dropna()
        
        if len(lengths) == 0:
            self.logger.warning("No sequence data available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Histogram
        ax1.hist(lengths, bins=30, alpha=0.7, edgecolor='black')
        ax1.set_title('Sequence Length Distribution')
        ax1.set_xlabel('Sequence Length')
        ax1.set_ylabel('Frequency')
        
        # Box plot
        ax2.boxplot(lengths)
        ax2.set_title('Sequence Length Box Plot')
        ax2.set_ylabel('Sequence Length')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Sequence length distribution saved to {output_file}")
    
    def plot_overlap_venn(self, datasets: Dict[str, set],
                         output_file: str = "overlap_venn.png",
                         figsize: Tuple[int, int] = (10, 8)):
        """Create Venn diagram for dataset overlaps"""
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
            
            plt.title('Dataset Overlap Venn Diagram')
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Venn diagram saved to {output_file}")
            
        except ImportError:
            self.logger.error("matplotlib_venn not installed. Install with: pip install matplotlib-venn")
    
    def plot_overlap_heatmap(self, overlap_matrix: pd.DataFrame,
                           output_file: str = "overlap_heatmap.png",
                           figsize: Tuple[int, int] = (10, 8)):
        """Create heatmap for dataset overlaps"""
        plt.figure(figsize=figsize)
        
        sns.heatmap(overlap_matrix, annot=True, cmap='Blues', fmt='.1f',
                   cbar_kws={'label': 'Overlap Percentage (%)'})
        plt.title('Dataset Overlap Analysis')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Overlap heatmap saved to {output_file}")
    
    def plot_quality_threshold_analysis(self, df: pd.DataFrame,
                                      quality_columns: List[str] = None,
                                      thresholds: Dict[str, float] = None,
                                      output_file: str = "quality_threshold_analysis.png",
                                      figsize: Tuple[int, int] = (15, 10)):
        """Analyze quality metrics against thresholds"""
        if quality_columns is None:
            quality_columns = ['iptm', 'ptm', 'ranking_score']
        
        if thresholds is None:
            thresholds = {'iptm': 0.6, 'ptm': 0.5, 'ranking_score': 0.8}
        
        # Filter to only include columns that exist
        available_columns = [col for col in quality_columns if col in df.columns]
        
        if not available_columns:
            self.logger.warning("No quality columns found for threshold analysis")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        for i, column in enumerate(available_columns[:4]):
            if i < len(axes):
                ax = axes[i]
                
                # Histogram with threshold line
                ax.hist(df[column].dropna(), bins=30, alpha=0.7, edgecolor='black')
                
                # Add threshold line if available
                if column in thresholds:
                    threshold = thresholds[column]
                    ax.axvline(threshold, color='red', linestyle='--', linewidth=2, 
                             label=f'Threshold ({threshold})')
                    ax.legend()
                
                ax.set_title(f'{column.upper()} Distribution')
                ax.set_xlabel(column)
                ax.set_ylabel('Frequency')
        
        # Hide unused subplots
        for i in range(len(available_columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Quality threshold analysis saved to {output_file}")
    
    def plot_time_series(self, df: pd.DataFrame,
                        time_column: str,
                        value_columns: List[str] = None,
                        output_file: str = "time_series.png",
                        figsize: Tuple[int, int] = (12, 8)):
        """Create time series plots"""
        if time_column not in df.columns:
            self.logger.warning(f"Time column '{time_column}' not found")
            return
        
        if value_columns is None:
            value_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            value_columns = [col for col in value_columns if col != time_column]
        
        # Filter to only include columns that exist
        available_columns = [col for col in value_columns if col in df.columns]
        
        if not available_columns:
            self.logger.warning("No value columns found for time series")
            return
        
        # Convert time column to datetime if possible
        try:
            df[time_column] = pd.to_datetime(df[time_column])
        except:
            self.logger.warning(f"Could not convert {time_column} to datetime")
        
        plt.figure(figsize=figsize)
        
        for column in available_columns:
            plt.plot(df[time_column], df[column], label=column, marker='o', markersize=2)
        
        plt.title('Time Series Analysis')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Time series plot saved to {output_file}")
    
    def plot_group_comparison(self, df: pd.DataFrame,
                            group_column: str,
                            value_column: str,
                            output_file: str = "group_comparison.png",
                            figsize: Tuple[int, int] = (12, 8)):
        """Compare groups using box plots and bar charts"""
        if group_column not in df.columns or value_column not in df.columns:
            self.logger.warning("Group or value column not found")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Box plot
        df.boxplot(column=value_column, by=group_column, ax=ax1)
        ax1.set_title(f'{value_column} by {group_column}')
        ax1.set_xlabel(group_column)
        ax1.set_ylabel(value_column)
        
        # Bar plot of means
        group_means = df.groupby(group_column)[value_column].mean()
        group_means.plot(kind='bar', ax=ax2)
        ax2.set_title(f'Mean {value_column} by {group_column}')
        ax2.set_xlabel(group_column)
        ax2.set_ylabel(f'Mean {value_column}')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Group comparison plot saved to {output_file}")
    
    def create_dashboard(self, df: pd.DataFrame,
                        output_file: str = "dashboard.png",
                        figsize: Tuple[int, int] = (20, 15)):
        """Create a comprehensive dashboard with multiple plots"""
        fig, axes = plt.subplots(3, 3, figsize=figsize)
        axes = axes.flatten()
        
        # Get numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Plot 1: Summary statistics
        if numeric_columns:
            summary_stats = df[numeric_columns].describe()
            axes[0].text(0.1, 0.9, 'Summary Statistics', transform=axes[0].transAxes, 
                        fontsize=12, fontweight='bold')
            axes[0].text(0.1, 0.8, f'Total rows: {len(df)}', transform=axes[0].transAxes)
            axes[0].text(0.1, 0.7, f'Numeric columns: {len(numeric_columns)}', transform=axes[0].transAxes)
            axes[0].set_xlim(0, 1)
            axes[0].set_ylim(0, 1)
            axes[0].axis('off')
        
        # Plot 2-4: Histograms of first 3 numeric columns
        for i, column in enumerate(numeric_columns[:3]):
            if i + 1 < len(axes):
                axes[i + 1].hist(df[column].dropna(), bins=20, alpha=0.7, edgecolor='black')
                axes[i + 1].set_title(f'{column} Distribution')
                axes[i + 1].set_xlabel(column)
                axes[i + 1].set_ylabel('Frequency')
        
        # Plot 5: Correlation heatmap (if multiple numeric columns)
        if len(numeric_columns) >= 2:
            correlation_matrix = df[numeric_columns].corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, fmt='.2f', ax=axes[4])
            axes[4].set_title('Correlation Matrix')
        
        # Plot 6: Missing data
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            missing_data.plot(kind='bar', ax=axes[5])
            axes[5].set_title('Missing Data by Column')
            axes[5].set_xlabel('Column')
            axes[5].set_ylabel('Missing Count')
            axes[5].tick_params(axis='x', rotation=45)
        
        # Plot 7: Box plots
        if numeric_columns:
            df[numeric_columns].boxplot(ax=axes[6])
            axes[6].set_title('Box Plots')
            axes[6].tick_params(axis='x', rotation=45)
        
        # Plot 8: Data types
        dtype_counts = df.dtypes.value_counts()
        dtype_counts.plot(kind='pie', ax=axes[7], autopct='%1.1f%%')
        axes[7].set_title('Data Types Distribution')
        
        # Hide unused subplots
        for i in range(8, len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('AlphaFold Data Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Dashboard saved to {output_file}") 