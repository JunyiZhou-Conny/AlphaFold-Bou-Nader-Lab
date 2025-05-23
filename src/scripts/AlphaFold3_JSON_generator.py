import json
import sys
from Bio import SeqIO

def generate_json_from_fasta(fasta_file, start_index, end_index):
    # Read sequences from the FASTA file
    sequences = list(SeqIO.parse(fasta_file, "fasta"))
    
    # Ensure indices are within bounds
    if start_index < 0 or end_index >= len(sequences):
        print("Error: Start or end index is out of bounds.")
        sys.exit(1)
    
    # Prepare the JSON structure
    json_data = []
    # Fix the first protein sequence (Q04740)
    fixed_seq_record = sequences[0]
    
    # Iterate over the specified range for the second protein
    for i in range(start_index, end_index + 1):
        pair_record = sequences[i]
        
        # Create a job entry for each pair, including the index in the name
        job_entry = {
            "name": f"Test Fold Job {i}: {fixed_seq_record.id}-{pair_record.id}",
            "modelSeeds": [],
            "sequences": [
                {
                    "proteinChain": {
                        "sequence": str(fixed_seq_record.seq),
                        "count": 1,
                        "useStructureTemplate": False
                    }
                },
                {
                    "proteinChain": {
                        "sequence": str(pair_record.seq),
                        "count": 1,
                        "useStructureTemplate": False
                    }
                }
            ],
            "dialect": "alphafoldserver",
            "version": 1
        }
        json_data.append(job_entry)
    
    # Generate the output file name based on indices
    output_json = f"output_{start_index}_{end_index}.json"
    
    # Write the JSON data to a file
    with open(output_json, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python AlphaFold3_JSON_generator.py <input_fasta> <start_index> <end_index>")
        sys.exit(1)
    
    input_fasta = sys.argv[1]
    start_index = int(sys.argv[2])
    end_index = int(sys.argv[3])
    
    generate_json_from_fasta(input_fasta, start_index, end_index)
