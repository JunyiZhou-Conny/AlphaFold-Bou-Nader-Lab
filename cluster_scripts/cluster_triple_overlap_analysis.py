#!/usr/bin/env python3
"""
Cluster-Specific Triple Overlap R-Loop Analysis Script
Analyzes AlphaFold3 results for the Triple Overlap R-Loop project
"""

import sys
import os
import re
import json
from pathlib import Path
import pandas as pd

# Add alphafold_core to Python path on cluster
alphafold_core_path = '/data7/Conny/scripts/alphafold_core'

# Check if the path exists
if not os.path.exists(alphafold_core_path):
    print(f"❌ alphafold_core path does not exist: {alphafold_core_path}")
    sys.exit(1)

# Remove current directory from sys.path to avoid conflicts
current_dir = os.getcwd()
if current_dir in sys.path:
    sys.path.remove(current_dir)

# Add parent directory to Python path
parent_dir = os.path.dirname(alphafold_core_path)
sys.path.insert(0, parent_dir)

print(f"🔍 Looking for alphafold_core at: {alphafold_core_path}")
print(f"✅ Added parent directory to Python path: {parent_dir}")
print(f"📁 Current working directory: {current_dir}")

try:
    # Import from alphafold_core
    from alphafold_core.pipeline.workflows import AF3SummaryAnalysisWorkflow
    from alphafold_core.data.processor import JSONProcessor
    from alphafold_core.analysis.quality import QualityAnalyzer
    print("✅ Successfully imported alphafold_core modules")
except ImportError as e:
    print(f"❌ Failed to import alphafold_core: {e}")
    print("Please check if alphafold_core is installed at the specified path")
    print(f"Python path: {sys.path[:3]}")
    sys.exit(1)

# Cluster-specific configuration for Triple Overlap R-Loop
CLUSTER_DATA_DIR = "/data7/Conny/Projects/Triple_Overlap_RLoop/data/26_Overlap"
CLUSTER_OUTPUT_DIR = "/data7/Conny/Projects/Triple_Overlap_RLoop/results"

# Check if input directory exists
if not os.path.exists(CLUSTER_DATA_DIR):
    print(f"❌ Input directory does not exist: {CLUSTER_DATA_DIR}")
    sys.exit(1)

# Create output directory if it doesn't exist
os.makedirs(CLUSTER_OUTPUT_DIR, exist_ok=True)

# Configure for headless cluster
import matplotlib
matplotlib.use('Agg')

