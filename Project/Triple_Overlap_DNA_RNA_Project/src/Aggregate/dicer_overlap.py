import pandas as pd
from Bio import SeqIO

def read_and_combine_csv_files():
    """
    Read and combine the three CSV files into a master file, using only protein names
    """
    # Read the three CSV files
    paper1_df = pd.read_csv("/Users/conny/Desktop/AlphaFold/Summer Project/src/Aggregate/paper1_fasta_results.csv")
    paper2_df = pd.read_csv("/Users/conny/Desktop/AlphaFold/Summer Project/src/Aggregate/paper2_fasta_results.csv")
    paper3_df = pd.read_csv("/Users/conny/Desktop/AlphaFold/Summer Project/src/Aggregate/paper3_gene_results_finalfinal.csv")
    
    # Select only relevant columns and rename for consistency
    paper1_df = paper1_df[['gene', 'accession', 'protein_name']]
    paper2_df = paper2_df[['gene', 'accession', 'protein_name']]
    paper3_df = paper3_df[['gene', 'accession', 'protein_name']]
    
    # Add source column to each dataframe
    paper1_df['source'] = 'paper1'
    paper2_df['source'] = 'paper2'
    paper3_df['source'] = 'paper3'
    
    # Combine all dataframes
    master_df = pd.concat([paper1_df, paper2_df, paper3_df], ignore_index=True)
    
    # Remove duplicates based on gene name
    master_df = master_df.drop_duplicates(subset=['gene'])
    
    # Save master file
    master_df.to_csv("master_proteins.csv", index=False)
    print(f"Created master file with {len(master_df)} unique genes")
    
    return master_df

def compare_with_dicer(master_df):
    """
    Compare master file with dicer candidates
    """
    # Read Dicer candidate genes
    dicer_df = pd.read_csv("/Users/conny/Desktop/AlphaFold/Summer Project/result/Dicer_candidates.tsv", sep="\t")
    dicer_genes = set(dicer_df["GENE"].dropna().str.upper())
    
    # Get genes from master file
    master_genes = set(master_df['gene'].dropna().str.upper())
    
    # Find overlaps and differences
    overlap = dicer_genes & master_genes
    only_in_dicer = dicer_genes - master_genes
    only_in_master = master_genes - dicer_genes
    
    # Create detailed overlap dataframe
    overlap_df = master_df[master_df['gene'].str.upper().isin(overlap)].copy()
    overlap_df['in_dicer'] = True
    
    # Save detailed results
    overlap_df.to_csv("dicer_master_overlap_detailed.csv", index=False)
    
    # Save summary results
    pd.DataFrame({"overlap": sorted(overlap)}).to_csv("dicer_master_overlap.csv", index=False)
    pd.DataFrame({"only_in_dicer": sorted(only_in_dicer)}).to_csv("dicer_only.csv", index=False)
    pd.DataFrame({"only_in_master": sorted(only_in_master)}).to_csv("master_only.csv", index=False)
    
    # Print summary
    print("\nComparison Results:")
    print(f"Number of Dicer candidates: {len(dicer_genes)}")
    print(f"Number of master proteins: {len(master_genes)}")
    print(f"Number of overlaps: {len(overlap)}")
    print(f"Number only in Dicer: {len(only_in_dicer)}")
    print(f"Number only in master: {len(only_in_master)}")
    
    print("\nResults saved:")
    print("- master_proteins.csv: Combined data from all three papers (gene, accession, protein_name)")
    print("- dicer_master_overlap_detailed.csv: Detailed information for overlapping genes")
    print("- dicer_master_overlap.csv: List of overlapping gene names")
    print("- dicer_only.csv: Genes only in Dicer file")
    print("- master_only.csv: Genes only in master file")

def main():
    # Create master file
    master_df = read_and_combine_csv_files()
    
    # Compare with dicer file
    compare_with_dicer(master_df)

if __name__ == "__main__":
    main()