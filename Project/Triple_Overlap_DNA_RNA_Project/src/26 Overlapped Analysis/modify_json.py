import json
import os

def modify_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Modify the structure
    modified_data = {
        "name": data["name"],
        "modelSeeds": data["modelSeeds"],
        "sequences": [
            {
                "protein": {
                    "id": "P",
                    "sequence": data["sequences"][0]["protein"]["sequence"]
                }
            },
            {
                "dna": {
                    "id": "D",
                    "sequence": data["sequences"][1]["dna"]["sequence"]
                }
            },
            {
                "rna": {
                    "id": "R",
                    "sequence": data["sequences"][2]["rna"]["sequence"]
                }
            }
        ],
        "dialect": "alphafold3",
        "version": 1
    }
    
    # Write back to file
    with open(file_path, 'w') as f:
        json.dump(modified_data, f, indent=2)

# Directory containing JSON files
json_dir = "/Users/conny/Desktop/AlphaFold/local_json_files_no_msa"

# Process all JSON files in the directory
for filename in os.listdir(json_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(json_dir, filename)
        print(f"Processing {filename}...")
        modify_json_file(file_path)

print("All files have been modified successfully!") 