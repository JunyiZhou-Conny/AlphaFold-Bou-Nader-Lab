#!/usr/bin/env python3
"""
Gene to Protein Workflow Demonstration

This script demonstrates how to use the new hierarchical structure
to process TSV files with gene names and convert them to protein data
in multiple formats (CSV, FASTA, JSON for AlphaFold).

Now includes robust search strategies with configurable criteria.
"""

import sys
from pathlib import Path

# Add the alphafold_core package to the path
sys.path.append(str(Path(__file__).parent.parent))

from alphafold_core.pipeline import GeneToProteinPipeline
from alphafold_core.data import ProteinSequenceFetcher, DataProcessor, SearchCriteria
from alphafold_core.config import config


def demonstrate_simple_workflow():
    """Demonstrate the simple workflow using the pipeline"""
    print("=== Simple Gene-to-Protein Workflow ===")
    
    # Initialize the pipeline
    pipeline = GeneToProteinPipeline()
    
    # Run the complete workflow
    results = pipeline.run_gene_to_protein_workflow(
        tsv_file="Summer Project/data/venn2_overlap.tsv",
        gene_column="GENE",
        output_prefix="demo_workflow"
    )
    
    print(f"✅ Workflow completed!")
    print(f"📊 Results:")
    print(f"   - Total genes processed: {results['workflow_summary']['total_genes_processed']}")
    print(f"   - Successful matches: {results['workflow_summary']['successful_protein_matches']}")
    print(f"   - Success rate: {results['workflow_summary']['success_rate']:.1f}%")
    print(f"📁 Output files generated:")
    for file_type, file_path in results['output_files'].items():
        print(f"   - {file_type}: {file_path}")
    
    return results


def demonstrate_robust_workflow():
    """Demonstrate the robust workflow with configurable search criteria"""
    print("\n=== Robust Gene-to-Protein Workflow ===")
    print("Using enhanced search strategies with fallback mechanisms")
    
    # Initialize the pipeline
    pipeline = GeneToProteinPipeline()
    
    # Run the robust workflow with specific criteria for human proteins
    results = pipeline.run_gene_to_protein_workflow_robust(
        tsv_file="Summer Project/data/venn2_overlap.tsv",
        gene_column="GENE",
        output_prefix="demo_robust_workflow",
        organism_id="9606",  # Human
        reviewed_only=True,   # Only reviewed entries
        exact_match=True      # Exact gene name matching
    )
    
    print(f"✅ Robust workflow completed!")
    print(f"🔍 Search Criteria:")
    print(f"   - Organism: Human (9606)")
    print(f"   - Reviewed only: {results['search_criteria']['reviewed_only']}")
    print(f"   - Exact match: {results['search_criteria']['exact_match']}")
    print(f"📊 Results:")
    print(f"   - Total genes processed: {results['workflow_summary']['total_genes_processed']}")
    print(f"   - Successful matches: {results['workflow_summary']['successful_protein_matches']}")
    print(f"   - Success rate: {results['workflow_summary']['success_rate']:.1f}%")
    print(f"   - Genes with multiple results: {results['workflow_summary']['genes_with_multiple_results']}")
    print(f"   - Multiple results rate: {results['workflow_summary']['multiple_results_rate']:.1f}%")
    print(f"📁 Output files generated:")
    for file_type, file_path in results['output_files'].items():
        print(f"   - {file_type}: {file_path}")
    
    return results


def demonstrate_step_by_step():
    """Demonstrate the workflow step by step for better understanding"""
    print("\n=== Step-by-Step Workflow ===")
    
    # Step 1: Initialize components
    print("Step 1: Initializing components...")
    fetcher = ProteinSequenceFetcher()
    processor = DataProcessor()
    
    # Step 2: Parse TSV and extract gene names
    print("Step 2: Parsing TSV file...")
    gene_protein_data = fetcher.process_genes_to_proteins(
        "Summer Project/data/venn2_overlap.tsv",
        "GENE"
    )
    
    print(f"   Found {len(gene_protein_data)} genes")
    successful = len([d for d in gene_protein_data.values() if "error" not in d])
    print(f"   Successfully matched: {successful} genes")
    
    # Step 3: Process data into multiple formats
    print("Step 3: Generating output files...")
    output_files = processor.process_gene_to_protein_data(
        gene_protein_data,
        "step_by_step_demo"
    )
    
    print(f"   Generated {len(output_files)} output files:")
    for file_type, file_path in output_files.items():
        print(f"     - {file_type}: {file_path}")
    
    return gene_protein_data, output_files


