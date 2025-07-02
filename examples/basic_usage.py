#!/usr/bin/env python3
"""
Basic Usage Examples for AlphaFold Core

This script demonstrates how to use the new hierarchical structure
for common AlphaFold-related tasks.
"""

import sys
from pathlib import Path

# Add the alphafold_core package to the path
sys.path.append(str(Path(__file__).parent.parent))

from alphafold_core.data import ProteinSequenceFetcher, JSONProcessor, DataProcessor
from alphafold_core.analysis import OverlapAnalyzer
from alphafold_core.pipeline import QualityAssessmentPipeline
from alphafold_core.config import config
from alphafold_core.utils import load_dataframe


def example_1_fetch_protein_sequences():
    """Example 1: Fetch protein sequences from Excel file"""
    print("=== Example 1: Fetching Protein Sequences ===")
    
    fetcher = ProteinSequenceFetcher()
    
    # Fetch sequences from Excel file (similar to your existing fetch_protein_sequences.py)
    sequences = fetcher.fetch_from_excel(
        excel_file="Paper 3 data.xlsx",
        column_name="Protein IDs",
        header_row=2
    )
    
    print(f"Fetched {len(sequences)} protein sequences")
    print(f"Successful: {len([s for s in sequences.values() if s != 'Sequence Not Found'])}")
    print(f"Failed: {len([s for s in sequences.values() if s == 'Sequence Not Found'])}")


def example_2_process_alphafold_json():
    """Example 2: Process AlphaFold JSON files (similar to AF3_Result_Table.py)"""
    print("\n=== Example 2: Processing AlphaFold JSON Files ===")
    
    processor = JSONProcessor()
    
    # Process all JSON files in a directory
    metrics_df = processor.process_directory(
        root_dir="alphafold_output",
        pattern="*_summary_confidences_0.json"
    )
    
    # Save to CSV
    processor.save_to_csv(metrics_df, "summary_metrics.csv")
    
    print(f"Processed {len(metrics_df)} JSON files")
    print(f"Average iPTM: {metrics_df['iptm'].mean():.3f}")
    print(f"Average pTM: {metrics_df['ptm'].mean():.3f}")


def example_3_quality_assessment_pipeline():
    """Example 3: Complete quality assessment pipeline"""
    print("\n=== Example 3: Quality Assessment Pipeline ===")
    
    pipeline = QualityAssessmentPipeline()
    
    # Run complete quality assessment
    results = pipeline.run_quality_assessment(
        json_directory="alphafold_output",
        output_prefix="quality_assessment",
        iptm_threshold=0.6,
        ptm_threshold=0.5
    )
    
    print("Quality Assessment Results:")
    print(f"Total predictions: {results['quality_summary']['total_predictions']}")
    print(f"High quality predictions: {results['quality_summary']['high_quality_predictions']}")
    print(f"Quality rate: {results['quality_summary']['quality_rate']:.1f}%")


def example_4_overlap_analysis():
    """Example 4: Overlap analysis between datasets"""
    print("\n=== Example 4: Overlap Analysis ===")
    
    analyzer = OverlapAnalyzer()
    
    # Analyze overlaps between multiple files
    file_paths = {
        "paper1": "paper1_proteins.csv",
        "paper2": "paper2_proteins.csv", 
        "paper3": "paper3_proteins.csv"
    }
    
    id_columns = {
        "paper1": "protein_id",
        "paper2": "protein_id",
        "paper3": "protein_id"
    }
    
    overlap_df = analyzer.analyze_from_files(file_paths, id_columns)
    
    print("Overlap Analysis Results:")
    print(overlap_df[['dataset1', 'dataset2', 'jaccard_similarity', 'intersection_size']])


def example_5_data_processing():
    """Example 5: General data processing tasks"""
    print("\n=== Example 5: Data Processing ===")
    
    processor = DataProcessor()
    
    # Load and filter data
    df = load_dataframe("summary_metrics.csv")
    if df is not None:
        filtered_df = processor.filter_dataframe(
            df, 
            iptm_threshold=0.6,
            ptm_threshold=0.5
        )
        
        # Extract target names
        if 'target_protein' in filtered_df.columns:
            target_names = processor.extract_target_names(filtered_df)
            processor.save_target_names(target_names, "high_quality_targets")
            
            print(f"Extracted {len(target_names)} high-quality target names")


def example_6_combine_json_files():
    """Example 6: Combine multiple JSON files"""
    print("\n=== Example 6: Combining JSON Files ===")
    
    processor = DataProcessor()
    
    # Combine multiple JSON files into one
    success = processor.combine_json_files(
        input_dir="json_files",
        output_file="combined_data.json"
    )
    
    if success:
        print("Successfully combined JSON files")
    else:
        print("Failed to combine JSON files")


def main():
    """Run all examples"""
    print("AlphaFold Core - Basic Usage Examples")
    print("=" * 50)
    
    try:
        # Note: These examples assume you have the appropriate data files
        # You may need to adjust file paths or skip examples based on your data
        
        # example_1_fetch_protein_sequences()
        # example_2_process_alphafold_json()
        # example_3_quality_assessment_pipeline()
        # example_4_overlap_analysis()
        # example_5_data_processing()
        # example_6_combine_json_files()
        
        print("\nExamples completed! Check the output files for results.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have the required data files in the correct locations.")


if __name__ == "__main__":
    main() 