import pandas as pd

def extract_overlapping_proteins():
    # Read the Excel file
    excel_path = "/Users/conny/Desktop/AlphaFold/Summer Project/src/26 Overlapped Analysis/protein_overlaps.xlsx"
    df = pd.read_excel(excel_path, sheet_name='All Three Papers')
    
    # Write overlapping proteins to FASTA file
    output_file = "overlapping_proteins.fasta"
    with open(output_file, 'w') as f:
        for _, row in df.iterrows():
            accession = row['Protein Accession']
            sequence = row['Amino Acid Sequence']
            f.write(f">{accession}\n")
            f.write(f"{sequence}\n")
    
    print(f"\nAnalysis complete!")
    print(f"Number of overlapping proteins: {len(df)}")
    print(f"\nOverlapping proteins have been written to: {output_file}")

if __name__ == "__main__":
    extract_overlapping_proteins() 