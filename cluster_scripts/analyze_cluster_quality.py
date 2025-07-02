#!/usr/bin/env python3
"""
Analyze Cluster Data Quality and Suggest Appropriate Thresholds
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Add alphafold_core to Python path
sys.path.append('/data7/Conny/scripts/alphafold_core')

from alphafold_core.data.processor import JSONProcessor
from alphafold_core.analysis.quality import QualityAnalyzer

def analyze_cluster_data_quality():
    """Analyze the quality of cluster data and suggest thresholds"""
    
    print("🔍 ANALYZING CLUSTER DATA QUALITY")
    print("=" * 50)
    
    # Load the cluster data
    json_processor = JSONProcessor()
    cluster_dir = Path("/data7/Conny/Dicer")
    
    print(f"Loading data from: {cluster_dir}")
    
    # Load the data
    df, missing_report = json_processor.process_af3_results(
        cluster_dir, 
        "temp_cluster_analysis.csv"
    )
    
    print(f"✅ Loaded {len(df)} predictions")
    print(f"📊 Columns: {list(df.columns)}")
    
    # Analyze quality metrics
    quality_analyzer = QualityAnalyzer()
    
    # Get quality assessment with default thresholds
    assessment = quality_analyzer.assess_prediction_quality(df)
    
    print(f"\n📊 QUALITY ASSESSMENT WITH DEFAULT THRESHOLDS")
    print("-" * 50)
    print(f"Total predictions: {assessment['total_predictions']}")
    print(f"Default thresholds: {assessment['thresholds_used']}")
    
    for metric, stats in assessment['quality_breakdown'].items():
        print(f"\n{metric.upper()}:")
        print(f"  - High quality: {stats['high_quality_count']} ({stats['high_quality_percentage']:.1f}%)")
        print(f"  - Threshold: {stats['threshold']}")
        print(f"  - Mean: {stats['mean_value']:.3f}")
        print(f"  - Median: {stats['median_value']:.3f}")
        print(f"  - Min: {df[metric].min():.3f}")
        print(f"  - Max: {df[metric].max():.3f}")
    
    # Suggest appropriate thresholds based on data distribution
    print(f"\n🎯 SUGGESTED THRESHOLDS FOR YOUR DATA")
    print("-" * 50)
    
    suggested_thresholds = {}
    for metric in ['iptm', 'ptm', 'ranking_score']:
        if metric in df.columns:
            data = df[metric].dropna()
            
            # Calculate percentiles
            p25 = data.quantile(0.25)
            p50 = data.quantile(0.50)  # median
            p75 = data.quantile(0.75)
            p90 = data.quantile(0.90)
            
            print(f"\n{metric.upper()} Distribution:")
            print(f"  - 25th percentile: {p25:.3f}")
            print(f"  - 50th percentile (median): {p50:.3f}")
            print(f"  - 75th percentile: {p75:.3f}")
            print(f"  - 90th percentile: {p90:.3f}")
            
            # Suggest thresholds
            suggested_thresholds[metric] = {
                'lenient': p25,      # 25th percentile
                'moderate': p50,     # 50th percentile (median)
                'strict': p75,       # 75th percentile
                'very_strict': p90   # 90th percentile
            }
    
    # Test different filtering strategies
    print(f"\n🧪 TESTING DIFFERENT FILTERING STRATEGIES")
    print("-" * 50)
    
    # Test with suggested thresholds
    for strictness in ['lenient', 'moderate', 'strict', 'very_strict']:
        thresholds = {metric: values[strictness] for metric, values in suggested_thresholds.items()}
        
        print(f"\n{strictness.upper()} thresholds: {thresholds}")
        
        # Test 'all' filter type
        high_quality_all = quality_analyzer.filter_high_quality_predictions(
            df, thresholds=thresholds, filter_type='all'
        )
        
        # Test 'any' filter type
        high_quality_any = quality_analyzer.filter_high_quality_predictions(
            df, thresholds=thresholds, filter_type='any'
        )
        
        # Test 'majority' filter type
        high_quality_majority = quality_analyzer.filter_high_quality_predictions(
            df, thresholds=thresholds, filter_type='majority'
        )
        
        print(f"  - 'all' filter: {len(high_quality_all)} predictions ({len(high_quality_all)/len(df)*100:.1f}%)")
        print(f"  - 'any' filter: {len(high_quality_any)} predictions ({len(high_quality_any)/len(df)*100:.1f}%)")
        print(f"  - 'majority' filter: {len(high_quality_majority)} predictions ({len(high_quality_majority)/len(df)*100:.1f}%)")
    
    # Show sample of high-quality predictions with moderate thresholds
    print(f"\n📋 SAMPLE HIGH-QUALITY PREDICTIONS (Moderate Thresholds)")
    print("-" * 50)
    
    moderate_thresholds = {metric: values['moderate'] for metric, values in suggested_thresholds.items()}
    high_quality_sample = quality_analyzer.filter_high_quality_predictions(
        df, thresholds=moderate_thresholds, filter_type='any'
    )
    
    if len(high_quality_sample) > 0:
        print(f"Found {len(high_quality_sample)} high-quality predictions")
        print("\nSample of high-quality predictions:")
        sample_cols = ['fold_group', 'job_number', 'target_protein', 'iptm', 'ptm', 'ranking_score']
        available_cols = [col for col in sample_cols if col in high_quality_sample.columns]
        print(high_quality_sample[available_cols].head(10).to_string())
    else:
        print("No high-quality predictions found with moderate thresholds")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS FOR YOUR CLUSTER DATA")
    print("-" * 50)
    
    # Find the best threshold combination
    best_thresholds = {}
    for metric in ['iptm', 'ptm', 'ranking_score']:
        if metric in suggested_thresholds:
            # Use moderate threshold for balanced approach
            best_thresholds[metric] = suggested_thresholds[metric]['moderate']
    
    print(f"Recommended thresholds: {best_thresholds}")
    print(f"Recommended filter type: 'any' (at least one threshold must be met)")
    
    # Test the recommendation
    recommended_high_quality = quality_analyzer.filter_high_quality_predictions(
        df, thresholds=best_thresholds, filter_type='any'
    )
    
    print(f"This will give you {len(recommended_high_quality)} high-quality predictions ({len(recommended_high_quality)/len(df)*100:.1f}%)")
    
    return df, suggested_thresholds, best_thresholds

if __name__ == "__main__":
    df, suggested_thresholds, best_thresholds = analyze_cluster_data_quality()
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Total predictions analyzed: {len(df)}")
    print(f"🎯 Use these thresholds for your cluster analysis: {best_thresholds}") 