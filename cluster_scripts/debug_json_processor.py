#!/usr/bin/env python3
"""
Debug script to test JSON processor methods directly
"""

import sys
import os
from pathlib import Path

# Add alphafold_core to Python path
sys.path.append('/data7/Conny/scripts/alphafold_core')

from alphafold_core.data.processor import JSONProcessor

# Test directory
TEST_DIR = "/data7/Conny/Dicer"

def test_process_directory():
    """Test the process_directory method"""
    print("\n🔧 TESTING process_directory METHOD")
    
    json_processor = JSONProcessor()
    test_dir = Path(TEST_DIR)
    
    print(f"Testing with directory: {test_dir}")
    print(f"Directory exists: {test_dir.exists()}")
    print(f"Directory is dir: {test_dir.is_dir()}")
    
    try:
        # Test with default pattern
        df = json_processor.process_directory(test_dir, "*_summary_confidences_0.json")
        print(f"Result: {len(df)} rows loaded")
        if not df.empty:
            print(f"Columns: {list(df.columns)}")
            print(f"First few rows:")
            print(df.head())
        else:
            print("❌ No data loaded")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_process_af3_results():
    """Test the process_af3_results method"""
    print("\n🔧 TESTING process_af3_results METHOD")
    
    json_processor = JSONProcessor()
    test_dir = Path(TEST_DIR)
    
    try:
        df, missing_report = json_processor.process_af3_results(test_dir, "debug_output.csv")
        print(f"Result: {len(df)} rows loaded")
        if not df.empty:
            print(f"Columns: {list(df.columns)}")
            print(f"First few rows:")
            print(df.head())
        else:
            print("❌ No data loaded")
        
        print(f"Missing report: {missing_report}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_find_json_files():
    """Test finding JSON files manually"""
    print("\n🔧 TESTING MANUAL JSON FILE SEARCH")
    
    test_dir = Path(TEST_DIR)
    
    # Test different patterns
    patterns = [
        "*_summary_confidences_0.json",
        "*summary_confidences*.json",
        "*.json"
    ]
    
    for pattern in patterns:
        print(f"\nSearching for pattern: {pattern}")
        try:
            from alphafold_core.utils import find_json_files
            files = find_json_files(test_dir, pattern)
            print(f"Found {len(files)} files")
            if files:
                print("First 5 files:")
                for file in files[:5]:
                    print(f"  • {file}")
                if len(files) > 5:
                    print(f"  • ... and {len(files) - 5} more")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_specific_fold_directory():
    """Test processing a specific fold directory"""
    print("\n🔧 TESTING SPECIFIC FOLD DIRECTORY")
    
    test_dir = Path(TEST_DIR)
    
    # Find a fold directory
    fold_dirs = [d for d in test_dir.iterdir() if d.is_dir() and d.name.startswith("folds_")]
    if fold_dirs:
        sample_fold = fold_dirs[0]
        print(f"Testing fold directory: {sample_fold}")
        
        json_processor = JSONProcessor()
        try:
            df = json_processor.process_directory(sample_fold, "*_summary_confidences_0.json")
            print(f"Result: {len(df)} rows loaded")
            if not df.empty:
                print(f"Columns: {list(df.columns)}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ No fold directories found")

if __name__ == "__main__":
    print("🚀 STARTING JSON PROCESSOR DEBUG")
    
    test_find_json_files()
    test_process_directory()
    test_process_af3_results()
    test_specific_fold_directory()
    
    print("\n✅ Debug completed!") 