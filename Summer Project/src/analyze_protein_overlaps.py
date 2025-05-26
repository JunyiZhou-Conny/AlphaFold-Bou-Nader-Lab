import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from Bio import SeqIO
from collections import defaultdict
import os

def read_fasta_proteins(fasta_file):
    """Read protein IDs from a FASTA file"""
    protein_ids = set()
    try:
        with open(fasta_file, 'r') as handle:
            for record in SeqIO.parse(handle, "fasta"):
                protein_ids.add(record.id)
    except FileNotFoundError:
        print(f"Warning: File {fasta_file} not found")
    return protein_ids

def merge_fasta_files(fasta_files, output_file="master_proteins.fasta"):
    """Merge multiple FASTA files into one master file"""
    all_records = []
    for fasta_file in fasta_files:
        try:
            with open(fasta_file, 'r') as handle:
                records = list(SeqIO.parse(handle, "fasta"))
                all_records.extend(records)
        except FileNotFoundError:
            print(f"Warning: File {fasta_file} not found")
    
    # Write all records to master file
    with open(output_file, 'w') as output_handle:
        SeqIO.write(all_records, output_handle, "fasta")
    
    print(f"Created master FASTA file: {output_file}")
    return len(all_records)

def analyze_overlaps(protein_sets, labels):
    """Analyze overlaps between protein sets and create visualizations"""
    # Create Venn diagram
    plt.figure(figsize=(10, 8))
    venn3(protein_sets, labels)
    plt.title("Protein Overlap Between Datasets")
    plt.savefig("protein_overlaps_venn.png")
    plt.close()

    # Calculate overlaps
    overlaps = {
        f"{labels[0]} only": len(protein_sets[0] - protein_sets[1] - protein_sets[2]),
        f"{labels[1]} only": len(protein_sets[1] - protein_sets[0] - protein_sets[2]),
        f"{labels[2]} only": len(protein_sets[2] - protein_sets[0] - protein_sets[1]),
        f"{labels[0]} and {labels[1]} only": len(protein_sets[0] & protein_sets[1] - protein_sets[2]),
        f"{labels[0]} and {labels[2]} only": len(protein_sets[0] & protein_sets[2] - protein_sets[1]),
        f"{labels[1]} and {labels[2]} only": len(protein_sets[1] & protein_sets[2] - protein_sets[0]),
        "All three": len(protein_sets[0] & protein_sets[1] & protein_sets[2])
    }

    # Save detailed overlap information
    with open("protein_overlaps.txt", "w") as f:
        f.write("Protein Overlap Analysis\n")
        f.write("======================\n\n")
        
        # Write summary statistics
        for label, count in overlaps.items():
            f.write(f"{label}: {count} proteins\n")
        
        f.write("\nDetailed Overlap Information\n")
        f.write("==========================\n\n")
        
        # Write detailed overlap information
        f.write(f"Proteins in all three datasets:\n")
        for protein in sorted(protein_sets[0] & protein_sets[1] & protein_sets[2]):
            f.write(f"{protein}\n")
        
        f.write(f"\nProteins in {labels[0]} and {labels[1]} only:\n")
        for protein in sorted(protein_sets[0] & protein_sets[1] - protein_sets[2]):
            f.write(f"{protein}\n")
        
        f.write(f"\nProteins in {labels[0]} and {labels[2]} only:\n")
        for protein in sorted(protein_sets[0] & protein_sets[2] - protein_sets[1]):
            f.write(f"{protein}\n")
        
        f.write(f"\nProteins in {labels[1]} and {labels[2]} only:\n")
        for protein in sorted(protein_sets[1] & protein_sets[2] - protein_sets[0]):
            f.write(f"{protein}\n")

def main():
    # Define input files with correct paths
    fasta_files = [
        "src/notebooks/p1_protein_sequences.fasta",
        "src/notebooks/p2_protein_sequences.fasta",
        "src/notebooks/p3_protein_sequences.fasta"
    ]
    
    labels = ["Paper 1", "Paper 2", "Paper 3"]
    
    # Read protein IDs from each file
    protein_sets = [read_fasta_proteins(f) for f in fasta_files]
    
    # Print number of proteins in each set
    for label, protein_set in zip(labels, protein_sets):
        print(f"Number of proteins in {label}: {len(protein_set)}")
    
    # Merge FASTA files
    total_proteins = merge_fasta_files(fasta_files)
    print(f"Total unique proteins across all files: {total_proteins}")
    
    # Analyze overlaps
    analyze_overlaps(protein_sets, labels)
    print("\nAnalysis complete! Check the following files:")
    print("- protein_overlaps_venn.png (Venn diagram visualization)")
    print("- protein_overlaps.txt (Detailed overlap information)")
    print("- master_proteins.fasta (Merged FASTA file)")

if __name__ == "__main__":
    main() 