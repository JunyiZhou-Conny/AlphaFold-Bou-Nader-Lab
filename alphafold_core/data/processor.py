"""
Data processing module for AlphaFold Core
Handles JSON processing, data manipulation, and transformation
"""

import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from collections import defaultdict
import logging

from ..config import config
from ..utils import (
    safe_json_load, safe_json_save, find_json_files, 
    parse_job_name, flatten_nested_dict, setup_logging,
    save_dataframe
)


class JSONProcessor:
    """Processes AlphaFold JSON files and extracts metrics"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.csv_headers = [
            "job_name", "iptm", "ptm", "ranking_score", "fraction_disordered", 
            "has_clash", "num_recycles",
            "chain_iptm_0", "chain_iptm_1",
            "chain_ptm_0", "chain_ptm_1",
            "chain_pair_iptm_00", "chain_pair_iptm_01", "chain_pair_iptm_10", "chain_pair_iptm_11",
            "chain_pair_pae_min_00", "chain_pair_pae_min_01", "chain_pair_pae_min_10", "chain_pair_pae_min_11"
        ]
        
        # AF3-specific headers
        self.af3_csv_headers = [
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
    
    def extract_metrics_from_file(self, json_file: Union[str, Path]) -> Optional[Dict]:
        """Extract metrics from a single JSON file"""
        try:
            content = safe_json_load(json_file)
            if not content:
                return None
            
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
            chain_iptm = content.get("chain_iptm", ["", ""])
            chain_ptm = content.get("chain_ptm", ["", ""])
            
            row["chain_iptm_0"], row["chain_iptm_1"] = (chain_iptm + ["", ""])[:2]
            row["chain_ptm_0"], row["chain_ptm_1"] = (chain_ptm + ["", ""])[:2]
            
            # Flatten 2x2 matrices
            for matrix_key, prefix in [("chain_pair_iptm", "chain_pair_iptm"), 
                                     ("chain_pair_pae_min", "chain_pair_pae_min")]:
                matrix = content.get(matrix_key, [["", ""], ["", ""]])
                for i in range(2):
                    for j in range(2):
                        row[f"{prefix}_{i}{j}"] = matrix[i][j] if matrix and len(matrix) > i and len(matrix[i]) > j else ""
            
            return row
        except Exception as e:
            self.logger.error(f"Error processing {json_file}: {e}")
            return None
    
    def process_directory(self, root_dir: Union[str, Path], 
                         pattern: str = "*_summary_confidences_0.json") -> pd.DataFrame:
        """Process all JSON files in a directory and return as DataFrame"""
        root_dir = Path(root_dir)
        json_files = find_json_files(root_dir, pattern)
        
        # Filter out macOS metadata files
        json_files = [f for f in json_files if not f.name.startswith("._")]
        
        self.logger.info(f"Found {len(json_files)} JSON files to process")
        
        rows = []
        for json_file in json_files:
            metrics = self.extract_metrics_from_file(json_file)
            if metrics:
                rows.append(metrics)
        
        df = pd.DataFrame(rows)
        self.logger.info(f"Successfully processed {len(rows)} files")
        return df
    
    def process_triple_overlap_json_files(self, root_dir: Union[str, Path]) -> pd.DataFrame:
        """Process triple_overlap JSON files with flexible naming patterns"""
        root_dir = Path(root_dir)
        
        # Look for various possible patterns
        patterns = [
            "*_summary_confidences.json",           # Your pattern
            "*_summary_confidences_0.json",         # Standard pattern
            "*summary_confidences*.json",           # Flexible pattern
            "*.json"                                # All JSON files
        ]
        
        json_files = []
        for pattern in patterns:
            files = list(root_dir.glob(pattern))
            if files:
                json_files = files
                self.logger.info(f"Found {len(files)} files with pattern: {pattern}")
                break
        
        if not json_files:
            self.logger.warning(f"No JSON files found in {root_dir}")
            return pd.DataFrame()
        
        rows = []
        for json_file in json_files:
            try:
                content = safe_json_load(json_file)
                if not content:
                    continue
                
                # Extract job name from filename
                job_name = self._extract_job_name_from_triple_overlap(json_file)
                
                row = {
                    "job_name": job_name,
                    "iptm": content.get("iptm", ""),
                    "ptm": content.get("ptm", ""),
                    "ranking_score": content.get("ranking_score", ""),
                    "fraction_disordered": content.get("fraction_disordered", ""),
                    "has_clash": content.get("has_clash", ""),
                    "num_recycles": content.get("num_recycles", "")
                }
                
                # Flatten chain_iptm and chain_ptm
                chain_iptm = content.get("chain_iptm", ["", ""])
                chain_ptm = content.get("chain_ptm", ["", ""])
                
                row["chain_iptm_0"], row["chain_iptm_1"] = (chain_iptm + ["", ""])[:2]
                row["chain_ptm_0"], row["chain_ptm_1"] = (chain_ptm + ["", ""])[:2]
                
                # Flatten 2x2 matrices
                for matrix_key, prefix in [("chain_pair_iptm", "chain_pair_iptm"), 
                                         ("chain_pair_pae_min", "chain_pair_pae_min")]:
                    matrix = content.get(matrix_key, [["", ""], ["", ""]])
                    for i in range(2):
                        for j in range(2):
                            row[f"{prefix}_{i}{j}"] = matrix[i][j] if matrix and len(matrix) > i and len(matrix[i]) > j else ""
                
                rows.append(row)
                
            except Exception as e:
                self.logger.error(f"Error processing {json_file}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        self.logger.info(f"Successfully processed {len(rows)} triple_overlap files")
        return df
    
    def _extract_job_name_from_triple_overlap(self, json_file: Path) -> str:
        """Extract job name from triple_overlap filename patterns"""
        filename = json_file.stem  # Remove .json extension
        
        # Pattern 1: triple_overlap_number_1_o00567-dna-rna_summary_confidences
        # Extract the protein ID (o00567)
        match = re.search(r'triple_overlap_number_\d+_([a-zA-Z0-9]+)-dna-rna', filename)
        if match:
            return match.group(1)
        
        # Pattern 2: Any protein ID pattern (e.g., p11387, q9bqg0)
        match = re.search(r'([a-zA-Z][0-9a-zA-Z]{5,6})', filename)
        if match:
            return match.group(1)
        
        # Pattern 3: Extract from standard patterns
        match = re.search(r'fold_.*?([a-zA-Z][0-9a-zA-Z]+)_summary_confidences', filename)
        if match:
            return match.group(1)
        
        # Fallback: use filename without extension
        return filename.replace('_summary_confidences', '').replace('triple_overlap_number_', '')
    
    def save_to_csv(self, df: pd.DataFrame, output_file: str = "summary_metrics.csv"):
        """Save processed data to CSV"""
        df.to_csv(output_file, index=False)
        self.logger.info(f"✅ Saved {len(df)} entries to {output_file}")
    
    # AF3-specific methods
    def process_af3_summary_file(self, summary_file: Union[str, Path], 
                                fold_group: str, job_number: int, 
                                target_protein: str) -> Optional[List]:
        """Process a single AF3 summary file with fold group information"""
        try:
            content = safe_json_load(summary_file)
            if not content:
                return None

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

            return row
        except Exception as e:
            self.logger.error(f"Error processing {summary_file}: {e}")
            return None
    
    def process_af3_results(self, base_dir: Union[str, Path], 
                          output_csv: str = "af3_summary_metrics.csv") -> Tuple[pd.DataFrame, Dict]:
        """Process AF3 results with fold group organization and missing job tracking"""
        base_dir = Path(base_dir)
        data_rows = []
        missing_jobs = defaultdict(list)
        total_jobs = 0
        
        # Process each fold directory
        fold_dirs = sorted([d for d in base_dir.iterdir() 
                           if d.is_dir() and d.name.startswith("folds_")])
        
        for fold_dir in fold_dirs:
            # Extract start and end indices from folder name
            match = re.match(r"folds_(\d+)_(\d+)", fold_dir.name)
            if not match:
                continue
                
            start_idx, end_idx = map(int, match.groups())
            expected_jobs = set(range(start_idx, end_idx + 1))
            found_jobs = set()
            
            self.logger.info(f"Processing {fold_dir.name}...")
            
            # Process each job directory
            for job_dir in fold_dir.iterdir():
                if not job_dir.is_dir():
                    continue
                    
                # Look for summary confidence files, but filter out macOS metadata files
                summary_files = [f for f in job_dir.glob("*_summary_confidences_0.json") 
                               if not f.name.startswith("._")]
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
                    
                    row = self.process_af3_summary_file(summary_file, fold_dir.name, 
                                                       job_number, target_protein)
                    if row:
                        data_rows.append(row)
            
            # Track missing jobs for this fold group
            missing = expected_jobs - found_jobs
            if missing:
                missing_jobs[fold_dir.name] = sorted(missing)
            
            total_jobs += len(expected_jobs)
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=self.af3_csv_headers)
        
        # Sort by job number
        df = df.sort_values('job_number')
        
        # Save results
        df.to_csv(output_csv, index=False)
        self.logger.info(f"✅ Saved {len(data_rows)} entries to {output_csv}")
        
        # Generate missing jobs report
        missing_report = self._generate_missing_jobs_report(missing_jobs, total_jobs, len(data_rows))
        
        return df, missing_report
    
    def _generate_missing_jobs_report(self, missing_jobs: Dict, 
                                    total_jobs: int, processed_jobs: int) -> Dict:
        """Generate missing jobs report"""
        report = {
            'total_expected_jobs': total_jobs,
            'total_processed_jobs': processed_jobs,
            'total_missing_jobs': total_jobs - processed_jobs,
            'missing_jobs_by_fold': dict(missing_jobs),
            'fold_groups_with_missing': list(missing_jobs.keys())
        }
        
        # Save report to file
        report_file = "missing_jobs_report.txt"
        with open(report_file, 'w') as f:
            f.write(f"Summary of Missing Jobs\n{'='*20}\n\n")
            f.write(f"Total expected jobs: {total_jobs}\n")
            f.write(f"Total processed jobs: {processed_jobs}\n")
            f.write(f"Total missing jobs: {total_jobs - processed_jobs}\n\n")
            
            if missing_jobs:
                f.write("Missing jobs by fold group:\n\n")
                for fold_group, jobs in sorted(missing_jobs.items()):
                    f.write(f"{fold_group}: {len(jobs)} missing\n")
                    f.write(f"Missing job numbers: {', '.join(map(str, jobs))}\n\n")
            else:
                f.write("No missing jobs found!\n")
        
        self.logger.info(f"✅ Saved missing jobs report to {report_file}")
        return report


class DataProcessor:
    """General data processing and manipulation utilities"""
    
    def __init__(self):
        self.logger = setup_logging()
    
    def combine_json_files(self, input_dir: Union[str, Path], 
                          output_file: Union[str, Path]) -> bool:
        """Combine multiple JSON files into a single file"""
        try:
            input_path = Path(input_dir)
            all_jobs = []
            
            for json_file in input_path.glob('*.json'):
                jobs = safe_json_load(json_file)
                if jobs:
                    all_jobs.extend(jobs)
            
            return safe_json_save(all_jobs, output_file)
        except Exception as e:
            self.logger.error(f"Error combining JSON files: {e}")
            return False
    
    def modify_json_structure(self, file_path: Union[str, Path]) -> bool:
        """Modify JSON structure for AlphaFold3 format"""
        try:
            data = safe_json_load(file_path)
            if not data:
                return False
            
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
            
            return safe_json_save(modified_data, file_path)
        except Exception as e:
            self.logger.error(f"Error modifying JSON structure: {e}")
            return False
    
    def filter_dataframe(self, df: pd.DataFrame, 
                        iptm_threshold: float = None,
                        ptm_threshold: float = None,
                        ranking_threshold: float = None) -> pd.DataFrame:
        """Filter dataframe based on quality thresholds"""
        filtered_df = df.copy()
        
        if iptm_threshold is not None:
            filtered_df = filtered_df[filtered_df['iptm'] >= iptm_threshold]
        
        if ptm_threshold is not None:
            filtered_df = filtered_df[filtered_df['ptm'] >= ptm_threshold]
        
        if ranking_threshold is not None:
            filtered_df = filtered_df[filtered_df['ranking_score'] >= ranking_threshold]
        
        self.logger.info(f"Filtered from {len(df)} to {len(filtered_df)} entries")
        return filtered_df
    
    def extract_target_names(self, df: pd.DataFrame, 
                           target_column: str = "target_protein",
                           capitalize: bool = True) -> List[str]:
        """Extract and optionally capitalize target names"""
        target_names = df[target_column].dropna().unique()
        
        if capitalize:
            target_names = [name.upper() for name in target_names]
        
        return target_names.tolist()
    
    def save_target_names(self, target_names: List[str], 
                         output_prefix: str = "target_names") -> Dict[str, str]:
        """Save target names to multiple formats"""
        output_files = {}
        
        # Save as text file
        txt_file = f"{output_prefix}.txt"
        with open(txt_file, 'w') as f:
            for name in target_names:
                f.write(f"{name}\n")
        output_files['txt'] = txt_file
        
        # Save as Excel
        xlsx_file = f"{output_prefix}.xlsx"
        target_df = pd.DataFrame({'Target_Names': target_names})
        target_df.to_excel(xlsx_file, index=False)
        output_files['xlsx'] = xlsx_file
        
        return output_files
    
    def split_protein_ids(self, protein_ids: List[str], 
                         separator: str = ";") -> List[str]:
        """Split protein IDs that may contain multiple IDs separated by semicolons"""
        split_ids = []
        for protein_id in protein_ids:
            if separator in protein_id:
                split_ids.extend([pid.strip() for pid in protein_id.split(separator)])
            else:
                split_ids.append(protein_id.strip())
        return split_ids
    
    def process_gene_to_protein_data(self, gene_protein_data: Dict[str, Dict], 
                                   output_prefix: str = "gene_protein_data") -> Dict[str, str]:
        """Process gene-to-protein data and save in multiple formats"""
        output_files = {}
        
        # Prepare data for different formats
        csv_data = []
        fasta_data = []
        json_data = []
        multiple_results_data = []  # Track genes with multiple results
        
        for gene_name, protein_info in gene_protein_data.items():
            if "error" in protein_info:
                # Gene not found
                csv_data.append({
                    "gene_name": gene_name,
                    "protein_accession": "Not Found",
                    "protein_name": "Not Found",
                    "sequence": "Not Found",
                    "organism": "Not Found",
                    "status": "Gene not found",
                    "multiple_results_found": False,
                    "total_results": 0,
                    "selected_result": "N/A"
                })
                continue
            
            # Check if multiple results were found
            multiple_results = protein_info.get("multiple_results_found", False)
            total_results = protein_info.get("total_results", 1)
            selected_result = protein_info.get("selected_result", "Single result")
            
            # If multiple results were found, add to tracking list
            if multiple_results:
                multiple_results_data.append({
                    "gene_name": gene_name,
                    "selected_accession": protein_info.get("accession", "Unknown"),
                    "selected_protein_name": protein_info.get("protein_name", "Unknown"),
                    "total_results": total_results,
                    "selected_result": selected_result,
                    "all_accessions": protein_info.get("all_accessions", []),
                    "all_protein_names": protein_info.get("all_protein_names", [])
                })
            
            # Successful protein info
            csv_data.append({
                "gene_name": gene_name,
                "protein_accession": protein_info.get("accession", "Unknown"),
                "protein_name": protein_info.get("protein_name", "Unknown"),
                "sequence": protein_info.get("sequence", "Unknown"),
                "organism": protein_info.get("organism", "Unknown"),
                "status": "Success",
                "multiple_results_found": multiple_results,
                "total_results": total_results,
                "selected_result": selected_result
            })
            
            # Add to FASTA data if sequence exists
            if protein_info.get("sequence") and protein_info["sequence"] != "Unknown":
                fasta_data.append({
                    "id": protein_info.get("accession", gene_name),
                    "description": f"{gene_name} | {protein_info.get('protein_name', 'Unknown')}",
                    "sequence": protein_info["sequence"]
                })
            
            # Add to JSON data for AlphaFold
            if protein_info.get("sequence") and protein_info["sequence"] != "Unknown":
                # Create job name and replace pipe with dash for AlphaFold3 compatibility
                job_name = f"Gene: {gene_name} | Protein: {protein_info.get('accession', gene_name)}"
                job_name = job_name.replace('|', '-')
                
                json_data.append({
                    "name": job_name,
                    "modelSeeds": [],
                    "sequences": [
                        {
                            "proteinChain": {
                                "sequence": protein_info["sequence"],
                                "count": 1,
                                "useStructureTemplate": False
                            }
                        }
                    ],
                    "dialect": "alphafoldserver",
                    "version": 1
                })
        
        # Save CSV
        csv_file = f"{output_prefix}.csv"
        csv_df = pd.DataFrame(csv_data)
        csv_df.to_csv(csv_file, index=False)
        output_files['csv'] = csv_file
        
        # Save FASTA
        if fasta_data:
            fasta_file = f"{output_prefix}.fasta"
            with open(fasta_file, 'w') as f:
                for entry in fasta_data:
                    f.write(f">{entry['id']} {entry['description']}\n")
                    f.write(f"{entry['sequence']}\n")
            output_files['fasta'] = fasta_file
        
        # Save JSON for AlphaFold
        if json_data:
            json_file = f"{output_prefix}_alphafold.json"
            safe_json_save(json_data, json_file)
            output_files['json'] = json_file
        
        # Save multiple results summary if any were found
        if multiple_results_data:
            multiple_results_file = f"{output_prefix}_multiple_results.csv"
            multiple_df = pd.DataFrame(multiple_results_data)
            multiple_df.to_csv(multiple_results_file, index=False)
            output_files['multiple_results'] = multiple_results_file
            
            # Also save as JSON for easier processing
            multiple_results_json = f"{output_prefix}_multiple_results.json"
            safe_json_save(multiple_results_data, multiple_results_json)
            output_files['multiple_results_json'] = multiple_results_json
        
        # Save summary statistics
        summary = {
            "total_genes": len(gene_protein_data),
            "successful_matches": len([d for d in csv_data if d["status"] == "Success"]),
            "failed_matches": len([d for d in csv_data if d["status"] == "Gene not found"]),
            "sequences_retrieved": len(fasta_data),
            "alphafold_jobs": len(json_data),
            "genes_with_multiple_results": len(multiple_results_data),
            "single_result_genes": len([d for d in csv_data if d["status"] == "Success" and not d["multiple_results_found"]])
        }
        
        summary_file = f"{output_prefix}_summary.json"
        safe_json_save(summary, summary_file)
        output_files['summary'] = summary_file
        
        self.logger.info(f"Processed {len(gene_protein_data)} genes")
        self.logger.info(f"Successfully matched: {summary['successful_matches']}")
        self.logger.info(f"Failed to match: {summary['failed_matches']}")
        self.logger.info(f"Genes with multiple results: {summary['genes_with_multiple_results']}")
        self.logger.info(f"Generated {len(output_files)} output files")
        
        return output_files 