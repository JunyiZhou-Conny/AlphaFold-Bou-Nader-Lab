import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from Bio import SeqIO
from collections import defaultdict
import os

def read_fasta_and_csv_proteins(fasta_file, csv_file):
    """Read protein IDs and descriptions from FASTA and CSV files"""
    protein_info = {}  # Dictionary to store accession -> description mapping
    protein_sequences = {}  # Dictionary to store accession -> sequence mapping
    protein_genes = {}  # Dictionary to store accession -> gene mapping
    
    # Read CSV file to get descriptions and gene information
    try:
        if "paper3" in csv_file:
            df = pd.read_csv(csv_file, encoding='latin1')
            for _, row in df.iterrows():
                protein_info[row['accession']] = row['protein_name']
                protein_genes[row['accession']] = row.get('gene', 'No gene information available')
        else:
            df = pd.read_csv(csv_file, encoding='latin1')
            for _, row in df.iterrows():
                protein_info[row['accession']] = row['description']
                protein_genes[row['accession']] = row.get('gene', 'No gene information available')
    except FileNotFoundError:
        print(f"Warning: CSV file {csv_file} not found")
    
    # Read FASTA file to get protein IDs and sequences
    protein_ids = set()
    try:
        with open(fasta_file, 'r') as handle:
            for record in SeqIO.parse(handle, "fasta"):
                protein_ids.add(record.id)
                protein_sequences[record.id] = str(record.seq)
    except FileNotFoundError:
        print(f"Warning: FASTA file {fasta_file} not found")
    
    return protein_ids, protein_info, protein_sequences, protein_genes

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

def create_overlap_excel(protein_sets, protein_info_dicts, protein_sequences_dicts, protein_genes_dicts, labels, output_file="protein_overlaps.xlsx"):
    """Create Excel file with multiple sheets for different protein overlaps"""
    with pd.ExcelWriter(output_file) as writer:
        # Sheet 1: All three papers overlap
        all_three = sorted(protein_sets[0] & protein_sets[1] & protein_sets[2])
        data_all_three = []
        for protein in all_three:
            data_all_three.append({
                'Protein Accession': protein,
                'Gene': protein_genes_dicts[0].get(protein, 'No gene information available'),
                'Paper 1 Description': protein_info_dicts[0].get(protein, 'No description available'),
                'Paper 2 Description': protein_info_dicts[1].get(protein, 'No description available'),
                'Paper 3 Description': protein_info_dicts[2].get(protein, 'No description available'),
                'Amino Acid Sequence': protein_sequences_dicts[0].get(protein, 'Sequence not available')
            })
        pd.DataFrame(data_all_three).to_excel(writer, sheet_name='All Three Papers', index=False)
        
        # Sheet 2: Paper 1 and 2 overlap
        p1_p2 = sorted(protein_sets[0] & protein_sets[1] - protein_sets[2])
        data_p1_p2 = []
        for protein in p1_p2:
            data_p1_p2.append({
                'Protein Accession': protein,
                'Gene': protein_genes_dicts[0].get(protein, 'No gene information available'),
                'Paper 1 Description': protein_info_dicts[0].get(protein, 'No description available'),
                'Paper 2 Description': protein_info_dicts[1].get(protein, 'No description available'),
                'Amino Acid Sequence': protein_sequences_dicts[0].get(protein, 'Sequence not available')
            })
        pd.DataFrame(data_p1_p2).to_excel(writer, sheet_name='Paper 1 and 2', index=False)
        
        # Sheet 3: Paper 1 and 3 overlap
        p1_p3 = sorted(protein_sets[0] & protein_sets[2] - protein_sets[1])
        data_p1_p3 = []
        for protein in p1_p3:
            data_p1_p3.append({
                'Protein Accession': protein,
                'Gene': protein_genes_dicts[0].get(protein, 'No gene information available'),
                'Paper 1 Description': protein_info_dicts[0].get(protein, 'No description available'),
                'Paper 3 Description': protein_info_dicts[2].get(protein, 'No description available'),
                'Amino Acid Sequence': protein_sequences_dicts[0].get(protein, 'Sequence not available')
            })
        pd.DataFrame(data_p1_p3).to_excel(writer, sheet_name='Paper 1 and 3', index=False)
        
        # Sheet 4: Paper 2 and 3 overlap
        p2_p3 = sorted(protein_sets[1] & protein_sets[2] - protein_sets[0])
        data_p2_p3 = []
        for protein in p2_p3:
            data_p2_p3.append({
                'Protein Accession': protein,
                'Gene': protein_genes_dicts[1].get(protein, 'No gene information available'),
                'Paper 2 Description': protein_info_dicts[1].get(protein, 'No description available'),
                'Paper 3 Description': protein_info_dicts[2].get(protein, 'No description available'),
                'Amino Acid Sequence': protein_sequences_dicts[1].get(protein, 'Sequence not available')
            })
        pd.DataFrame(data_p2_p3).to_excel(writer, sheet_name='Paper 2 and 3', index=False)