def demonstrate_step_by_step_robust():
    """Demonstrate the robust workflow step by step"""
    print("\n=== Step-by-Step Robust Workflow ===")
    
    # Step 1: Initialize components
    print("Step 1: Initializing components...")
    fetcher = ProteinSequenceFetcher()
    processor = DataProcessor()
    
    # Step 2: Create search criteria for human proteins
    print("Step 2: Setting up robust search criteria...")
    criteria = SearchCriteria(
        organism_id="9606",      # Human
        reviewed_only=True,       # Only reviewed entries
        exact_match=True,         # Exact gene name matching
        max_results=10            # Get up to 10 results for fallback
    )
    print(f"   - Organism: Human (9606)")
    print(f"   - Reviewed only: {criteria.reviewed_only}")
    print(f"   - Exact match: {criteria.exact_match}")
    
    # Step 3: Parse TSV and extract gene names with robust search
    print("Step 3: Parsing TSV file and searching UniProt with robust strategies...")
    gene_protein_data = fetcher.process_genes_to_proteins_robust(
        "Summer Project/data/venn2_overlap.tsv",
        "GENE",
        criteria
    )
    
    print(f"   Found {len(gene_protein_data)} genes")
    successful = len([d for d in gene_protein_data.values() if "error" not in d])
    print(f"   Successfully matched: {successful} genes")
    
    # Step 4: Process data into multiple formats
    print("Step 4: Generating output files...")
    output_files = processor.process_gene_to_protein_data(
        gene_protein_data,
        "step_by_step_robust_demo"
    )
    
    print(f"   Generated {len(output_files)} output files:")
    for file_type, file_path in output_files.items():
        print(f"     - {file_type}: {file_path}")
    
    return gene_protein_data, output_files


def demonstrate_batch_processing():
    """Demonstrate batch processing of multiple files"""
    print("\n=== Batch Processing Demo ===")
    
    # For demo purposes, we'll use the same file multiple times
    # In real usage, you'd have different TSV files
    tsv_files = [
        "Summer Project/data/venn2_overlap.tsv"
    ]
    
    pipeline = GeneToProteinPipeline()
    
    # Run batch processing
    batch_results = pipeline.run_batch_processing(
        tsv_files=tsv_files,
        gene_column="GENE",
        output_dir="batch_demo_results"
    )
    
    print(f"✅ Batch processing completed!")
    print(f"📊 Batch Summary:")
    print(f"   - Files processed: {batch_results['batch_summary']['total_files']}")
    print(f"   - Successful files: {batch_results['batch_summary']['successful_files']}")
    print(f"   - Total genes: {batch_results['batch_summary']['total_genes_processed']}")
    print(f"   - Overall success rate: {batch_results['batch_summary']['overall_success_rate']:.1f}%")
    
    return batch_results


