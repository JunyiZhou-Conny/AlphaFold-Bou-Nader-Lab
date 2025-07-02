#!/usr/bin/env python3
"""
Cluster-Specific AF3 Analysis Script - FINAL WORKING VERSION
Uses the same alphafold_core system, just with cluster paths
"""

import sys
import os
import re
import json
from pathlib import Path
import pandas as pd

# Add alphafold_core to Python path on cluster - use parent directory method
alphafold_core_path = '/data7/Conny/scripts/alphafold_core'

# Check if the path exists
if not os.path.exists(alphafold_core_path):
    print(f"❌ alphafold_core path does not exist: {alphafold_core_path}")
    sys.exit(1)

# Remove current directory from sys.path to avoid conflicts
current_dir = os.getcwd()
if current_dir in sys.path:
    sys.path.remove(current_dir)

# Add parent directory to Python path (this method works from debug)
parent_dir = os.path.dirname(alphafold_core_path)
sys.path.insert(0, parent_dir)

print(f"🔍 Looking for alphafold_core at: {alphafold_core_path}")
print(f"✅ Added parent directory to Python path: {parent_dir}")
print(f"📁 Current working directory: {current_dir}")
print(f"🔧 Removed current directory from Python path to avoid conflicts")

try:
    # Import from alphafold_core (same as local)
    from alphafold_core.pipeline.workflows import AF3SummaryAnalysisWorkflow
    from alphafold_core.data.processor import JSONProcessor
    from alphafold_core.analysis.quality import QualityAnalyzer
    print("✅ Successfully imported alphafold_core modules")
except ImportError as e:
    print(f"❌ Failed to import alphafold_core: {e}")
    print("Please check if alphafold_core is installed at the specified path")
    print(f"Python path: {sys.path[:3]}")
    sys.exit(1)

# Cluster-specific configuration
CLUSTER_JSON_DIR = "/data7/Conny/Projects/Dicer_685/AF3_Server/data/Dicer/folds_all"
CLUSTER_OUTPUT_DIR = "/data7/Conny/Projects/Dicer_685/AF3_Server/results"

# Check if input directory exists
if not os.path.exists(CLUSTER_JSON_DIR):
    print(f"❌ Input directory does not exist: {CLUSTER_JSON_DIR}")
    sys.exit(1)

# Create output directory if it doesn't exist
os.makedirs(CLUSTER_OUTPUT_DIR, exist_ok=True)

# Configure for headless cluster
import matplotlib
matplotlib.use('Agg')

