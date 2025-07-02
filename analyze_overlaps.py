#!/usr/bin/env python3
"""
Analyze Overlapping Entities from Top Hits Analysis
==================================================

This script analyzes the specific overlapping entities from the top hits analysis
and provides detailed information about which proteins overlap between datasets.
"""

import pandas as pd
from pathlib import Path

def load_target_names(file_path):
    """Load target names from a text file."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

def analyze_overlaps():
    """Analyze overlapping entities between datasets."""
    
    # Load target names from each dataset
    af3_targets = set(load_target_names('my_results/AF3_target_names.txt'))
    afp_targets = set(load_target_names('my_results/AFP_target_names.txt'))
    afp_jack_targets = set(load_target_names('my_results/AFP_Jack_target_names.txt'))
    
    print("=== OVERLAP ANALYSIS ===")
    print()
    
    # AF3 vs AFP overlap
    af3_afp_overlap = af3_targets.intersection(afp_targets)
    print(f"AF3 vs AFP Overlap ({len(af3_afp_overlap)} proteins):")
    if af3_afp_overlap:
        for protein in sorted(af3_afp_overlap):
            print(f"  - {protein}")
    else:
        print("  No overlap found")
    print()
    
    # AF3 vs AFP_Jack overlap
    af3_afp_jack_overlap = af3_targets.intersection(afp_jack_targets)
    print(f"AF3 vs AFP_Jack Overlap ({len(af3_afp_jack_overlap)} proteins):")
    if af3_afp_jack_overlap:
        for protein in sorted(af3_afp_jack_overlap):
            print(f"  - {protein}")
    else:
        print("  No overlap found")
    print()
    
    # AFP vs AFP_Jack overlap
    afp_afp_jack_overlap = afp_targets.intersection(afp_jack_targets)
    print(f"AFP vs AFP_Jack Overlap ({len(afp_afp_jack_overlap)} proteins):")
    if afp_afp_jack_overlap:
        for protein in sorted(afp_afp_jack_overlap):
            print(f"  - {protein}")
    else:
        print("  No overlap found")
    print()
    
    # Three-way overlap
    three_way_overlap = af3_targets.intersection(afp_targets).intersection(afp_jack_targets)
    print(f"Three-way Overlap (AF3 ∩ AFP ∩ AFP_Jack) ({len(three_way_overlap)} proteins):")
    if three_way_overlap:
        for protein in sorted(three_way_overlap):
            print(f"  - {protein}")
    else:
        print("  No three-way overlap found")
    print()
    
    # Unique to each dataset
    print("=== UNIQUE PROTEINS ===")
    print()
    
    only_af3 = af3_targets - afp_targets - afp_jack_targets
    print(f"Only in AF3 ({len(only_af3)} proteins):")
    for protein in sorted(only_af3):
        print(f"  - {protein}")
    print()
    
    only_afp = afp_targets - af3_targets - afp_jack_targets
    print(f"Only in AFP ({len(only_afp)} proteins):")
    for protein in sorted(only_afp):
        print(f"  - {protein}")
    print()
    
    only_afp_jack = afp_jack_targets - af3_targets - afp_targets
    print(f"Only in AFP_Jack ({len(only_afp_jack)} proteins):")
    for protein in sorted(only_afp_jack):
        print(f"  - {protein}")
    print()
    
    # Summary statistics
    print("=== SUMMARY STATISTICS ===")
    print(f"Total unique proteins across all datasets: {len(af3_targets.union(afp_targets).union(afp_jack_targets))}")
    print(f"AF3 total: {len(af3_targets)}")
    print(f"AFP total: {len(afp_targets)}")
    print(f"AFP_Jack total: {len(afp_jack_targets)}")
    print()
    print(f"AF3 ∩ AFP: {len(af3_afp_overlap)}")
    print(f"AF3 ∩ AFP_Jack: {len(af3_afp_jack_overlap)}")
    print(f"AFP ∩ AFP_Jack: {len(afp_afp_jack_overlap)}")
    print(f"AF3 ∩ AFP ∩ AFP_Jack: {len(three_way_overlap)}")

def analyze_merged_data():
    """Analyze the merged dataset to get more detailed overlap information."""
    
    print("\n=== MERGED DATASET ANALYSIS ===")
    
    # Load merged dataset
    merged_df = pd.read_csv('my_results/merged_datasets.csv')
    
    # Identify which datasets each protein appears in
    overlap_info = []
    
    for _, row in merged_df.iterrows():
        protein = row['target_protein']
        
        # Check which datasets have data for this protein
        has_af3 = pd.notna(row['iptm'])  # AF3 data present
        has_afp = pd.notna(row['AFP_iptm'])  # AFP data present
        has_afp_jack = pd.notna(row['AFP_Jack_iptm'])  # AFP_Jack data present
        
        datasets = []
        if has_af3:
            datasets.append('AF3')
        if has_afp:
            datasets.append('AFP')
        if has_afp_jack:
            datasets.append('AFP_Jack')
        
        overlap_info.append({
            'protein': protein,
            'datasets': datasets,
            'num_datasets': len(datasets)
        })
    
    # Convert to DataFrame for easier analysis
    overlap_df = pd.DataFrame(overlap_info)
    
    # Show proteins that appear in multiple datasets
    multi_dataset = overlap_df[overlap_df['num_datasets'] > 1]
    
    print(f"\nProteins appearing in multiple datasets ({len(multi_dataset)} total):")
    for _, row in multi_dataset.iterrows():
        print(f"  {row['protein']}: {', '.join(row['datasets'])}")
    
    # Show proteins that appear in all three datasets
    all_three = overlap_df[overlap_df['num_datasets'] == 3]
    print(f"\nProteins appearing in all three datasets ({len(all_three)} total):")
    for _, row in all_three.iterrows():
        print(f"  {row['protein']}")
    
    # Show proteins that appear in exactly two datasets
    exactly_two = overlap_df[overlap_df['num_datasets'] == 2]
    print(f"\nProteins appearing in exactly two datasets ({len(exactly_two)} total):")
    for _, row in exactly_two.iterrows():
        print(f"  {row['protein']}: {', '.join(row['datasets'])}")

if __name__ == "__main__":
    analyze_overlaps()
    analyze_merged_data() 