def demonstrate_batch_processing_robust():
    """Demonstrate robust batch processing of multiple files"""
    print("\n=== Robust Batch Processing Demo ===")
    
    # For demo purposes, we'll use the same file multiple times
    # In real usage, you'd have different TSV files
    tsv_files = [
        "Summer Project/data/venn2_overlap.tsv"
    ]
    
    pipeline = GeneToProteinPipeline()
    
    # Run robust batch processing with human-specific criteria
    batch_results = pipeline.run_batch_processing_robust(
        tsv_files=tsv_files,
        gene_column="GENE",
        output_dir="batch_robust_demo_results",
        organism_id="9606",      # Human
        reviewed_only=True,       # Only reviewed entries
        exact_match=True          # Exact gene name matching
    )
    
    print(f"✅ Robust batch processing completed!")
    print(f"🔍 Search Criteria:")
    print(f"   - Organism: Human (9606)")
    print(f"   - Reviewed only: {batch_results['search_criteria']['reviewed_only']}")
    print(f"   - Exact match: {batch_results['search_criteria']['exact_match']}")
    print(f"📊 Batch Summary:")
    print(f"   - Files processed: {batch_results['batch_summary']['total_files']}")
    print(f"   - Successful files: {batch_results['batch_summary']['successful_files']}")
    print(f"   - Total genes: {batch_results['batch_summary']['total_genes_processed']}")
    print(f"   - Overall success rate: {batch_results['batch_summary']['overall_success_rate']:.1f}%")
    
    return batch_results


def show_output_file_contents():
    """Show what the output files look like"""
    print("\n=== Output File Examples ===")
    
    # Check if demo files exist
    csv_file = "demo_robust_workflow.csv"
    fasta_file = "demo_robust_workflow.fasta"
    json_file = "demo_robust_workflow_alphafold.json"
    multiple_results_file = "demo_robust_workflow_multiple_results.csv"
    summary_file = "demo_robust_workflow_summary.json"
    
    if Path(csv_file).exists():
        print(f"📄 CSV file preview ({csv_file}):")
        import pandas as pd
        df = pd.read_csv(csv_file)
        print(df.head(3).to_string())
        print(f"   ... and {len(df) - 3} more rows")
        
        # Show multiple results information
        multiple_results = df[df['multiple_results_found'] == True]
        if len(multiple_results) > 0:
            print(f"\n🔍 Genes with multiple results found: {len(multiple_results)}")
            print("   These genes had multiple UniProt matches and may need manual review:")
            for _, row in multiple_results.head(3).iterrows():
                print(f"   - {row['gene_name']}: {row['selected_result']} (Total: {row['total_results']})")
            if len(multiple_results) > 3:
                print(f"   ... and {len(multiple_results) - 3} more genes with multiple results")
    
    if Path(multiple_results_file).exists():
        print(f"\n📋 Multiple results details ({multiple_results_file}):")
        import pandas as pd
        multi_df = pd.read_csv(multiple_results_file)
        if len(multi_df) > 0:
            print(f"   Found {len(multi_df)} genes with multiple results")
            print("   First few entries:")
            for _, row in multi_df.head(2).iterrows():
                print(f"   - {row['gene_name']}: Selected {row['selected_accession']}")
                print(f"     All options: {', '.join(row['all_accessions'][:3])}{'...' if len(row['all_accessions']) > 3 else ''}")
    
    if Path(summary_file).exists():
        print(f"\n📊 Summary file preview ({summary_file}):")
        import json
        with open(summary_file, 'r') as f:
            summary = json.load(f)
            print(f"   - Total genes: {summary.get('total_genes_processed', 'N/A')}")
            print(f"   - Success rate: {summary.get('success_rate', 0):.1f}%")
            print(f"   - Genes with multiple results: {summary.get('genes_with_multiple_results', 0)}")
            print(f"   - Multiple results rate: {summary.get('multiple_results_rate', 0):.1f}%")
    
    if Path(fasta_file).exists():
        print(f"\n🧬 FASTA file preview ({fasta_file}):")
        with open(fasta_file, 'r') as f:
            lines = f.readlines()[:6]  # First 3 entries
            for line in lines:
                print(f"   {line.rstrip()}")
        print("   ... and more sequences")
    
    if Path(json_file).exists():
        print(f"\n🔧 AlphaFold JSON file preview ({json_file}):")
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
            if data:
                print(f"   Contains {len(data)} AlphaFold job entries")
                print(f"   First job name: {data[0]['name']}")
                print(f"   Sequence length: {len(data[0]['sequences'][0]['proteinChain']['sequence'])}")


