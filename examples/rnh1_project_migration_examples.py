#!/usr/bin/env python3
"""
RNH1 Project Migration Examples

This script demonstrates how to migrate workflows from the RNH1_Q40740_Collab_Project
to the new alphafold_core hierarchical system. Each example shows the old way vs new way.
"""

import sys
from pathlib import Path

# Add the alphafold_core package to the path
sys.path.append(str(Path(__file__).parent.parent))

from alphafold_core.data import ProteinSequenceFetcher, DataProcessor
from alphafold_core.pipeline import GeneToProteinPipeline, OrganizedWorkflowManager
from alphafold_core.analysis import OverlapAnalyzer
from alphafold_core.visualization import PlotGenerator


def example_1_sequence_extraction_migration():
    """
    Example 1: Sequence Extraction Migration
    
    OLD WAY: Manual API calls in SequenceExtract.ipynb
    NEW WAY: Using ProteinSequenceFetcher
    """
    print("=== Example 1: Sequence Extraction Migration ===")
    
    # OLD WAY (from SequenceExtract.ipynb)
    print("OLD WAY (SequenceExtract.ipynb):")
    print("""
import requests
import pandas as pd

# Manual API calls
def fetch_sequence(protein_id):
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}"
    response = requests.get(url, headers=headers, params=params)
    if response.ok:
        data = response.json()
        sequence_info = data.get("sequence", {})
        return sequence_info.get("value", None)
    return None

# Manual processing
data = pd.read_excel("WT untagged_vs_RNH1.xlsx")
protein_ids = data['Protein.Ids']
results = {}
for entry in protein_ids:
    ids = entry.split(";")
    for protein_id in ids:
        protein_id = protein_id.strip()
        if protein_id and protein_id not in results:
            sequence = fetch_sequence(protein_id)
            if sequence:
                results[protein_id] = sequence

# Manual FASTA writing
with open("unique_protein_sequences.fasta", "w") as file:
    for protein_id, sequence in results.items():
        file.write(f">{protein_id}\\n{sequence}\\n")
""")
    
    # NEW WAY (using alphafold_core)
    print("\nNEW WAY (alphafold_core):")
    print("""
from alphafold_core.data import ProteinSequenceFetcher

# Simple one-liner
fetcher = ProteinSequenceFetcher()
sequences = fetcher.fetch_from_excel(
    "WT untagged_vs_RNH1.xlsx", 
    "Protein.Ids"
)
""")
    
    # Demonstrate the new way
    print("\n✅ Benefits of NEW WAY:")
    print("   - Built-in rate limiting and error handling")
    print("   - Automatic duplicate removal")
    print("   - Progress tracking with tqdm")
    print("   - Comprehensive logging")
    print("   - Reusable component")


def example_2_json_generation_migration():
    """
    Example 2: JSON Generation Migration
    
    OLD WAY: Manual JSON generation scripts
    NEW WAY: Using DataProcessor
    """
    print("\n=== Example 2: JSON Generation Migration ===")
    
    # OLD WAY (from AlphaFold3_JSON_generator.py)
    print("OLD WAY (AlphaFold3_JSON_generator.py):")
    print("""
import json

# Manual JSON structure creation
def create_alphafold_json(protein_id, sequence):
    job = {
        "name": f"Protein: {protein_id}",
        "modelSeeds": [],
        "sequences": [
            {
                "proteinChain": {
                    "sequence": sequence,
                    "count": 1,
                    "useStructureTemplate": False
                }
            }
        ],
        "dialect": "alphafoldserver",
        "version": 1
    }
    return job

# Manual file handling
jobs = []
for protein_id, sequence in sequences.items():
    job = create_alphafold_json(protein_id, sequence)
    jobs.append(job)

with open("alphafold_jobs.json", "w") as f:
    json.dump(jobs, f, indent=2)
""")
    
    # NEW WAY (using alphafold_core)
    print("\nNEW WAY (alphafold_core):")
    print("""
from alphafold_core.data import DataProcessor

# Automatic JSON generation
processor = DataProcessor()
output_files = processor.process_gene_to_protein_data(
    gene_protein_data, 
    "rnh1_workflow"
)
# Generates: rnh1_workflow_alphafold.json
""")
    
    # Demonstrate the new way
    print("\n✅ Benefits of NEW WAY:")
    print("   - Automatic job name formatting (no pipe characters)")
    print("   - Multiple output formats (CSV, FASTA, JSON)")
    print("   - Built-in validation")
    print("   - Summary statistics")
    print("   - Error handling for missing sequences")


