#!/usr/bin/env python3
"""
Debug script for Triple Overlap R-Loop data loading
Tests the data loading functionality without running the full workflow
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
    from alphafold_core.data.processor import JSONProcessor
    print("✅ Successfully imported alphafold_core modules")
except ImportError as e:
    print(f"❌ Failed to import alphafold_core: {e}")
    print("Please check if alphafold_core is installed at the specified path")
    print(f"Python path: {sys.path[:3]}")
    sys.exit(1)

# Cluster-specific configuration for Triple Overlap R-Loop
CLUSTER_DATA_DIR = "/data7/Conny/Projects/Triple_Overlap_RLoop/data/26_Overlap"
CLUSTER_OUTPUT_DIR = "/data7/Conny/Projects/Triple_Overlap_RLoop/results"

def debug_directory_structure():
    """Debug the directory structure"""
    print(f"\n🔍 DEBUGGING DIRECTORY STRUCTURE")
    print(f"Data directory: {CLUSTER_DATA_DIR}")
    
    data_dir = Path(CLUSTER_DATA_DIR)
    
    if not data_dir.exists():
        print(f"❌ Directory does not exist: {CLUSTER_DATA_DIR}")
        return False
    
    if not data_dir.is_dir():
        print(f"❌ Path is not a directory: {CLUSTER_DATA_DIR}")
        return False
    
    print(f"✅ Directory exists and is accessible")
    
    # List all data type directories
    data_types = [d for d in data_dir.iterdir() if d.is_dir()]
    print(f"Found {len(data_types)} data type directories:")
    
    for data_type in data_types:
        print(f"  📂 {data_type.name}")
        
        # Count protein directories
        protein_dirs = [d for d in data_type.iterdir() if d.is_dir() and not d.name.endswith('.md')]
        print(f"    └── {len(protein_dirs)} protein directories")
        
        # Show first few protein directories
        for protein_dir in protein_dirs[:3]:
            print(f"       • {protein_dir.name}")
            
            # Check for summary files
            summary_files = list(protein_dir.glob("*_summary_confidences_*.json"))
            print(f"         └── {len(summary_files)} summary files")
            
            if summary_files:
                # Show first few summary files
                for summary_file in summary_files[:3]:
                    print(f"            - {summary_file.name}")
                if len(summary_files) > 3:
                    print(f"            - ... and {len(summary_files) - 3} more")
        
        if len(protein_dirs) > 3:
            print(f"       • ... and {len(protein_dirs) - 3} more protein directories")
    
    return True

def test_data_loading():
    """Test loading data from one data type"""
    print(f"\n🧪 TESTING DATA LOADING")
    
    data_dir = Path(CLUSTER_DATA_DIR)
    
    # Test with one data type (dsRNA)
    test_data_type = "dsRNA"
    test_data_type_dir = data_dir / test_data_type
    
    if not test_data_type_dir.exists():
        print(f"❌ Test data type directory does not exist: {test_data_type_dir}")
        return None
    
    print(f"Testing with data type: {test_data_type}")
    
    # Find protein directories
    protein_dirs = [d for d in test_data_type_dir.iterdir() if d.is_dir() and not d.name.endswith('.md')]
    print(f"Found {len(protein_dirs)} protein directories")
    
    data_rows = []
    
    # Process first few protein directories for testing
    for protein_dir in protein_dirs[:5]:  # Test with first 5
        # Extract protein ID and type from directory name
        match = re.match(r'([a-zA-Z0-9]+)_([a-z]+)', protein_dir.name)
        if not match:
            print(f"⚠️  Skipping directory with unexpected name: {protein_dir.name}")
            continue
            
        protein_id = match.group(1)
        protein_type = match.group(2)
        
        print(f"  Processing {protein_id} ({protein_type})")
        
        # Look for summary confidence files
        summary_files = list(protein_dir.glob("*_summary_confidences_*.json"))
        
        if not summary_files:
            print(f"    ⚠️  No summary files found")
            continue
        
        print(f"    📄 Found {len(summary_files)} summary files")
        
        # Process each summary file
        for summary_file in summary_files:
            try:
                with open(summary_file, 'r') as f:
                    content = json.load(f)
                
                # Extract model number from filename
                model_match = re.search(r'summary_confidences_(\d+)\.json$', summary_file.name)
                model_num = int(model_match.group(1)) if model_match else 0
                
                row = {
                    'data_type': test_data_type,
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
                print(f"      ✅ Processed model {model_num}")
                
            except Exception as e:
                print(f"      ❌ Error processing {summary_file}: {e}")
                continue
    
    # Create DataFrame
    if data_rows:
        df = pd.DataFrame(data_rows)
        
        # Sort by protein ID and model number
        df = df.sort_values(['protein_id', 'model_number'])
        
        print(f"\n✅ Successfully loaded {len(df)} predictions from test")
        print(f"📊 Unique proteins: {df['protein_id'].nunique()}")
        print(f"📊 Models per protein: {df.groupby('protein_id').size().describe()}")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Show sample data
        print(f"\n📋 Sample data:")
        print(df.head().to_string())
        
        return df
    else:
        print("❌ No data loaded from test")
        return pd.DataFrame()

def test_json_processor():
    """Test the JSON processor with the new data structure"""
    print(f"\n🔧 TESTING JSON PROCESSOR")
    
    json_processor = JSONProcessor()
    data_dir = Path(CLUSTER_DATA_DIR)
    
    # Test process_directory method
    print(f"Testing process_directory with pattern '*_summary_confidences_0.json':")
    try:
        df = json_processor.process_directory(data_dir, "*_summary_confidences_0.json")
        print(f"  Result: {len(df)} rows loaded")
        if not df.empty:
            print(f"  Columns: {list(df.columns)}")
            print(f"  Sample data:")
            print(df.head().to_string())
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test process_triple_overlap_json_files method
    print(f"\nTesting process_triple_overlap_json_files:")
    try:
        df = json_processor.process_triple_overlap_json_files(data_dir)
        print(f"  Result: {len(df)} rows loaded")
        if not df.empty:
            print(f"  Columns: {list(df.columns)}")
            print(f"  Sample data:")
            print(df.head().to_string())
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 STARTING TRIPLE OVERLAP R-LOOP DEBUG")
    
    # Debug directory structure
    if debug_directory_structure():
        # Test data loading
        test_df = test_data_loading()
        
        # Test JSON processor
        test_json_processor()
        
        if test_df is not None and not test_df.empty:
            print(f"\n✅ Debug completed successfully!")
            print(f"📊 Test loaded {len(test_df)} predictions")
        else:
            print(f"\n⚠️  Debug completed but no data was loaded")
    else:
        print(f"\n❌ Debug failed - directory structure issues") 