def analyze_overlaps(protein_sets, protein_info_dicts, protein_sequences_dicts, protein_genes_dicts, labels):
    """Analyze overlaps between protein sets and create visualizations with descriptions"""
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

    # Save detailed overlap information with descriptions
    with open("protein_overlaps.txt", "w") as f:
        f.write("Protein Overlap Analysis\n")
        f.write("======================\n\n")
        
        # Write summary statistics
        for label, count in overlaps.items():
            f.write(f"{label}: {count} proteins\n")
        
        f.write("\nDetailed Overlap Information\n")
        f.write("==========================\n\n")
        
        # Write detailed overlap information with descriptions
        f.write(f"Proteins in all three datasets:\n")
        for protein in sorted(protein_sets[0] & protein_sets[1] & protein_sets[2]):
            descriptions = []
            for info_dict in protein_info_dicts:
                desc = info_dict.get(protein, "No description available")
                descriptions.append(desc)
            f.write(f"{protein}\n")
            f.write(f"  Gene: {protein_genes_dicts[0].get(protein, 'No gene information available')}\n")
            f.write(f"  Paper 1: {descriptions[0]}\n")
            f.write(f"  Paper 2: {descriptions[1]}\n")
            f.write(f"  Paper 3: {descriptions[2]}\n\n")
        
        f.write(f"\nProteins in {labels[0]} and {labels[1]} only:\n")
        for protein in sorted(protein_sets[0] & protein_sets[1] - protein_sets[2]):
            f.write(f"{protein}\n")
            f.write(f"  Gene: {protein_genes_dicts[0].get(protein, 'No gene information available')}\n")
            f.write(f"  Paper 1: {protein_info_dicts[0].get(protein, 'No description available')}\n")
            f.write(f"  Paper 2: {protein_info_dicts[1].get(protein, 'No description available')}\n\n")
        
        f.write(f"\nProteins in {labels[0]} and {labels[2]} only:\n")
        for protein in sorted(protein_sets[0] & protein_sets[2] - protein_sets[1]):
            f.write(f"{protein}\n")
            f.write(f"  Gene: {protein_genes_dicts[0].get(protein, 'No gene information available')}\n")
            f.write(f"  Paper 1: {protein_info_dicts[0].get(protein, 'No description available')}\n")
            f.write(f"  Paper 3: {protein_info_dicts[2].get(protein, 'No description available')}\n\n")
        
        f.write(f"\nProteins in {labels[1]} and {labels[2]} only:\n")
        for protein in sorted(protein_sets[1] & protein_sets[2] - protein_sets[0]):
            f.write(f"{protein}\n")
            f.write(f"  Gene: {protein_genes_dicts[1].get(protein, 'No gene information available')}\n")
            f.write(f"  Paper 2: {protein_info_dicts[1].get(protein, 'No description available')}\n")
            f.write(f"  Paper 3: {protein_info_dicts[2].get(protein, 'No description available')}\n\n")
    
    # Create Excel file with multiple sheets
    create_overlap_excel(protein_sets, protein_info_dicts, protein_sequences_dicts, protein_genes_dicts, labels)

def main():
    # Define input files with correct paths
    fasta_files = [
        "/Users/conny/Desktop/AlphaFold/Summer Project/result/paper1_fasta_results.fasta",
        "/Users/conny/Desktop/AlphaFold/Summer Project/result/paper2_fasta_results.fasta",
        "/Users/conny/Desktop/AlphaFold/Summer Project/result/paper3_fasta_results.fasta"
    ]
    
    csv_files = [
        "/Users/conny/Desktop/AlphaFold/Summer Project/result/3 Paper Individual/paper1_fasta_results.csv",
        "/Users/conny/Desktop/AlphaFold/Summer Project/result/3 Paper Individual/paper2_fasta_results.csv",
        "/Users/conny/Desktop/AlphaFold/Summer Project/result/3 Paper Individual/paper3_fasta_results.csv"
    ]
    
    labels = ["Paper 1", "Paper 2", "Paper 3"]
    
    # Read protein IDs and descriptions from each file pair
    protein_sets = []
    protein_info_dicts = []
    protein_sequences_dicts = []
    protein_genes_dicts = []
    for fasta_file, csv_file in zip(fasta_files, csv_files):
        protein_ids, protein_info, protein_sequences, protein_genes = read_fasta_and_csv_proteins(fasta_file, csv_file)
        protein_sets.append(protein_ids)
        protein_info_dicts.append(protein_info)
        protein_sequences_dicts.append(protein_sequences)
        protein_genes_dicts.append(protein_genes)
    
    # Print number of proteins in each set
    for label, protein_set in zip(labels, protein_sets):
        print(f"Number of proteins in {label}: {len(protein_set)}")
    
    # Merge FASTA files
    total_proteins = merge_fasta_files(fasta_files)
    print(f"Total unique proteins across all files: {total_proteins}")
    
    # Analyze overlaps with descriptions
    analyze_overlaps(protein_sets, protein_info_dicts, protein_sequences_dicts, protein_genes_dicts, labels)
    print("\nAnalysis complete! Check the following files:")
    print("- protein_overlaps_venn.png (Venn diagram visualization)")
    print("- protein_overlaps.txt (Detailed overlap information with descriptions)")
    print("- protein_overlaps.xlsx (Excel file with multiple sheets for different overlaps)")
    print("- master_proteins.fasta (Merged FASTA file)")

if __name__ == "__main__":
    main()