def example_3_result_analysis_migration():
    """
    Example 3: Result Analysis Migration
    
    OLD WAY: Manual result processing scripts
    NEW WAY: Using analysis modules
    """
    print("\n=== Example 3: Result Analysis Migration ===")
    
    # OLD WAY (from AF3_Result_Table.py)
    print("OLD WAY (AF3_Result_Table.py):")
    print("""
import pandas as pd
import json

# Manual result parsing
def process_af3_results(result_file):
    with open(result_file, 'r') as f:
        data = json.load(f)
    
    results = []
    for job in data:
        result = {
            'job_name': job['name'],
            'plddt': job.get('plddt', 0),
            'iptm': job.get('iptm', 0),
            'ptm': job.get('ptm', 0)
        }
        results.append(result)
    
    df = pd.DataFrame(results)
    df.to_csv('af3_results.csv', index=False)
    return df
""")
    
    # NEW WAY (using alphafold_core)
    print("\nNEW WAY (alphafold_core):")
    print("""
from alphafold_core.analysis import QualityAnalyzer

# Automated result analysis
analyzer = QualityAnalyzer()
results = analyzer.analyze_alphafold_results(
    result_directory="af3_results/",
    output_prefix="rnh1_analysis"
)
""")
    
    # Demonstrate the new way
    print("\n✅ Benefits of NEW WAY:")
    print("   - Automatic result parsing")
    print("   - Quality assessment metrics")
    print("   - Statistical analysis")
    print("   - Multiple output formats")
    print("   - Built-in filtering options")


def example_4_overlap_analysis_migration():
    """
    Example 4: Overlap Analysis Migration
    
    OLD WAY: Manual overlap analysis scripts
    NEW WAY: Using OverlapAnalyzer
    """
    print("\n=== Example 4: Overlap Analysis Migration ===")
    
    # OLD WAY (from analyze_overlap.py)
    print("OLD WAY (analyze_overlap.py):")
    print("""
import pandas as pd

# Manual overlap calculation
def analyze_overlap(af3_data, afp_data):
    af3_proteins = set(af3_data['protein_id'].unique())
    afp_proteins = set(afp_data['protein_id'].unique())
    
    overlap = af3_proteins.intersection(afp_proteins)
    overlap_count = len(overlap)
    
    print(f"AF3 proteins: {len(af3_proteins)}")
    print(f"AFP proteins: {len(afp_proteins)}")
    print(f"Overlap: {overlap_count}")
    
    return overlap
""")
    
    # NEW WAY (using alphafold_core)
    print("\nNEW WAY (alphafold_core):")
    print("""
from alphafold_core.analysis import OverlapAnalyzer

# Automated overlap analysis
analyzer = OverlapAnalyzer()
overlap_results = analyzer.analyze_overlaps(
    datasets={
        'alphafold3': 'af3_results.csv',
        'alphapulldown': 'afp_results.csv'
    },
    id_columns={
        'alphafold3': 'protein_id',
        'alphapulldown': 'protein_id'
    },
    output_prefix="rnh1_overlap"
)
""")
    
    # Demonstrate the new way
    print("\n✅ Benefits of NEW WAY:")
    print("   - Automatic overlap calculation")
    print("   - Statistical significance testing")
    print("   - Visualization generation")
    print("   - Multiple dataset support")
    print("   - Detailed reporting")


def example_5_complete_workflow_migration():
    """
    Example 5: Complete Workflow Migration
    
    OLD WAY: Multiple scattered scripts
    NEW WAY: Single organized workflow
    """
    print("\n=== Example 5: Complete Workflow Migration ===")
    
    # OLD WAY (multiple scripts)
    print("OLD WAY (Multiple scattered scripts):")
    print("""
# Step 1: Run SequenceExtract.ipynb
# Step 2: Run AlphaFold3_JSON_generator.py
# Step 3: Run AF3_Result_Table.py
# Step 4: Run analyze_overlap.py
# Step 5: Manual file organization
""")
    
    # NEW WAY (organized workflow)
    print("\nNEW WAY (Organized workflow):")
    print("""
from alphafold_core.pipeline import OrganizedWorkflowManager

# Single organized workflow
workflow_manager = OrganizedWorkflowManager()
results = workflow_manager.run_gene_to_protein_workflow(
    input_file="WT untagged_vs_RNH1.xlsx",
    output_prefix="rnh1_complete_workflow",
    split_json=True,
    jobs_per_batch=30
)
""")
    
    # Demonstrate the new way
    print("\n✅ Benefits of NEW WAY:")
    print("   - Single command execution")
    print("   - Organized output directories")
    print("   - Automatic batch splitting")
    print("   - Comprehensive logging")
    print("   - Workflow summary generation")


def demonstrate_migration():
    """Demonstrate the migration examples"""
    print("RNH1 Project Migration Examples")
    print("=" * 50)
    print("This demonstrates how to migrate from scattered scripts")
    print("to the new alphafold_core hierarchical system.\n")
    
    # Run all migration examples
    example_1_sequence_extraction_migration()
    example_2_json_generation_migration()
    example_3_result_analysis_migration()
    example_4_overlap_analysis_migration()
    example_5_complete_workflow_migration()
    
    print("\n" + "=" * 50)
    print("🎉 Migration Examples Complete!")
    print("The new alphafold_core system provides:")
    print("   ✅ Better error handling and logging")
    print("   ✅ Reusable components")
    print("   ✅ Organized outputs")
    print("   ✅ Configuration management")
    print("   ✅ Comprehensive testing capabilities")


if __name__ == "__main__":
    demonstrate_migration() 