#!/usr/bin/env python3
"""
Run Full Robust Gene-to-Protein Workflow

This script runs the robust gene-to-protein conversion workflow
on the actual TSV file with 685 genes.
"""

import sys
from pathlib import Path

# Add the alphafold_core package to the path
sys.path.append(str(Path(__file__).parent))

from alphafold_core.pipeline import GeneToProteinPipeline

def main():
    """Run the full robust workflow on the actual TSV file"""
    print("🧬 Running Full Robust Gene-to-Protein Workflow")
    print("=" * 60)
    
    # Initialize the pipeline
    pipeline = GeneToProteinPipeline()
    
    # Use the actual TSV file path
    tsv_file = "/Users/conny/Desktop/AlphaFold/Project/Dicer_685_Project/venn2_overlap.tsv"
    
    print(f"📁 Input file: {tsv_file}")
    print(f"🔍 Search criteria: Human (9606), Reviewed only, Exact match")
    print(f"⏳ This may take several minutes for 685 genes...")
    print()
    
    try:
        # Run the robust workflow
        results = pipeline.run_gene_to_protein_workflow_robust(
            tsv_file=tsv_file,
            gene_column="GENE",  # Based on the file structure we saw earlier
            output_prefix="full_robust_workflow",
            organism_id="9606",  # Human
            reviewed_only=True,   # Only reviewed entries
            exact_match=True      # Exact gene name matching
        )
        
        print(f"\n✅ Workflow completed successfully!")
        print(f"\n📊 Results Summary:")
        print(f"   - Total genes processed: {results['workflow_summary']['total_genes_processed']}")
        print(f"   - Successful matches: {results['workflow_summary']['successful_protein_matches']}")
        print(f"   - Success rate: {results['workflow_summary']['success_rate']:.1f}%")
        print(f"   - Genes with multiple results: {results['workflow_summary']['genes_with_multiple_results']}")
        print(f"   - Multiple results rate: {results['workflow_summary']['multiple_results_rate']:.1f}%")
        
        print(f"\n🔍 Search Criteria Used:")
        print(f"   - Organism: Human (9606)")
        print(f"   - Reviewed only: {results['search_criteria']['reviewed_only']}")
        print(f"   - Exact match: {results['search_criteria']['exact_match']}")
        
        print(f"\n📁 Output Files Generated:")
        for file_type, file_path in results['output_files'].items():
            print(f"   - {file_type}: {file_path}")
        
        print(f"\n🎉 All done! Check the output files for your results.")
        
    except Exception as e:
        print(f"❌ Error during workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 