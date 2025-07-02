#!/usr/bin/env python3
"""
Test script to verify alphafold_core import works from cluster directory
"""

import sys
import os

print(f"📁 Current working directory: {os.getcwd()}")

# Add alphafold_core to Python path
alphafold_core_path = '/data7/Conny/scripts/alphafold_core'

# Check if path exists
if not os.path.exists(alphafold_core_path):
    print(f"❌ alphafold_core path does not exist: {alphafold_core_path}")
    sys.exit(1)

# Add to Python path
sys.path.insert(0, alphafold_core_path)

print(f"🔍 Looking for alphafold_core at: {alphafold_core_path}")
print(f"✅ Added to Python path: {alphafold_core_path}")

try:
    # Test basic import
    import alphafold_core
    print("✅ Basic alphafold_core import successful")
    
    # Test specific imports
    from alphafold_core.pipeline.workflows import AF3SummaryAnalysisWorkflow
    print("✅ AF3SummaryAnalysisWorkflow import successful")
    
    from alphafold_core.data.processor import JSONProcessor
    print("✅ JSONProcessor import successful")
    
    from alphafold_core.analysis.quality import QualityAnalyzer
    print("✅ QualityAnalyzer import successful")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    print(f"Python path: {sys.path[:3]}")
    sys.exit(1) 