def load_data_directly():
    """Load data directly using custom method for the actual directory structure"""
    print(f"\n🔄 LOADING DATA DIRECTLY")
    
    json_dir = Path(CLUSTER_JSON_DIR)
    print(f"Using directory: {json_dir}")
    
    # Find all job directories
    job_dirs = [d for d in json_dir.iterdir() if d.is_dir() and d.name.startswith('test_fold_job_')]
    print(f"Found {len(job_dirs)} job directories")
    
    data_rows = []
    
    for job_dir in job_dirs:
        # Extract job number and protein info from directory name
        # Format: test_fold_job_100_q9upy3_q9bq39
        match = re.match(r'test_fold_job_(\d+)_q[\d\w]+_([a-zA-Z][\d\w]+)', job_dir.name)
        if not match:
            print(f"⚠️  Skipping directory with unexpected name: {job_dir.name}")
            continue
            
        job_number = int(match.group(1))
        target_protein = match.group(2)
        
        # Look for summary confidence files
        summary_files = list(job_dir.glob("*_summary_confidences_*.json"))
        
        if not summary_files:
            print(f"⚠️  No summary files found in {job_dir.name}")
            continue
        
        # Process each summary file (usually 5 models: 0-4)
        for summary_file in summary_files:
            try:
                with open(summary_file, 'r') as f:
                    content = json.load(f)
                
                # Extract model number from filename
                model_match = re.search(r'summary_confidences_(\d+)\.json$', summary_file.name)
                model_num = int(model_match.group(1)) if model_match else 0
                
                row = {
                    'fold_group': 'folds_all',  # All jobs are in one group
                    'job_number': job_number,
                    'target_protein': target_protein,
                    'model_number': model_num,
                    'iptm': content.get("iptm", ""),
                    'ptm': content.get("ptm", ""),
                    'ranking_score': content.get("ranking_score", ""),
                    'fraction_disordered': content.get("fraction_disordered", ""),
                    'has_clash': content.get("has_clash", ""),
                    'num_recycles': content.get("num_recycles", "")
                }
                
                # Flatten chain_iptm and chain_ptm
                chain_iptm = content.get("chain_iptm", ["", ""])
                chain_ptm = content.get("chain_ptm", ["", ""])
                
                row["chain_iptm_0"], row["chain_iptm_1"] = (chain_iptm + ["", ""])[:2]
                row["chain_ptm_0"], row["chain_ptm_1"] = (chain_ptm + ["", ""])[:2]
                
                # Flatten 2x2 matrices
                for matrix_key, prefix in [("chain_pair_iptm", "chain_pair_iptm"), 
                                         ("chain_pair_pae_min", "chain_pair_pae_min")]:
                    matrix = content.get(matrix_key, [["", ""], ["", ""]])
                    for i in range(2):
                        for j in range(2):
                            row[f"{prefix}_{i}{j}"] = matrix[i][j] if matrix and len(matrix) > i and len(matrix[i]) > j else ""
                
                data_rows.append(row)
                
            except Exception as e:
                print(f"❌ Error processing {summary_file}: {e}")
                continue
    
    # Create DataFrame
    if data_rows:
        df = pd.DataFrame(data_rows)
        
        # Sort by job number and model number
        df = df.sort_values(['job_number', 'model_number'])
        
        # Save to CSV
        output_csv = f"{CLUSTER_OUTPUT_DIR}/cluster_af3_analysis_summary_metrics.csv"
        df.to_csv(output_csv, index=False)
        
        print(f"✅ Successfully loaded {len(df)} predictions from {len(job_dirs)} job directories")
        print(f"📊 Columns: {list(df.columns)}")
        print(f"📊 Unique jobs: {df['job_number'].nunique()}")
        print(f"📊 Models per job: {df.groupby('job_number').size().describe()}")
        
        return df
    else:
        print("❌ No data loaded")
        return pd.DataFrame()

def run_cluster_analysis():
    """Run AF3 analysis on cluster using alphafold_core"""
    
    print(f"\n🚀 STARTING CLUSTER ANALYSIS")
    print(f"Input directory: {CLUSTER_JSON_DIR}")
    print(f"Output directory: {CLUSTER_OUTPUT_DIR}")
    
    # Load data directly (bypassing the workflow's _load_data method)
    df = load_data_directly()
    
    if df is None or df.empty:
        print("❌ No data loaded for analysis")
        return None
    
    # Create the workflow
    print(f"\n🔄 CREATING WORKFLOW")
    workflow = AF3SummaryAnalysisWorkflow()
    
    # Run the analysis with the loaded DataFrame
    print(f"\n🔄 RUNNING AF3 ANALYSIS WORKFLOW")
    try:
        results = workflow.run_af3_analysis_workflow(
            input_source=df,  # Pass the DataFrame directly instead of directory path
            output_prefix=f"{CLUSTER_OUTPUT_DIR}/cluster_af3_analysis",
            analysis_type="comprehensive"
        )
        
        print(f"\n✅ Workflow completed!")
        print(f"Results keys: {list(results.keys())}")
        
        if 'data_info' in results:
            data_info = results['data_info']
            print(f"📊 Data loaded: {data_info.get('total_predictions', 0)} predictions")
            print(f"📊 Columns: {data_info.get('columns', [])}")
        
        if 'output_files' in results:
            print(f"📁 Generated output files:")
            for file_type, file_path in results['output_files'].items():
                print(f"   - {file_type}: {file_path}")
        
        return results
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = run_cluster_analysis()
    if results and 'data_info' in results:
        print("\n✅ Cluster analysis completed successfully!")
        print(f"📁 Outputs saved to: {CLUSTER_OUTPUT_DIR}")
        print(f"📊 Total predictions analyzed: {results['data_info'].get('total_predictions', 0)}")
    else:
        print("\n❌ Cluster analysis failed!")
        print("Check the error messages above for details.") 