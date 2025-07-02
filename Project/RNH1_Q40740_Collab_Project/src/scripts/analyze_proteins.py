import pandas as pd
import sys
import requests
from tqdm import tqdm

def analyze_gene_data(file_path):
    """
    Analyze gene data from an Excel file, focusing on gene names and descriptions.
    Maintains all entries, replaces missing descriptions with "Missing", and performs UniProt queries.
    
    Args:
        file_path (str): Path to the Excel file containing gene data
    """
    try:
        # Read the Excel file
        print(f"\nReading file: {file_path}")
        df = pd.read_excel(file_path, header=1)
        
        # Replace missing descriptions with "Missing"
        df['Description'] = df['Description'].fillna("Missing")
        
        # Basic information
        print("\n=== Basic Information ===")
        print(f"Total genes: {len(df)}")
        print(f"Columns: {', '.join(df.columns)}")
        
        # Create gene-description pairs
        gene_desc_pairs = list(zip(df['Protein'], df['Description']))
        print(f"\nTotal gene-description pairs: {len(gene_desc_pairs)}")
        
        # Check for missing values
        print("\n=== Missing Value Analysis ===")
        missing_protein = df['Protein'].isna().sum()
        missing_desc = (df['Description'] == "Missing").sum()
        print(f"Missing gene names: {missing_protein}")
        print(f"Missing descriptions (replaced with 'Missing'): {missing_desc}")
        
        if missing_desc > 0:
            print("\nGenes with missing descriptions:")
            missing_desc_df = df[df['Description'] == "Missing"]
            print(missing_desc_df[['Protein', 'Description']].to_string())
        
        # Check for duplicates
        print("\n=== Duplicate Analysis ===")
        duplicates = df[df['Protein'].duplicated(keep=False)]
        if len(duplicates) > 0:
            print(f"Found {len(duplicates)} duplicate genes:")
            print(duplicates.sort_values('Protein')[['Protein', 'Description']].to_string())
        else:
            print("No duplicate genes found.")
        
        # Save the complete gene list
        print("\n=== Saving Results ===")
        # Save all genes to a CSV file
        df.to_csv('complete_gene_list.csv', index=False)
        print("Saved complete gene list to 'complete_gene_list.csv'")
        
        # Perform UniProt queries
        print("\n=== Performing UniProt Queries ===")
        organism = "9606"  # Human
        results = []
        failed = []
        
        for gene, description in tqdm(gene_desc_pairs, desc="Querying UniProt"):
            # Modified query to only use gene name and organism
            query = f'gene_exact:{gene} AND organism_id:{organism}'
            url = "https://rest.uniprot.org/uniprotkb/search"
            params = {
                "query": query,
                "fields": "accession,gene_names,protein_name,organism_name,reviewed",
                "format": "json",
                "size": 500
            }
            try:
                res = requests.get(url, params=params, timeout=30)
                data = res.json()
                results_list = data.get("results", [])
                
                if not results_list:
                    failed.append({
                        "gene": gene,
                        "description": description
                    })
                
                # Add all results
                for result in results_list:
                    results.append({
                        "gene": gene,
                        "description": description,
                        "accession": result.get("primaryAccession"),
                        "reviewed": result.get("reviewed", False)
                    })
                    
            except Exception as e:
                failed.append({
                    "gene": gene,
                    "description": description,
                    "error": str(e)
                })
                print(f"Error for {gene}: {e}")
        
        # Save results
        results_df = pd.DataFrame(results)
        results_df.to_csv("uniprot_results.csv", index=False)
        print("\nSaved UniProt results to uniprot_results.csv")
        
        # Save failed queries
        if failed:
            failed_df = pd.DataFrame(failed)
            failed_df.to_csv("failed_queries.csv", index=False)
            print(f"\nFailed queries ({len(failed)}):")
            for item in failed:
                print(f"{item['gene']}: {item['description']}")
            print("\nSaved failed queries to failed_queries.csv")
        
        # Summary statistics
        print("\n=== Summary Statistics ===")
        print(f"Total genes: {len(df)}")
        print(f"Genes with complete information: {len(df) - missing_desc}")
        print(f"Genes with missing descriptions: {missing_desc}")
        print(f"Duplicate genes: {len(duplicates)}")
        print(f"Successful UniProt queries: {len(results)}")
        print(f"Failed UniProt queries: {len(failed)}")
        
        # Print first few entries as example
        print("\n=== Sample Entries ===")
        print("First 5 gene-description pairs:")
        for i, (gene, desc) in enumerate(gene_desc_pairs[:5]):
            print(f"{i+1}. {gene}: {desc}")
        
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    file_path = '/Users/conny/Desktop/AlphaFold/Summer Project/data/Supplemental_Table_S1.xlsx'
    analyze_gene_data(file_path) 