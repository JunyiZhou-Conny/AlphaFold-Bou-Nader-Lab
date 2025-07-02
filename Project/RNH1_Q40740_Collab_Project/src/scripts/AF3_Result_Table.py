import os
import json
import csv
import argparse
from pathlib import Path

# Define the metrics/fields to extract from each JSON file
CSV_HEADERS = [
    "job_name", "iptm", "ptm", "ranking_score", "fraction_disordered", "has_clash", "num_recycles",
    "chain_iptm_0", "chain_iptm_1",
    "chain_ptm_0", "chain_ptm_1",
    "chain_pair_iptm_00", "chain_pair_iptm_01", "chain_pair_iptm_10", "chain_pair_iptm_11",
    "chain_pair_pae_min_00", "chain_pair_pae_min_01", "chain_pair_pae_min_10", "chain_pair_pae_min_11"
]

def parse_job_name(json_path):
    # Extract job name from the filename, e.g., fold_rnah1_dss1_summary_confidences_0.json -> fold_rnah1_dss1
    job_name = Path(json_path).stem.replace('_summary_confidences_0', '')
    # Replace pipe character with dash for AlphaFold3 compatibility
    job_name = job_name.replace('|', '-')
    return job_name

def extract_metrics(json_file):
    try:
        with open(json_file, 'r') as f:
            content = json.load(f)
        row = {
            "job_name": parse_job_name(json_file),
            "iptm": content.get("iptm", ""),
            "ptm": content.get("ptm", ""),
            "ranking_score": content.get("ranking_score", ""),
            "fraction_disordered": content.get("fraction_disordered", ""),
            "has_clash": content.get("has_clash", ""),
            "num_recycles": content.get("num_recycles", "")
        }
        # Flatten chain_iptm and chain_ptm
        row["chain_iptm_0"], row["chain_iptm_1"] = (content.get("chain_iptm", ["", ""]) + ["", ""])[:2]
        row["chain_ptm_0"], row["chain_ptm_1"] = (content.get("chain_ptm", ["", ""]) + ["", ""])[:2]
        # Flatten 2x2 matrices
        for matrix_key, prefix in [("chain_pair_iptm", "chain_pair_iptm"), ("chain_pair_pae_min", "chain_pair_pae_min")]:
            matrix = content.get(matrix_key, [["", ""], ["", ""]])
            for i in range(2):
                for j in range(2):
                    row[f"{prefix}_{i}{j}"] = matrix[i][j] if matrix and len(matrix) > i and len(matrix[i]) > j else ""
        return row
    except Exception as e:
        print(f"Error processing {json_file}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Summarize *_summary_confidences_0.json files into a CSV table.")
    parser.add_argument('--root', type=str, required=True, help='Root directory to search recursively')
    parser.add_argument('--output', type=str, default='summary_metrics.csv', help='Output CSV file name')
    args = parser.parse_args()

    root = Path(args.root)
    all_jsons = list(root.rglob('*_summary_confidences_0.json'))
    print(f"Found {len(all_jsons)} summary_confidences_0.json files.")

    rows = []
    for json_file in all_jsons:
        metrics = extract_metrics(json_file)
        if metrics:
            rows.append(metrics)

    # Write to CSV
    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Saved {len(rows)} entries to {args.output}")

if __name__ == "__main__":
    main() 