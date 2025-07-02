"""
Report generation utilities for AlphaFold Core
Provides utilities for generating comprehensive reports
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

from ..config import config
from ..utils import setup_logging


class ReportGenerator:
    """Generates comprehensive reports for AlphaFold analysis"""
    
    def __init__(self):
        self.logger = setup_logging()
    
    def generate_data_summary_report(self, df: pd.DataFrame,
                                   output_file: str = "data_summary_report.txt") -> str:
        """Generate a comprehensive data summary report"""
        report = []
        report.append("AlphaFold Data Summary Report")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Basic information
        report.append("DATASET OVERVIEW")
        report.append("-" * 20)
        report.append(f"Total rows: {len(df)}")
        report.append(f"Total columns: {len(df.columns)}")
        report.append(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        report.append("")
        
        # Column information
        report.append("COLUMN INFORMATION")
        report.append("-" * 20)
        for column in df.columns:
            dtype = df[column].dtype
            non_null = df[column].count()
            null_count = df[column].isnull().sum()
            null_percentage = (null_count / len(df)) * 100
            
            report.append(f"{column}:")
            report.append(f"  - Data type: {dtype}")
            report.append(f"  - Non-null values: {non_null}")
            report.append(f"  - Null values: {null_count} ({null_percentage:.1f}%)")
            
            # Add sample values for non-numeric columns
            if not pd.api.types.is_numeric_dtype(df[column]):
                unique_values = df[column].nunique()
                report.append(f"  - Unique values: {unique_values}")
                if unique_values <= 10:
                    sample_values = df[column].dropna().unique()[:5]
                    report.append(f"  - Sample values: {', '.join(map(str, sample_values))}")
            
            report.append("")
        
        # Numeric columns summary
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            report.append("NUMERIC COLUMNS SUMMARY")
            report.append("-" * 25)
            for column in numeric_columns:
                data = df[column].dropna()
                if len(data) > 0:
                    report.append(f"{column}:")
                    report.append(f"  - Mean: {data.mean():.3f}")
                    report.append(f"  - Median: {data.median():.3f}")
                    report.append(f"  - Std: {data.std():.3f}")
                    report.append(f"  - Min: {data.min():.3f}")
                    report.append(f"  - Max: {data.max():.3f}")
                    report.append("")
        
        # Quality metrics summary (if available)
        quality_columns = ['iptm', 'ptm', 'ranking_score']
        available_quality = [col for col in quality_columns if col in df.columns]
        
        if available_quality:
            report.append("QUALITY METRICS SUMMARY")
            report.append("-" * 25)
            for column in available_quality:
                data = df[column].dropna()
                if len(data) > 0:
                    # Define thresholds
                    thresholds = {'iptm': 0.6, 'ptm': 0.5, 'ranking_score': 0.8}
                    threshold = thresholds.get(column, 0.5)
                    
                    above_threshold = (data >= threshold).sum()
                    report.append(f"{column.upper()}:")
                    report.append(f"  - Mean: {data.mean():.3f}")
                    report.append(f"  - Median: {data.median():.3f}")
                    report.append(f"  - Above threshold ({threshold}): {above_threshold} ({above_threshold/len(data)*100:.1f}%)")
                    report.append("")
        
        # Save report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        self.logger.info(f"Data summary report saved to {output_file}")
        return '\n'.join(report)
    
    def generate_quality_assessment_report(self, df: pd.DataFrame,
                                         thresholds: Dict[str, float] = None,
                                         output_file: str = "quality_assessment_report.txt") -> str:
        """Generate a quality assessment report"""
        if thresholds is None:
            thresholds = {'iptm': 0.6, 'ptm': 0.5, 'ranking_score': 0.8}
        
        report = []
        report.append("AlphaFold Quality Assessment Report")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall statistics
        report.append("OVERALL STATISTICS")
        report.append("-" * 20)
        report.append(f"Total predictions: {len(df)}")
        report.append("")
        
        # Quality metrics analysis
        report.append("QUALITY METRICS ANALYSIS")
        report.append("-" * 25)
        
        for metric, threshold in thresholds.items():
            if metric in df.columns:
                data = df[metric].dropna()
                if len(data) > 0:
                    above_threshold = (data >= threshold).sum()
                    below_threshold = (data < threshold).sum()
                    
                    report.append(f"{metric.upper()}:")
                    report.append(f"  - Threshold: {threshold}")
                    report.append(f"  - Mean: {data.mean():.3f}")
                    report.append(f"  - Median: {data.median():.3f}")
                    report.append(f"  - Std: {data.std():.3f}")
                    report.append(f"  - Min: {data.min():.3f}")
                    report.append(f"  - Max: {data.max():.3f}")
                    report.append(f"  - Above threshold: {above_threshold} ({above_threshold/len(data)*100:.1f}%)")
                    report.append(f"  - Below threshold: {below_threshold} ({below_threshold/len(data)*100:.1f}%)")
                    report.append("")
        
        # Combined quality analysis
        report.append("COMBINED QUALITY ANALYSIS")
        report.append("-" * 25)
        
        # Calculate overall quality score
        quality_scores = []
        for metric, threshold in thresholds.items():
            if metric in df.columns:
                score = (df[metric] >= threshold).astype(int)
                quality_scores.append(score)
        
        if quality_scores:
            overall_quality = pd.concat(quality_scores, axis=1).mean(axis=1)
            high_quality = (overall_quality >= 0.5).sum()
            
            report.append(f"Overall quality score:")
            report.append(f"  - Mean: {overall_quality.mean():.3f}")
            report.append(f"  - High quality predictions: {high_quality} ({high_quality/len(df)*100:.1f}%)")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)
        
        for metric, threshold in thresholds.items():
            if metric in df.columns:
                data = df[metric].dropna()
                if len(data) > 0:
                    above_threshold = (data >= threshold).sum()
                    percentage = above_threshold / len(data) * 100
                    
                    if percentage >= 80:
                        report.append(f"✓ {metric.upper()}: Excellent quality ({percentage:.1f}% above threshold)")
                    elif percentage >= 60:
                        report.append(f"○ {metric.upper()}: Good quality ({percentage:.1f}% above threshold)")
                    elif percentage >= 40:
                        report.append(f"⚠ {metric.upper()}: Moderate quality ({percentage:.1f}% above threshold)")
                    else:
                        report.append(f"✗ {metric.upper()}: Poor quality ({percentage:.1f}% above threshold)")
        
        report.append("")
        
        # Save report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        self.logger.info(f"Quality assessment report saved to {output_file}")
        return '\n'.join(report)
    
    def generate_comparison_report(self, comparison_results: Dict[str, Any],
                                 output_file: str = "comparison_report.txt") -> str:
        """Generate a comparison report between datasets"""
        report = []
        report.append("Dataset Comparison Report")
        report.append("=" * 40)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Dataset overview
        if 'datasets' in comparison_results:
            report.append("DATASETS COMPARED")
            report.append("-" * 20)
            for dataset in comparison_results['datasets']:
                report.append(f"  - {dataset}")
            report.append("")
        
        # Summary statistics
        if 'summary_statistics' in comparison_results:
            report.append("SUMMARY STATISTICS")
            report.append("-" * 20)
            for dataset_name, stats in comparison_results['summary_statistics'].items():
                report.append(f"{dataset_name}:")
                for column, column_stats in stats.items():
                    report.append(f"  - {column}: mean={column_stats['mean']:.3f}, std={column_stats['std']:.3f}")
                report.append("")
        
        # Quality comparison
        if 'quality_summary' in comparison_results:
            report.append("QUALITY METRICS COMPARISON")
            report.append("-" * 30)
            for dataset_name, quality_stats in comparison_results['quality_summary'].items():
                report.append(f"{dataset_name}:")
                for metric, stats in quality_stats.items():
                    report.append(f"  - {metric}: mean={stats['mean']:.3f}, median={stats['median']:.3f}")
                report.append("")
        
        # Prediction counts
        if 'prediction_counts' in comparison_results:
            report.append("PREDICTION COUNTS")
            report.append("-" * 20)
            for dataset_name, count in comparison_results['prediction_counts'].items():
                report.append(f"  - {dataset_name}: {count} predictions")
            report.append("")
        
        # Overlaps
        if 'overlaps' in comparison_results:
            report.append("DATASET OVERLAPS")
            report.append("-" * 20)
            for overlap_key, overlap_stats in comparison_results['overlaps'].items():
                report.append(f"{overlap_key}:")
                report.append(f"  - Intersection: {overlap_stats['intersection_size']}")
                report.append(f"  - Jaccard similarity: {overlap_stats['jaccard_similarity']:.3f}")
                report.append(f"  - Overlap % (set1): {overlap_stats['overlap_percentage_set1']:.1f}%")
                report.append(f"  - Overlap % (set2): {overlap_stats['overlap_percentage_set2']:.1f}%")
                report.append("")
        
        # Unique predictions
        if 'unique_predictions' in comparison_results:
            report.append("UNIQUE PREDICTIONS")
            report.append("-" * 20)
            for dataset_name, unique_stats in comparison_results['unique_predictions'].items():
                report.append(f"{dataset_name}:")
                report.append(f"  - Unique count: {unique_stats['unique_count']}")
                report.append(f"  - Unique percentage: {unique_stats['unique_percentage']:.1f}%")
                report.append("")
        
        # Save report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        self.logger.info(f"Comparison report saved to {output_file}")
        return '\n'.join(report)
    
    def generate_execution_report(self, execution_results: Dict[str, Any],
                                output_file: str = "execution_report.txt") -> str:
        """Generate an execution report for pipeline runs"""
        report = []
        report.append("Pipeline Execution Report")
        report.append("=" * 30)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Execution summary
        if 'execution_time' in execution_results:
            report.append("EXECUTION SUMMARY")
            report.append("-" * 20)
            report.append(f"Total execution time: {execution_results['execution_time']:.2f} seconds")
            report.append("")
        
        # Steps executed
        if 'steps' in execution_results:
            report.append("STEPS EXECUTED")
            report.append("-" * 15)
            for step_name, step_result in execution_results['steps'].items():
                status = "✓ SUCCESS" if step_result.get('success', False) else "✗ FAILED"
                report.append(f"{step_name}: {status}")
                if 'message' in step_result:
                    report.append(f"  - {step_result['message']}")
                if 'duration' in step_result:
                    report.append(f"  - Duration: {step_result['duration']:.2f} seconds")
                report.append("")
        
        # Output files
        if 'output_files' in execution_results:
            report.append("OUTPUT FILES")
            report.append("-" * 12)
            for file_type, file_path in execution_results['output_files'].items():
                report.append(f"  - {file_type}: {file_path}")
            report.append("")
        
        # Errors and warnings
        if 'errors' in execution_results and execution_results['errors']:
            report.append("ERRORS")
            report.append("-" * 7)
            for error in execution_results['errors']:
                report.append(f"  - {error}")
            report.append("")
        
        if 'warnings' in execution_results and execution_results['warnings']:
            report.append("WARNINGS")
            report.append("-" * 10)
            for warning in execution_results['warnings']:
                report.append(f"  - {warning}")
            report.append("")
        
        # Save report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        self.logger.info(f"Execution report saved to {output_file}")
        return '\n'.join(report)
    
    def generate_html_report(self, df: pd.DataFrame,
                           output_file: str = "alphafold_report.html") -> str:
        """Generate an HTML report with interactive elements"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AlphaFold Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .success {{ color: green; }}
                .warning {{ color: orange; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>AlphaFold Analysis Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Dataset Overview</h2>
                <div class="metric">
                    <strong>Total Rows:</strong> {len(df)}
                </div>
                <div class="metric">
                    <strong>Total Columns:</strong> {len(df.columns)}
                </div>
                <div class="metric">
                    <strong>Memory Usage:</strong> {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB
                </div>
            </div>
            
            <div class="section">
                <h2>Column Information</h2>
                <table>
                    <tr>
                        <th>Column</th>
                        <th>Data Type</th>
                        <th>Non-Null</th>
                        <th>Null Count</th>
                        <th>Null %</th>
                    </tr>
        """
        
        for column in df.columns:
            non_null = df[column].count()
            null_count = df[column].isnull().sum()
            null_percentage = (null_count / len(df)) * 100
            
            html_content += f"""
                    <tr>
                        <td>{column}</td>
                        <td>{df[column].dtype}</td>
                        <td>{non_null}</td>
                        <td>{null_count}</td>
                        <td>{null_percentage:.1f}%</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        """
        
        # Add quality metrics section if available
        quality_columns = ['iptm', 'ptm', 'ranking_score']
        available_quality = [col for col in quality_columns if col in df.columns]
        
        if available_quality:
            html_content += """
            <div class="section">
                <h2>Quality Metrics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Mean</th>
                        <th>Median</th>
                        <th>Std</th>
                        <th>Min</th>
                        <th>Max</th>
                    </tr>
            """
            
            for column in available_quality:
                data = df[column].dropna()
                if len(data) > 0:
                    html_content += f"""
                    <tr>
                        <td>{column.upper()}</td>
                        <td>{data.mean():.3f}</td>
                        <td>{data.median():.3f}</td>
                        <td>{data.std():.3f}</td>
                        <td>{data.min():.3f}</td>
                        <td>{data.max():.3f}</td>
                    </tr>
                    """
            
            html_content += """
                </table>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        # Save HTML report
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report saved to {output_file}")
        return html_content 