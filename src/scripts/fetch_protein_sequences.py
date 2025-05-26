import requests
import sys
import json
import pandas as pd
from tqdm import tqdm
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random

def setup_session():
    """Configure and return a requests session with retry strategy"""
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def fetch_sequence(session, protein_id, max_retries=3, timeout=30):
    """
    Fetch sequence with retry logic and rate limiting
    """
    for attempt in range(max_retries):
        try:
            # Add random delay between requests (0.5 to 2 seconds)
            time.sleep(random.uniform(0.5, 2))
            
            url = f"https://rest.uniprot.org/uniprotkb/{protein_id}"
            response = session.get(
                url, 
                headers={"accept": "application/json"},
                params={"fields": ["sequence"]},
                timeout=timeout
            )
            
            if response.ok:
                data = response.json()
                sequence_info = data.get("sequence", {})
                return sequence_info.get("value", None)
            elif response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limit hit, waiting {retry_after} seconds...", file=sys.stderr)
                time.sleep(retry_after)
                continue
            else:
                print(f"Warning: Failed to fetch {protein_id} (Status code: {response.status_code})", file=sys.stderr)
                return None
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Timeout for {protein_id}, retrying in {wait_time:.2f} seconds...", file=sys.stderr)
                time.sleep(wait_time)
                continue
            else:
                print(f"Warning: Timeout after {max_retries} attempts for {protein_id}", file=sys.stderr)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Warning: Request failed for {protein_id}: {str(e)}", file=sys.stderr)
            return None
    
    return None

def process_protein_ids(protein_ids, output_file="protein_sequences.fasta", failed_queries_file="failed_queries.csv"):
    """
    Process a list of protein IDs and save sequences to FASTA file
    """
    session = setup_session()
    results = {}
    failed_queries = []

    # Wrap tqdm around the outer loop
    for entry in tqdm(protein_ids, desc="Fetching sequences"):
        protein_ids_split = entry.split(";")
        for protein_id in protein_ids_split:
            protein_id = protein_id.strip()
            if protein_id and protein_id not in results:
                sequence = fetch_sequence(session, protein_id)
                if sequence:
                    results[protein_id] = sequence
                else:
                    results[protein_id] = "Sequence Not Found"
                    failed_queries.append(protein_id)

    # Save successful sequences
    with open(output_file, "w") as file:
        for protein_id, sequence in results.items():
            file.write(f">{protein_id}\n{sequence}\n")

    # Save failed queries to CSV
    if failed_queries:
        pd.DataFrame({"protein_id": failed_queries}).to_csv(failed_queries_file, index=False)
        print(f"\nFailed queries saved to {failed_queries_file}")

    print(f"Protein sequences saved to {output_file}")
    print(f"Successfully retrieved: {len(results) - len(failed_queries)} sequences")
    print(f"Failed to retrieve: {len(failed_queries)} sequences")

if __name__ == "__main__":
    # Example usage
    import pandas as pd
    
    # Read your Excel file
    df = pd.read_excel('/Users/conny/Desktop/AlphaFold/Paper 3 data.xlsx', header=2)
    protein_ids = df['Protein IDs'].dropna().unique()
    
    # Process the protein IDs
    process_protein_ids(
        protein_ids,
        output_file="p3_protein_sequences.fasta",
        failed_queries_file="failed_queries.csv"
    ) 