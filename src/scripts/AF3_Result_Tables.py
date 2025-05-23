import os
import json
import csv
import re
from pathlib import Path
from collections import defaultdict

class AF3ResultProcessor:
    def __init__(self, base_dir, output_csv="af3_summary_metrics.csv"):
        self.base_dir = Path(base_dir)
        self.output_csv = output_csv
        self.data_rows = []
        self.missing_jobs = defaultdict(list)
        self.total_jobs = 0
        
        # Headers for the CSV file
        self.csv_headers = [
            "fold_group", "job_number", "target_protein",
            "iptm", "ptm", "ranking_score", "fraction_disordered", 
            "has_clash", "num_recycles",
            "chain_iptm_0", "chain_iptm_1",
            "chain_ptm_0", "chain_ptm_1",
            "chain_pair_iptm_00", "chain_pair_iptm_01", 
            "chain_pair_iptm_10", "chain_pair_iptm_11",
            "chain_pair_pae_min_00", "chain_pair_pae_min_01", 
            "chain_pair_pae_min_10", "chain_pair_pae_min_11"
        ]

    def process_summary_file(self, summary_file, fold_group, job_number, target_protein):
        try:
            with open(summary_file, 'r') as f:
                content = json.load(f)

            row = [
                fold_group,
                job_number,
                target_protein,
                content.get("iptm", ""),
                content.get("ptm", ""),
                content.get("ranking_score", ""),
                content.get("fraction_disordered", ""),
                content.get("has_clash", ""),
                content.get("num_recycles", "")
            ]

            # Flatten chain_iptm and chain_ptm
            row += content.get("chain_iptm", ["", ""])
            row += content.get("chain_ptm", ["", ""])

            # Flatten 2x2 matrices
            for matrix_key in ["chain_pair_iptm", "chain_pair_pae_min"]:
                matrix = content.get(matrix_key, [[None]*2]*2)
                row += [matrix[i][j] if matrix and len(matrix) > i and len(matrix[i]) > j else ""
                        for i in range(2) for j in range(2)]

            self.data_rows.append(row)
            return True

        except Exception as e:
            print(f"Error processing {summary_file}: {e}")
            return False

    def process_results(self):
        # Process each fold directory
        fold_dirs = sorted([d for d in self.base_dir.iterdir() if d.is_dir() and d.name.startswith("folds_")])
        
        for fold_dir in fold_dirs:
            # Extract start and end indices from folder name
            match = re.match(r"folds_(\d+)_(\d+)", fold_dir.name)
            if not match:
                continue
                
            start_idx, end_idx = map(int, match.groups())
            expected_jobs = set(range(start_idx, end_idx + 1))
            found_jobs = set()
            
            print(f"Processing {fold_dir.name}...")
            
            # Process each job directory
            for job_dir in fold_dir.iterdir():
                if not job_dir.is_dir():
                    continue
                    
                # Look for summary confidence files
                summary_files = list(job_dir.glob("*_summary_confidences_0.json"))
                if not summary_files:
                    continue
                    
                for summary_file in summary_files:
                    # Extract job number and target protein from filename
                    match = re.match(r"fold_test_fold_job_(\d+)_q[\d\w]+_([a-zA-Z][\d\w]+)_summary_confidences_0\.json", 
                                   summary_file.name)
                    if not match:
                        continue
                        
                    job_number = int(match.group(1))
                    target_protein = match.group(2)
                    found_jobs.add(job_number)
                    
                    self.process_summary_file(summary_file, fold_dir.name, job_number, target_protein)
            
            # Track missing jobs for this fold group
            missing = expected_jobs - found_jobs
            if missing:
                self.missing_jobs[fold_dir.name] = sorted(missing)
            
            self.total_jobs += len(expected_jobs)

    def save_results(self):
        # Sort data rows by job number
        self.data_rows.sort(key=lambda x: int(x[1]))
        
        # Write main results
        with open(self.output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.csv_headers)
            writer.writerows(self.data_rows)
            
        print(f"✅ Saved {len(self.data_rows)} entries to {self.output_csv}")
        
        # Write missing jobs report
        missing_report = "missing_jobs_report.txt"
        with open(missing_report, 'w') as f:
            f.write(f"Summary of Missing Jobs\n{'='*20}\n\n")
            f.write(f"Total expected jobs: {self.total_jobs}\n")
            f.write(f"Total processed jobs: {len(self.data_rows)}\n")
            f.write(f"Total missing jobs: {self.total_jobs - len(self.data_rows)}\n\n")
            
            if self.missing_jobs:
                f.write("Missing jobs by fold group:\n\n")
                for fold_group, jobs in sorted(self.missing_jobs.items()):
                    f.write(f"{fold_group}: {len(jobs)} missing\n")
                    f.write(f"Missing job numbers: {', '.join(map(str, jobs))}\n\n")
            else:
                f.write("No missing jobs found!\n")
                
        print(f"✅ Saved missing jobs report to {missing_report}")

def main():
    base_dir = "/Users/conny/Desktop/AlphaFoldResult/AF3"
    processor = AF3ResultProcessor(base_dir)
    processor.process_results()
    processor.save_results()

if __name__ == "__main__":
    main()
