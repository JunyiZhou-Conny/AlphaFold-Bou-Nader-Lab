import json
from pathlib import Path

def combine_json_files(input_dir: str, output_file: str):
    """
    Combine multiple JSON files into a single file
    
    Args:
        input_dir (str): Directory containing the JSON files
        output_file (str): Path to the output combined JSON file
    """
    # List to store all jobs
    all_jobs = []
    
    # Read each JSON file
    input_path = Path(input_dir)
    for json_file in input_path.glob('*.json'):
        with open(json_file, 'r') as f:
            jobs = json.load(f)
            all_jobs.extend(jobs)
    
    # Write combined jobs to output file
    with open(output_file, 'w') as f:
        json.dump(all_jobs, f, indent=2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Combine multiple AlphaFold3 JSON files into one')
    parser.add_argument('input_dir', help='Directory containing the JSON files')
    parser.add_argument('output_file', help='Path to the output combined JSON file')
    
    args = parser.parse_args()
    combine_json_files(args.input_dir, args.output_file)