def compare_with_old_approach():
    """Compare the new approach with the old scattered scripts approach"""
    print("\n=== Comparison: New vs Old Approach ===")
    
    print("🔴 OLD APPROACH (Scattered Scripts):")
    print("   ❌ One massive script with hard-coded paths")
    print("   ❌ Mixed concerns (parsing, API calls, file I/O)")
    print("   ❌ Difficult to test individual components")
    print("   ❌ Hard to reuse parts for other projects")
    print("   ❌ No error handling or logging")
    print("   ❌ Manual file format conversion")
    print("   ❌ Basic gene search without fallback strategies")
    
    print("\n🟢 NEW APPROACH (Hierarchical Structure):")
    print("   ✅ Modular design with clear separation of concerns")
    print("   ✅ Reusable components (fetcher, processor, pipeline)")
    print("   ✅ Built-in error handling and retry logic")
    print("   ✅ Comprehensive logging and progress tracking")
    print("   ✅ Multiple output formats generated automatically")
    print("   ✅ Easy to test individual components")
    print("   ✅ Configuration management (no hard-coded paths)")
    print("   ✅ High-level pipelines for complex workflows")
    print("   ✅ Robust search strategies with fallback mechanisms")
    print("   ✅ Configurable search criteria (organism, reviewed status, etc.)")


def compare_search_strategies():
    """Compare different search strategies"""
    print("\n=== Search Strategy Comparison ===")
    
    print("🔍 ROBUST SEARCH STRATEGIES:")
    print("   Strategy 1: gene_exact:NAME AND organism_id:9606 AND reviewed:true")
    print("   Strategy 2: gene_exact:NAME AND organism_id:9606")
    print("   Strategy 3: gene:NAME AND organism_id:9606 AND reviewed:true")
    print("   Strategy 4: gene:NAME AND organism_id:9606")
    
    print("\n📈 BENEFITS OF ROBUST SEARCH:")
    print("   ✅ Higher success rates through fallback strategies")
    print("   ✅ Prioritizes reviewed (Swiss-Prot) entries")
    print("   ✅ Ensures human proteins (organism_id:9606)")
    print("   ✅ Handles gene name variations and synonyms")
    print("   ✅ Graceful degradation when exact matches fail")
    print("   ✅ Configurable for different use cases")
    print("   ✅ Tracks genes with multiple results for manual review")
    print("   ✅ Returns only one result per gene (selected automatically)")
    print("   ✅ Provides detailed information about selection process")


def main():
    """Run the complete demonstration"""
    print("Gene to Protein Workflow Demonstration")
    print("=" * 60)
    print("This demo shows how to use the new hierarchical structure")
    print("to process TSV files with gene names and convert them to")
    print("protein data in multiple formats with robust search strategies.\n")
    
    try:
        # Run the demonstrations
        results = demonstrate_simple_workflow()
        robust_results = demonstrate_robust_workflow()
        gene_data, output_files = demonstrate_step_by_step()
        robust_gene_data, robust_output_files = demonstrate_step_by_step_robust()
        batch_results = demonstrate_batch_processing()
        robust_batch_results = demonstrate_batch_processing_robust()
        
        # Show output file contents
        show_output_file_contents()
        
        # Compare approaches
        compare_with_old_approach()
        compare_search_strategies()
        
        print("\n" + "=" * 60)
        print("🎉 Demonstration completed successfully!")
        print("The new robust hierarchical structure makes complex bioinformatics")
        print("workflows much more manageable and maintainable.")
        print("Key improvements:")
        print("  • Configurable search criteria for different organisms")
        print("  • Fallback strategies for better success rates")
        print("  • Prioritization of reviewed protein entries")
        print("  • Enhanced error handling and logging")
        print("  • Automatic selection of single result per gene")
        print("  • Tracking of genes with multiple results for manual review")
        print("  • Detailed reporting of selection process")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        print("Make sure the TSV file exists and is accessible.")


if __name__ == "__main__":
    main() 