def load_triple_overlap_data():
    """Load data from the Triple Overlap R-Loop directory structure"""
    print(f"\n🔄 LOADING TRIPLE OVERLAP R-LOOP DATA")
    
    data_dir = Path(CLUSTER_DATA_DIR)
    print(f"Using directory: {data_dir}")
    
    # Find all data type directories (dsDNA, dsRNA, RLoop, ssDNA)
    data_types = [d for d in data_dir.iterdir() if d.is_dir()]
    print(f"Found {len(data_types)} data type directories: {[d.name for d in data_types]}")
    
    data_rows = []
    
    for data_type_dir in data_types:
        data_type = data_type_dir.name
        print(f"\n📁 Processing data type: {data_type}")
        
        # Find all protein directories
        protein_dirs = [d for d in data_type_dir.iterdir() if d.is_dir() and not d.name.endswith('.md')]
        print(f"Found {len(protein_dirs)} protein directories in {data_type}")
        
        for protein_dir in protein_dirs:
            # Extract protein ID and type from directory name
            # Format: o00567_dsrna, p11387_dsdna, etc.
            match = re.match(r'([a-zA-Z0-9]+)_([a-z]+)', protein_dir.name)
            if not match:
                print(f"⚠️  Skipping directory with unexpected name: {protein_dir.name}")
                continue
                
            protein_id = match.group(1)
            protein_type = match.group(2)
            
            # Look for summary confidence files
            summary_files = list(protein_dir.glob("*_summary_confidences_*.json"))
            
            if not summary_files:
                print(f"⚠️  No summary files found in {protein_dir.name}")
                continue
            
            print(f"  📄 Found {len(summary_files)} summary files for {protein_id}")
            
            # Process each summary file (usually 5 models: 0-4)
            for summary_file in summary_files:
                try:
                    with open(summary_file, 'r') as f:
                        content = json.load(f)
                    
                    # Extract model number from filename
                    model_match = re.search(r'summary_confidences_(\d+)\.json$', summary_file.name)
                    model_num = int(model_match.group(1)) if model_match else 0
                    
                    row = {
                        'data_type': data_type,
                        'protein_id': protein_id,
                        'protein_type': protein_type,
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
        
        # Sort by data type, protein ID, and model number
        df = df.sort_values(['data_type', 'protein_id', 'model_number'])
        
        # Save to CSV
        output_csv = f"{CLUSTER_OUTPUT_DIR}/triple_overlap_analysis_summary_metrics.csv"
        df.to_csv(output_csv, index=False)
        
        print(f"\n✅ Successfully loaded {len(df)} predictions")
        print(f"📊 Data types: {df['data_type'].unique()}")
        print(f"📊 Unique proteins: {df['protein_id'].nunique()}")
        print(f"📊 Models per protein: {df.groupby(['data_type', 'protein_id']).size().describe()}")
        print(f"📊 Columns: {list(df.columns)}")
        
        return df
    else:
        print("❌ No data loaded")
        return pd.DataFrame()

def run_triple_overlap_analysis():
    """Run Triple Overlap R-Loop analysis on cluster"""
    
    print(f"\n🚀 STARTING TRIPLE OVERLAP R-LOOP ANALYSIS")
    print(f"Input directory: {CLUSTER_DATA_DIR}")
    print(f"Output directory: {CLUSTER_OUTPUT_DIR}")
    
    # Load data directly
    df = load_triple_overlap_data()
    
    if df is None or df.empty:
        print("❌ No data loaded for analysis")
        return None
    
    # Create the workflow
    print(f"\n🔄 CREATING WORKFLOW")
    workflow = AF3SummaryAnalysisWorkflow()
    
    # Run the analysis with the loaded DataFrame
    print(f"\n🔄 RUNNING TRIPLE OVERLAP ANALYSIS WORKFLOW")
    try:
        results = workflow.run_af3_analysis_workflow(
            input_source=df,  # Pass the DataFrame directly
            output_prefix=f"{CLUSTER_OUTPUT_DIR}/triple_overlap_analysis",
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

def generate_data_type_summary(df):
    """Generate summary statistics by data type"""
    print(f"\n📊 GENERATING DATA TYPE SUMMARY")
    
    if df.empty:
        print("❌ No data to summarize")
        return
    
    # Summary by data type
    summary_stats = []
    
    for data_type in df['data_type'].unique():
        type_data = df[df['data_type'] == data_type]
        
        stats = {
            'data_type': data_type,
            'total_predictions': len(type_data),
            'unique_proteins': type_data['protein_id'].nunique(),
            'avg_iptm': type_data['iptm'].mean() if 'iptm' in type_data.columns else None,
            'avg_ptm': type_data['ptm'].mean() if 'ptm' in type_data.columns else None,
            'avg_ranking_score': type_data['ranking_score'].mean() if 'ranking_score' in type_data.columns else None,
            'models_per_protein': len(type_data) / type_data['protein_id'].nunique()
        }
        
        summary_stats.append(stats)
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_stats)
    
    # Save summary
    summary_file = f"{CLUSTER_OUTPUT_DIR}/triple_overlap_data_type_summary.csv"
    summary_df.to_csv(summary_file, index=False)
    
    print(f"✅ Saved data type summary to: {summary_file}")
    print(f"\n📊 Summary by data type:")
    print(summary_df.to_string(index=False))
    
    return summary_df

if __name__ == "__main__":
    results = run_triple_overlap_analysis()
    
    if results and 'data_info' in results:
        print("\n✅ Triple Overlap R-Loop analysis completed successfully!")
        print(f"📁 Outputs saved to: {CLUSTER_OUTPUT_DIR}")
        print(f"📊 Total predictions analyzed: {results['data_info'].get('total_predictions', 0)}")
        
        # Generate additional summary if we have data
        if 'data_info' in results and results['data_info'].get('total_predictions', 0) > 0:
            # We need to reload the data for the summary since it's not in results
            df = load_triple_overlap_data()
            if not df.empty:
                generate_data_type_summary(df)
    else:
        print("\n❌ Triple Overlap R-Loop analysis failed!")
        print("Check the error messages above for details.") 