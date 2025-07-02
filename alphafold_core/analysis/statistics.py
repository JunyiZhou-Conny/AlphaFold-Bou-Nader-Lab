"""
Statistical analysis module for AlphaFold Core
Handles statistical analysis of AlphaFold predictions and data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from ..config import config
from ..utils import setup_logging


class StatisticalAnalyzer:
    """Performs statistical analysis on AlphaFold data"""
    
    def __init__(self):
        self.logger = setup_logging()
    
    def calculate_descriptive_statistics(self, data: pd.Series) -> Dict[str, float]:
        """Calculate descriptive statistics for a data series"""
        stats_dict = {
            'count': len(data.dropna()),
            'mean': data.mean(),
            'median': data.median(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'q25': data.quantile(0.25),
            'q75': data.quantile(0.75),
            'skewness': data.skew(),
            'kurtosis': data.kurtosis()
        }
        return stats_dict
    
    def analyze_dataframe_statistics(self, df: pd.DataFrame,
                                   numeric_columns: List[str] = None) -> Dict[str, Any]:
        """Analyze statistics for all numeric columns in a dataframe"""
        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        analysis = {
            'columns': numeric_columns,
            'statistics': {},
            'correlations': {},
            'missing_data': {}
        }
        
        # Calculate statistics for each column
        for column in numeric_columns:
            if column in df.columns:
                analysis['statistics'][column] = self.calculate_descriptive_statistics(df[column])
                analysis['missing_data'][column] = df[column].isna().sum()
        
        # Calculate correlations
        if len(numeric_columns) > 1:
            correlation_matrix = df[numeric_columns].corr()
            analysis['correlations'] = correlation_matrix.to_dict()
        
        return analysis
    
    def perform_hypothesis_test(self, data1: pd.Series, data2: pd.Series,
                              test_type: str = 't_test') -> Dict[str, Any]:
        """Perform hypothesis testing between two datasets"""
        # Remove NaN values
        data1_clean = data1.dropna()
        data2_clean = data2.dropna()
        
        if len(data1_clean) == 0 or len(data2_clean) == 0:
            return {'error': 'Insufficient data for testing'}
        
        results = {
            'test_type': test_type,
            'sample_sizes': {'group1': len(data1_clean), 'group2': len(data2_clean)},
            'group_means': {'group1': data1_clean.mean(), 'group2': data2_clean.mean()},
            'group_stds': {'group1': data1_clean.std(), 'group2': data2_clean.std()}
        }
        
        if test_type == 't_test':
            # Independent t-test
            t_stat, p_value = stats.ttest_ind(data1_clean, data2_clean)
            results.update({
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            })
        
        elif test_type == 'mann_whitney':
            # Mann-Whitney U test (non-parametric)
            u_stat, p_value = stats.mannwhitneyu(data1_clean, data2_clean, alternative='two-sided')
            results.update({
                'u_statistic': u_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            })
        
        elif test_type == 'ks_test':
            # Kolmogorov-Smirnov test
            ks_stat, p_value = stats.ks_2samp(data1_clean, data2_clean)
            results.update({
                'ks_statistic': ks_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            })
        
        return results
    
    def analyze_distribution_fit(self, data: pd.Series,
                               distributions: List[str] = None) -> Dict[str, Any]:
        """Analyze how well data fits different distributions"""
        if distributions is None:
            distributions = ['normal', 'lognormal', 'exponential', 'gamma']
        
        data_clean = data.dropna()
        if len(data_clean) == 0:
            return {'error': 'No data available for analysis'}
        
        results = {
            'data_statistics': self.calculate_descriptive_statistics(data_clean),
            'distribution_fits': {}
        }
        
        for dist_name in distributions:
            try:
                if dist_name == 'normal':
                    params = stats.norm.fit(data_clean)
                    ks_stat, p_value = stats.kstest(data_clean, 'norm', params)
                elif dist_name == 'lognormal':
                    params = stats.lognorm.fit(data_clean)
                    ks_stat, p_value = stats.kstest(data_clean, 'lognorm', params)
                elif dist_name == 'exponential':
                    params = stats.expon.fit(data_clean)
                    ks_stat, p_value = stats.kstest(data_clean, 'expon', params)
                elif dist_name == 'gamma':
                    params = stats.gamma.fit(data_clean)
                    ks_stat, p_value = stats.kstest(data_clean, 'gamma', params)
                else:
                    continue
                
                results['distribution_fits'][dist_name] = {
                    'parameters': params,
                    'ks_statistic': ks_stat,
                    'p_value': p_value,
                    'good_fit': p_value > 0.05
                }
            
            except Exception as e:
                results['distribution_fits'][dist_name] = {'error': str(e)}
        
        return results
    
    def calculate_confidence_intervals(self, data: pd.Series,
                                     confidence_level: float = 0.95) -> Dict[str, float]:
        """Calculate confidence intervals for the mean"""
        data_clean = data.dropna()
        
        if len(data_clean) == 0:
            return {'error': 'No data available'}
        
        mean = data_clean.mean()
        std_err = stats.sem(data_clean)
        
        # Calculate confidence interval
        ci_lower, ci_upper = stats.t.interval(confidence_level, len(data_clean) - 1, 
                                            loc=mean, scale=std_err)
        
        return {
            'mean': mean,
            'std_error': std_err,
            'confidence_level': confidence_level,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'sample_size': len(data_clean)
        }
    
    def perform_anova(self, data_dict: Dict[str, pd.Series]) -> Dict[str, Any]:
        """Perform one-way ANOVA on multiple groups"""
        # Prepare data for ANOVA
        groups = []
        group_names = []
        
        for name, data in data_dict.items():
            clean_data = data.dropna()
            if len(clean_data) > 0:
                groups.append(clean_data)
                group_names.append(name)
        
        if len(groups) < 2:
            return {'error': 'Need at least 2 groups for ANOVA'}
        
        # Perform ANOVA
        f_stat, p_value = stats.f_oneway(*groups)
        
        results = {
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'groups': group_names,
            'group_sizes': [len(group) for group in groups],
            'group_means': [group.mean() for group in groups]
        }
        
        return results
    
    def create_statistical_report(self, df: pd.DataFrame,
                                output_file: str = "statistical_report.txt") -> str:
        """Generate a comprehensive statistical report"""
        analysis = self.analyze_dataframe_statistics(df)
        
        report = []
        report.append("Statistical Analysis Report")
        report.append("=" * 40)
        report.append("")
        
        # Overall statistics
        report.append(f"Dataset Overview:")
        report.append(f"  - Total rows: {len(df)}")
        report.append(f"  - Numeric columns: {len(analysis['columns'])}")
        report.append("")
        
        # Statistics for each column
        for column in analysis['columns']:
            if column in analysis['statistics']:
                stats = analysis['statistics'][column]
                report.append(f"{column.upper()} Statistics:")
                report.append(f"  - Count: {stats['count']}")
                report.append(f"  - Mean: {stats['mean']:.3f}")
                report.append(f"  - Median: {stats['median']:.3f}")
                report.append(f"  - Std: {stats['std']:.3f}")
                report.append(f"  - Min: {stats['min']:.3f}")
                report.append(f"  - Max: {stats['max']:.3f}")
                report.append(f"  - Q25: {stats['q25']:.3f}")
                report.append(f"  - Q75: {stats['q75']:.3f}")
                report.append(f"  - Skewness: {stats['skewness']:.3f}")
                report.append(f"  - Kurtosis: {stats['kurtosis']:.3f}")
                report.append("")
        
        # Missing data summary
        if any(analysis['missing_data'].values()):
            report.append("Missing Data Summary:")
            for column, missing_count in analysis['missing_data'].items():
                if missing_count > 0:
                    percentage = (missing_count / len(df)) * 100
                    report.append(f"  - {column}: {missing_count} ({percentage:.1f}%)")
            report.append("")
        
        # Save report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        self.logger.info(f"Statistical report saved to {output_file}")
        return '\n'.join(report)
    
    def plot_statistical_summary(self, df: pd.DataFrame,
                               output_file: str = "statistical_summary.png",
                               figsize: Tuple[int, int] = (15, 12)):
        """Create comprehensive statistical summary plots"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            self.logger.warning("No numeric columns found for plotting")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        # Box plots
        df[numeric_columns].boxplot(ax=axes[0])
        axes[0].set_title('Box Plots of Numeric Variables')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Histograms
        for i, column in enumerate(numeric_columns[:4]):
            if i < len(axes) - 1:
                axes[i + 1].hist(df[column].dropna(), bins=30, alpha=0.7, edgecolor='black')
                axes[i + 1].set_title(f'{column} Distribution')
                axes[i + 1].set_xlabel(column)
                axes[i + 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Statistical summary plot saved to {output_file}")
    
    def plot_correlation_matrix(self, df: pd.DataFrame,
                              output_file: str = "correlation_matrix.png",
                              figsize: Tuple[int, int] = (10, 8)):
        """Create correlation matrix heatmap"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) < 2:
            self.logger.warning("Need at least 2 numeric columns for correlation matrix")
            return
        
        correlation_matrix = df[numeric_columns].corr()
        
        plt.figure(figsize=figsize)
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f')
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Correlation matrix plot saved to {output_file}")
    
    def compare_groups_statistically(self, df: pd.DataFrame,
                                   group_column: str,
                                   value_column: str,
                                   output_file: str = "group_comparison.png",
                                   figsize: Tuple[int, int] = (12, 8)):
        """Compare groups statistically and create visualization"""
        if group_column not in df.columns or value_column not in df.columns:
            self.logger.error("Group or value column not found in dataframe")
            return
        
        # Group the data
        groups = df.groupby(group_column)[value_column]
        
        # Perform ANOVA
        anova_result = self.perform_anova({name: group for name, group in groups})
        
        # Create comparison plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Box plot
        df.boxplot(column=value_column, by=group_column, ax=ax1)
        ax1.set_title(f'{value_column} by {group_column}')
        ax1.set_xlabel(group_column)
        ax1.set_ylabel(value_column)
        
        # Bar plot of means with error bars
        group_means = groups.mean()
        group_stds = groups.std()
        
        group_means.plot(kind='bar', yerr=group_stds, ax=ax2, capsize=5)
        ax2.set_title(f'Mean {value_column} by {group_column}')
        ax2.set_xlabel(group_column)
        ax2.set_ylabel(f'Mean {value_column}')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Group comparison plot saved to {output_file}")
        
        return anova_result 