#!/usr/bin/env python3
"""
Debug script to test different import methods for alphafold_core
"""

import sys
import os

print("=== DEBUGGING ALPHAFOLD_CORE IMPORT ===")
print(f"📁 Current working directory: {os.getcwd()}")
print(f"🐍 Python executable: {sys.executable}")
print(f"📋 Original sys.path (first 5):")
for i, path in enumerate(sys.path[:5]):
    print(f"  {i}: {path}")

alphafold_core_path = '/data7/Conny/scripts/alphafold_core'

print(f"\n🔍 Checking alphafold_core path: {alphafold_core_path}")
print(f"Path exists: {os.path.exists(alphafold_core_path)}")

if os.path.exists(alphafold_core_path):
    print(f"Path is directory: {os.path.isdir(alphafold_core_path)}")
    print(f"Contents:")
    try:
        contents = os.listdir(alphafold_core_path)
        for item in contents:
            print(f"  - {item}")
    except Exception as e:
        print(f"  Error listing contents: {e}")

print(f"\n=== TESTING DIFFERENT IMPORT METHODS ===")

# Method 1: Direct import with path manipulation
print("\n1️⃣ Testing Method 1: Direct path manipulation")
try:
    # Clear sys.path and add only what we need
    original_path = sys.path.copy()
    sys.path = ['/data7/Conny/scripts/alphafold_core'] + [p for p in original_path if p != os.getcwd()]
    
    print(f"Modified sys.path (first 3):")
    for i, path in enumerate(sys.path[:3]):
        print(f"  {i}: {path}")
    
    import alphafold_core
    print("✅ Method 1: Basic import successful")
    
    from alphafold_core.pipeline.workflows import AF3SummaryAnalysisWorkflow
    print("✅ Method 1: Workflow import successful")
    
except Exception as e:
    print(f"❌ Method 1 failed: {e}")
    import traceback
    traceback.print_exc()

# Method 2: Using importlib
print("\n2️⃣ Testing Method 2: Using importlib")
try:
    import importlib.util
    import sys
    
    # Reset sys.path
    sys.path = original_path
    
    # Load module using importlib
    spec = importlib.util.spec_from_file_location(
        "alphafold_core", 
        os.path.join(alphafold_core_path, "__init__.py")
    )
    alphafold_core = importlib.util.module_from_spec(spec)
    sys.modules["alphafold_core"] = alphafold_core
    spec.loader.exec_module(alphafold_core)
    
    print("✅ Method 2: importlib import successful")
    
except Exception as e:
    print(f"❌ Method 2 failed: {e}")
    import traceback
    traceback.print_exc()

# Method 3: Using exec
print("\n3️⃣ Testing Method 3: Using exec")
try:
    # Reset sys.path
    sys.path = original_path
    
    # Add to path and import
    sys.path.insert(0, alphafold_core_path)
    
    # Try importing with exec
    exec("import alphafold_core")
    print("✅ Method 3: exec import successful")
    
except Exception as e:
    print(f"❌ Method 3 failed: {e}")
    import traceback
    traceback.print_exc()

# Method 4: Check if it's a Python path issue
print("\n4️⃣ Testing Method 4: Check module structure")
try:
    # Reset sys.path
    sys.path = original_path
    
    # Check if __init__.py exists and is readable
    init_file = os.path.join(alphafold_core_path, "__init__.py")
    print(f"__init__.py exists: {os.path.exists(init_file)}")
    print(f"__init__.py readable: {os.access(init_file, os.R_OK)}")
    
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            content = f.read()
            print(f"__init__.py content (first 100 chars): {content[:100]}")
    
    # Try importing from parent directory
    parent_dir = os.path.dirname(alphafold_core_path)
    sys.path.insert(0, parent_dir)
    
    import alphafold_core
    print("✅ Method 4: Import from parent directory successful")
    
except Exception as e:
    print(f"❌ Method 4 failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== FINAL DIAGNOSIS ===")
print("If all methods failed, the issue might be:")
print("1. Python environment differences")
print("2. Module structure issues")
print("3. Permission issues")
print("4. Path encoding issues") 