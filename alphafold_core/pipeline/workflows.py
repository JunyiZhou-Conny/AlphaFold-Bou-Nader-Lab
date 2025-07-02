"""
Workflow pipelines for AlphaFold Core
High-level workflows that combine multiple operations
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import logging
import time

from ..config import config
from ..utils import setup_logging, timing_decorator
from ..data import ProteinSequenceFetcher, JSONProcessor, DataProcessor
from ..analysis import OverlapAnalyzer, QualityAnalyzer
from ..analysis.statistics import StatisticalAnalyzer
from ..analysis.comparison import ComparisonAnalyzer
from ..visualization.reports import ReportGenerator


class ProteinAnalysisPipeline:
    """Complete pipeline for protein sequence analysis"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.fetcher = ProteinSequenceFetcher()
        self.processor = DataProcessor()
    
    @timing_decorator
    def run_complete_analysis(self, input_file: str, 
                            input_type: str = "excel",
                            column_name: str = "Protein IDs",
                            header_row: int = 2) -> Dict[str, Any]:
        """Run complete protein analysis pipeline"""
        self.logger.info(f"Starting complete protein analysis for {input_file}")
        
        results = {
            'input_file': input_file,
            'sequences_fetched': {},
            'analysis_summary': {}
        }
        
        # Step 1: Fetch sequences
        if input_type.lower() == "excel":
            sequences = self.fetcher.fetch_from_excel(input_file, column_name, header_row)
        elif input_type.lower() == "csv":
            sequences = self.fetcher.fetch_from_csv(input_file, column_name)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")
        
        results['sequences_fetched'] = sequences
        
        # Step 2: Analyze sequence characteristics
        if sequences:
            sequence_lengths = [len(seq) for seq in sequences.values() if seq != "Sequence Not Found"]
            results['analysis_summary'] = {
                'total_proteins': len(sequences),
                'successful_fetches': len([s for s in sequences.values() if s != "Sequence Not Found"]),
                'failed_fetches': len([s for s in sequences.values() if s == "Sequence Not Found"]),
                'avg_sequence_length': sum(sequence_lengths) / len(sequence_lengths) if sequence_lengths else 0,
                'min_sequence_length': min(sequence_lengths) if sequence_lengths else 0,
                'max_sequence_length': max(sequence_lengths) if sequence_lengths else 0
            }
        
        self.logger.info("Complete protein analysis finished")
        return results


class OverlapAnalysisPipeline:
    """Complete pipeline for overlap analysis between datasets"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.overlap_analyzer = OverlapAnalyzer()
    
    @timing_decorator
    def run_overlap_analysis(self, file_paths: Dict[str, str],
                           id_columns: Dict[str, str],
                           output_prefix: str = "overlap_analysis",
                           create_visualizations: bool = True) -> Dict[str, Any]:
        """Run complete overlap analysis pipeline"""
        self.logger.info("Starting overlap analysis pipeline")
        
        results = {
            'file_paths': file_paths,
            'overlap_results': None,
            'overlap_matrix': None,
            'visualizations': {}
        }
        
        # Step 1: Perform overlap analysis
        overlap_df = self.overlap_analyzer.analyze_from_files(file_paths, id_columns)
        results['overlap_results'] = overlap_df
        
        # Step 2: Create overlap matrix
        datasets = {}
        for name, file_path in file_paths.items():
            df = pd.read_csv(file_path)
            id_col = id_columns.get(name, 'protein_id')
            if id_col in df.columns:
                datasets[name] = set(df[id_col].dropna().unique())
        
        if datasets:
            overlap_matrix = self.overlap_analyzer.create_overlap_matrix(datasets)
            results['overlap_matrix'] = overlap_matrix
        
        # Step 3: Save results
        output_files = self.overlap_analyzer.save_overlap_results(overlap_df, output_prefix)
        results['output_files'] = output_files
        
        # Step 4: Create visualizations
        if create_visualizations and overlap_matrix is not None:
            heatmap_file = f"{output_prefix}_heatmap.png"
            self.overlap_analyzer.plot_overlap_heatmap(overlap_matrix, heatmap_file)
            results['visualizations']['heatmap'] = heatmap_file
            
            if len(datasets) <= 3:
                venn_file = f"{output_prefix}_venn.png"
                self.overlap_analyzer.plot_venn_diagram(datasets, venn_file)
                results['visualizations']['venn'] = venn_file
        
        self.logger.info("Overlap analysis pipeline completed")
        return results


class QualityAssessmentPipeline:
    """Complete pipeline for AlphaFold quality assessment"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.json_processor = JSONProcessor()
        self.data_processor = DataProcessor()
    
    @timing_decorator
    def run_quality_assessment(self, json_directory: str,
                             output_prefix: str = "quality_assessment",
                             iptm_threshold: float = None,
                             ptm_threshold: float = None,
                             ranking_threshold: float = None) -> Dict[str, Any]:
        """Run complete quality assessment pipeline"""
        self.logger.info(f"Starting quality assessment for {json_directory}")
        
        results = {
            'json_directory': json_directory,
            'raw_metrics': None,
            'filtered_metrics': None,
            'quality_summary': {},
            'output_files': {}
        }
        
        # Step 1: Process JSON files
        metrics_df = self.json_processor.process_directory(json_directory)
        results['raw_metrics'] = metrics_df
        
        # Step 2: Apply quality filters
        filtered_df = self.data_processor.filter_dataframe(
            metrics_df, iptm_threshold, ptm_threshold, ranking_threshold
        )
        results['filtered_metrics'] = filtered_df
        
        # Step 3: Generate quality summary
        if not metrics_df.empty:
            results['quality_summary'] = {
                'total_predictions': len(metrics_df),
                'high_quality_predictions': len(filtered_df),
                'quality_rate': len(filtered_df) / len(metrics_df) * 100,
                'avg_iptm': metrics_df['iptm'].mean(),
                'avg_ptm': metrics_df['ptm'].mean(),
                'avg_ranking_score': metrics_df['ranking_score'].mean(),
                'filtered_avg_iptm': filtered_df['iptm'].mean() if not filtered_df.empty else 0,
                'filtered_avg_ptm': filtered_df['ptm'].mean() if not filtered_df.empty else 0,
                'filtered_avg_ranking_score': filtered_df['ranking_score'].mean() if not filtered_df.empty else 0
            }
        
        # Step 4: Save results
        raw_file = f"{output_prefix}_raw_metrics.csv"
        filtered_file = f"{output_prefix}_filtered_metrics.csv"
        
        self.json_processor.save_to_csv(metrics_df, raw_file)
        self.json_processor.save_to_csv(filtered_df, filtered_file)
        
        results['output_files'] = {
            'raw_metrics': raw_file,
            'filtered_metrics': filtered_file
        }
        
        # Step 5: Extract target names if available
        if 'target_protein' in filtered_df.columns:
            target_names = self.data_processor.extract_target_names(filtered_df)
            target_files = self.data_processor.save_target_names(
                target_names, f"{output_prefix}_targets"
            )
            results['output_files'].update(target_files)
        
        self.logger.info("Quality assessment pipeline completed")
        return results


class DataProcessingPipeline:
    """Complete pipeline for general data processing tasks"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.data_processor = DataProcessor()
    
    @timing_decorator
    def run_data_processing(self, input_files: List[str],
                          output_directory: str,
                          operations: List[str],
                          **kwargs) -> Dict[str, Any]:
        """Run complete data processing pipeline"""
        self.logger.info("Starting data processing pipeline")
        
        results = {
            'input_files': input_files,
            'operations': operations,
            'output_directory': output_directory,
            'processed_files': {},
            'operation_results': {}
        }
        
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for operation in operations:
            self.logger.info(f"Executing operation: {operation}")
            
            if operation == "combine_json":
                # Combine multiple JSON files
                combined_file = output_dir / "combined_data.json"
                success = self.data_processor.combine_json_files(
                    input_files[0], combined_file
                )
                results['processed_files']['combined_json'] = str(combined_file) if success else None
                
            elif operation == "modify_json_structure":
                # Modify JSON structure for each file
                modified_files = []
                for input_file in input_files:
                    success = self.data_processor.modify_json_structure(input_file)
                    if success:
                        modified_files.append(input_file)
                results['processed_files']['modified_json'] = modified_files
                
            elif operation == "split_protein_ids":
                # Split protein IDs
                for input_file in input_files:
                    df = pd.read_csv(input_file)
                    protein_column = kwargs.get('protein_column', 'protein_id')
                    if protein_column in df.columns:
                        protein_ids = df[protein_column].dropna().tolist()
                        split_ids = self.data_processor.split_protein_ids(protein_ids)
                        
                        output_file = output_dir / f"{Path(input_file).stem}_split_ids.txt"
                        with open(output_file, 'w') as f:
                            for pid in split_ids:
                                f.write(f"{pid}\n")
                        results['processed_files']['split_ids'] = str(output_file)
                
            else:
                self.logger.warning(f"Unknown operation: {operation}")
        
        self.logger.info("Data processing pipeline completed")
        return results


class GeneToProteinPipeline:
    """Pipeline for processing gene names to protein data"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.fetcher = ProteinSequenceFetcher()
        self.processor = DataProcessor()
    
    @timing_decorator
    def run_gene_to_protein_workflow(self, tsv_file: str,
                                   gene_column: str = "GENE",
                                   output_prefix: str = "gene_protein_workflow") -> Dict:
        """Complete workflow: TSV genes → UniProt search → Multi-format output"""
        self.logger.info(f"Starting gene-to-protein workflow for {tsv_file}")
        
        results = {
            "input_file": tsv_file,
            "gene_column": gene_column,
            "output_prefix": output_prefix,
            "steps": {},
            "output_files": {}
        }
        
        # Step 1: Parse TSV and extract gene names
        self.logger.info("Step 1: Parsing TSV file and extracting gene names")
        try:
            df = pd.read_csv(tsv_file, sep='\t')
            gene_names = df[gene_column].dropna().unique()
            results["steps"]["tsv_parsing"] = {
                "total_rows": len(df),
                "unique_genes": len(gene_names)
            }
            self.logger.info(f"Found {len(gene_names)} unique genes")
        except Exception as e:
            self.logger.error(f"Error parsing TSV file: {e}")
            return {"error": f"Failed to parse TSV file: {e}"}
        
        # Step 2: Search UniProt for each gene
        self.logger.info("Step 2: Searching UniProt for protein information")
        gene_protein_data = self.fetcher.process_genes_to_proteins(tsv_file, gene_column)
        results["steps"]["uniprot_search"] = {
            "genes_searched": len(gene_names),
            "successful_matches": len([d for d in gene_protein_data.values() if "error" not in d]),
            "failed_matches": len([d for d in gene_protein_data.values() if "error" in d])
        }
        
        # Step 3: Process data and generate multiple output formats
        self.logger.info("Step 3: Processing data and generating output files")
        output_files = self.processor.process_gene_to_protein_data(
            gene_protein_data, 
            output_prefix
        )
        results["output_files"] = output_files
        
        # Step 4: Generate summary report
        self.logger.info("Step 4: Generating summary report")
        summary = {
            "workflow": "Gene to Protein Pipeline",
            "input_file": tsv_file,
            "gene_column": gene_column,
            "total_genes_processed": len(gene_names),
            "successful_protein_matches": results["steps"]["uniprot_search"]["successful_matches"],
            "failed_protein_matches": results["steps"]["uniprot_search"]["failed_matches"],
            "success_rate": (results["steps"]["uniprot_search"]["successful_matches"] / len(gene_names)) * 100,
            "output_files_generated": list(output_files.keys()),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save workflow summary
        summary_file = f"{output_prefix}_workflow_summary.json"
        from ..utils import safe_json_save
        safe_json_save(summary, summary_file)
        results["workflow_summary"] = summary
        results["output_files"]["workflow_summary"] = summary_file
        
        self.logger.info("Gene-to-protein workflow completed successfully")
        self.logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"Generated {len(output_files)} output files")
        
        return results

    @timing_decorator
    def run_gene_to_protein_workflow_robust(self, tsv_file: str,
                                          gene_column: str = "GENE",
                                          output_prefix: str = "gene_protein_workflow_robust",
                                          organism_id: str = "9606",
                                          reviewed_only: bool = True,
                                          exact_match: bool = True) -> Dict:
        """Complete workflow with robust search strategies"""
        from ..data.fetcher import SearchCriteria
        
        self.logger.info(f"Starting robust gene-to-protein workflow for {tsv_file}")
        
        # Create search criteria
        criteria = SearchCriteria(
            organism_id=organism_id,
            reviewed_only=reviewed_only,
            exact_match=exact_match,
            max_results=10
        )
        
        results = {
            "input_file": tsv_file,
            "gene_column": gene_column,
            "output_prefix": output_prefix,
            "search_criteria": {
                "organism_id": criteria.organism_id,
                "reviewed_only": criteria.reviewed_only,
                "exact_match": criteria.exact_match
            },
            "steps": {},
            "output_files": {}
        }
        
        # Step 1: Parse TSV and extract gene names
        self.logger.info("Step 1: Parsing TSV file and extracting gene names")
        try:
            df = pd.read_csv(tsv_file, sep='\t')
            gene_names = df[gene_column].dropna().unique()
            results["steps"]["tsv_parsing"] = {
                "total_rows": len(df),
                "unique_genes": len(gene_names)
            }
            self.logger.info(f"Found {len(gene_names)} unique genes")
        except Exception as e:
            self.logger.error(f"Error parsing TSV file: {e}")
            return {"error": f"Failed to parse TSV file: {e}"}
        
        # Step 2: Search UniProt with robust strategies
        self.logger.info("Step 2: Searching UniProt with robust strategies")
        gene_protein_data = self.fetcher.process_genes_to_proteins_robust(
            tsv_file, gene_column, criteria
        )
        results["steps"]["uniprot_search"] = {
            "genes_searched": len(gene_names),
            "successful_matches": len([d for d in gene_protein_data.values() if "error" not in d]),
            "failed_matches": len([d for d in gene_protein_data.values() if "error" in d])
        }
        
        # Step 3: Process data and generate multiple output formats
        self.logger.info("Step 3: Processing data and generating output files")
        output_files = self.processor.process_gene_to_protein_data(
            gene_protein_data, 
            output_prefix
        )
        results["output_files"] = output_files
        
        # Step 4: Generate summary report
        self.logger.info("Step 4: Generating summary report")
        
        # Count genes with multiple results
        genes_with_multiple_results = 0
        for protein_info in gene_protein_data.values():
            if "error" not in protein_info and protein_info.get("multiple_results_found", False):
                genes_with_multiple_results += 1
        
        summary = {
            "workflow": "Robust Gene to Protein Pipeline",
            "input_file": tsv_file,
            "gene_column": gene_column,
            "search_criteria": results["search_criteria"],
            "total_genes_processed": len(gene_names),
            "successful_protein_matches": results["steps"]["uniprot_search"]["successful_matches"],
            "failed_protein_matches": results["steps"]["uniprot_search"]["failed_matches"],
            "success_rate": (results["steps"]["uniprot_search"]["successful_matches"] / len(gene_names)) * 100,
            "genes_with_multiple_results": genes_with_multiple_results,
            "single_result_genes": results["steps"]["uniprot_search"]["successful_matches"] - genes_with_multiple_results,
            "multiple_results_rate": (genes_with_multiple_results / results["steps"]["uniprot_search"]["successful_matches"] * 100) if results["steps"]["uniprot_search"]["successful_matches"] > 0 else 0,
            "output_files_generated": list(output_files.keys()),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save workflow summary
        summary_file = f"{output_prefix}_workflow_summary.json"
        from ..utils import safe_json_save
        safe_json_save(summary, summary_file)
        results["workflow_summary"] = summary
        results["output_files"]["workflow_summary"] = summary_file
        
        self.logger.info("Robust gene-to-protein workflow completed successfully")
        self.logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"Genes with multiple results: {genes_with_multiple_results}")
        self.logger.info(f"Multiple results rate: {summary['multiple_results_rate']:.1f}%")
        self.logger.info(f"Generated {len(output_files)} output files")
        
        return results
    
    def run_batch_processing(self, tsv_files: List[str],
                           gene_column: str = "GENE",
                           output_dir: str = "batch_results") -> Dict:
        """Process multiple TSV files in batch"""
        self.logger.info(f"Starting batch processing of {len(tsv_files)} files")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        batch_results = {
            "batch_size": len(tsv_files),
            "output_directory": str(output_dir),
            "individual_results": {},
            "batch_summary": {}
        }
        
        successful_files = 0
        total_genes = 0
        total_successful_matches = 0
        
        for i, tsv_file in enumerate(tsv_files):
            self.logger.info(f"Processing file {i+1}/{len(tsv_files)}: {tsv_file}")
            
            try:
                output_prefix = output_dir / f"batch_{i+1}_{Path(tsv_file).stem}"
                result = self.run_gene_to_protein_workflow(
                    tsv_file, 
                    gene_column, 
                    str(output_prefix)
                )
                
                if "error" not in result:
                    successful_files += 1
                    total_genes += result["steps"]["tsv_parsing"]["unique_genes"]
                    total_successful_matches += result["steps"]["uniprot_search"]["successful_matches"]
                
                batch_results["individual_results"][tsv_file] = result
                
            except Exception as e:
                self.logger.error(f"Error processing {tsv_file}: {e}")
                batch_results["individual_results"][tsv_file] = {"error": str(e)}
        
        # Generate batch summary
        batch_results["batch_summary"] = {
            "total_files": len(tsv_files),
            "successful_files": successful_files,
            "total_genes_processed": total_genes,
            "total_successful_matches": total_successful_matches,
            "overall_success_rate": (total_successful_matches / total_genes * 100) if total_genes > 0 else 0
        }
        
        # Save batch summary
        batch_summary_file = output_dir / "batch_summary.json"
        from ..utils import safe_json_save
        safe_json_save(batch_results["batch_summary"], batch_summary_file)
        
        self.logger.info("Batch processing completed")
        self.logger.info(f"Successfully processed: {successful_files}/{len(tsv_files)} files")
        self.logger.info(f"Overall success rate: {batch_results['batch_summary']['overall_success_rate']:.1f}%")
        
        return batch_results

    def run_batch_processing_robust(self, tsv_files: List[str],
                                  gene_column: str = "GENE",
                                  output_dir: str = "batch_results_robust",
                                  organism_id: str = "9606",
                                  reviewed_only: bool = True,
                                  exact_match: bool = True) -> Dict:
        """Process multiple TSV files in batch with robust search strategies"""
        self.logger.info(f"Starting robust batch processing of {len(tsv_files)} files")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        batch_results = {
            "batch_size": len(tsv_files),
            "output_directory": str(output_dir),
            "search_criteria": {
                "organism_id": organism_id,
                "reviewed_only": reviewed_only,
                "exact_match": exact_match
            },
            "individual_results": {},
            "batch_summary": {}
        }
        
        successful_files = 0
        total_genes = 0
        total_successful_matches = 0
        
        for i, tsv_file in enumerate(tsv_files):
            self.logger.info(f"Processing file {i+1}/{len(tsv_files)}: {tsv_file}")
            
            try:
                output_prefix = output_dir / f"batch_{i+1}_{Path(tsv_file).stem}"
                result = self.run_gene_to_protein_workflow_robust(
                    tsv_file, 
                    gene_column, 
                    str(output_prefix),
                    organism_id,
                    reviewed_only,
                    exact_match
                )
                
                if "error" not in result:
                    successful_files += 1
                    total_genes += result["steps"]["tsv_parsing"]["unique_genes"]
                    total_successful_matches += result["steps"]["uniprot_search"]["successful_matches"]
                
                batch_results["individual_results"][tsv_file] = result
                
            except Exception as e:
                self.logger.error(f"Error processing {tsv_file}: {e}")
                batch_results["individual_results"][tsv_file] = {"error": str(e)}
        
        # Generate batch summary
        batch_results["batch_summary"] = {
            "total_files": len(tsv_files),
            "successful_files": successful_files,
            "total_genes_processed": total_genes,
            "total_successful_matches": total_successful_matches,
            "overall_success_rate": (total_successful_matches / total_genes * 100) if total_genes > 0 else 0
        }
        
        # Save batch summary
        batch_summary_file = output_dir / "batch_summary.json"
        from ..utils import safe_json_save
        safe_json_save(batch_results["batch_summary"], batch_summary_file)
        
        self.logger.info("Robust batch processing completed")
        self.logger.info(f"Successfully processed: {successful_files}/{len(tsv_files)} files")
        self.logger.info(f"Overall success rate: {batch_results['batch_summary']['overall_success_rate']:.1f}%")
        
        return batch_results


class AF3SummaryAnalysisWorkflow:
    """Comprehensive workflow for AF3 summary statistics analysis"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.json_processor = JSONProcessor()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.quality_analyzer = QualityAnalyzer()
        self.comparison_analyzer = ComparisonAnalyzer()
        self.report_generator = ReportGenerator()
        self.data_processor = DataProcessor()
    
    def run_af3_analysis_workflow(self, 
                                input_source: Union[str, Path, pd.DataFrame],
                                output_prefix: str = "af3_analysis",
                                analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Run comprehensive AF3 analysis workflow
        
        Args:
            input_source: Can be:
                - Directory path (for JSON processing)
                - CSV file path (for existing summary stats)
                - DataFrame (for direct analysis)
            output_prefix: Prefix for output files
            analysis_type: "comprehensive", "quality_only", "statistics_only"
        
        Returns:
            Dictionary containing all analysis results and file paths
        """
        self.logger.info(f"Starting AF3 analysis workflow with prefix: {output_prefix}")
        
        results = {
            'workflow_type': 'af3_summary_analysis',
            'input_source': str(input_source),
            'output_prefix': output_prefix,
            'analysis_type': analysis_type,
            'output_files': {},
            'analysis_results': {}
        }
        
        # Step 1: Load/Process Data
        df = self._load_data(input_source, output_prefix)
        if df is None or df.empty:
            self.logger.error("No data loaded for analysis")
            return results
        
        results['data_info'] = {
            'total_predictions': len(df),
            'columns': list(df.columns),
            'numeric_columns': list(df.select_dtypes(include=['number']).columns)
        }
        
        # Step 2: Quality Analysis
        if analysis_type in ["comprehensive", "quality_only"]:
            quality_results = self._perform_quality_analysis(df, output_prefix)
            results['analysis_results']['quality'] = quality_results
            results['output_files'].update(quality_results.get('output_files', {}))
        
        # Step 3: Statistical Analysis
        if analysis_type in ["comprehensive", "statistics_only"]:
            stats_results = self._perform_statistical_analysis(df, output_prefix)
            results['analysis_results']['statistics'] = stats_results
            results['output_files'].update(stats_results.get('output_files', {}))
        
        # Step 4: Comparison Analysis (if multiple datasets)
        if analysis_type == "comprehensive" and self._has_multiple_datasets(df):
            comparison_results = self._perform_comparison_analysis(df, output_prefix)
            results['analysis_results']['comparison'] = comparison_results
            results['output_files'].update(comparison_results.get('output_files', {}))
        
        # Step 5: Generate Comprehensive Report
        if analysis_type == "comprehensive":
            report_results = self._generate_comprehensive_report(df, results, output_prefix)
            results['output_files'].update(report_results.get('output_files', {}))
        
        self.logger.info(f"✅ AF3 analysis workflow completed. Output prefix: {output_prefix}")
        return results
    
    def _load_data(self, input_source: Union[str, Path, pd.DataFrame], 
                  output_prefix: str) -> Optional[pd.DataFrame]:
        """Load data from various sources"""
        try:
            if isinstance(input_source, pd.DataFrame):
                df = input_source.copy()
                self.logger.info(f"Loaded DataFrame with {len(df)} rows")
                return df
            
            input_path = Path(input_source)
            
            if input_path.is_file() and input_path.suffix.lower() == '.csv':
                # Load existing CSV file
                df = pd.read_csv(input_path)
                self.logger.info(f"Loaded CSV file: {input_path} with {len(df)} rows")
                return df
            
            elif input_path.is_dir():
                # Check if it's a triple_overlap directory (no fold groups)
                files_in_dir = list(input_path.glob("*"))
                json_files = [f for f in files_in_dir if f.is_file() and f.suffix.lower() == '.json']
                
                if json_files:
                    # Check if any files match triple_overlap pattern
                    triple_overlap_files = [f for f in json_files if 'triple_overlap' in f.name or 'summary_confidences' in f.name]
                    
                    if triple_overlap_files:
                        # Use triple_overlap processing
                        df = self.json_processor.process_triple_overlap_json_files(input_path)
                        if not df.empty:
                            # Save the processed data
                            output_csv = f"{output_prefix}_summary_metrics.csv"
                            df.to_csv(output_csv, index=False)
                            self.logger.info(f"Processed triple_overlap JSON files from directory: {input_path}")
                            self.logger.info(f"Saved processed data to: {output_csv}")
                            return df
                    
                    # Fallback to standard AF3 processing
                    df, missing_report = self.json_processor.process_af3_results(
                        input_path, f"{output_prefix}_summary_metrics.csv"
                    )
                    self.logger.info(f"Processed standard AF3 JSON files from directory: {input_path}")
                    return df
            
            else:
                self.logger.error(f"Unsupported input source: {input_source}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return None
    
    def _perform_quality_analysis(self, df: pd.DataFrame, 
                                output_prefix: str) -> Dict[str, Any]:
        """Perform quality analysis on AF3 data"""
        self.logger.info("Performing quality analysis...")
        
        results = {
            'output_files': {},
            'quality_assessment': {},
            'filtered_data': {}
        }
        
        # Quality assessment
        quality_assessment = self.quality_analyzer.assess_prediction_quality(df)
        results['quality_assessment'] = quality_assessment
        
        # Generate quality report
        quality_report_file = f"{output_prefix}_quality_report.txt"
        quality_report = self.quality_analyzer.generate_quality_report(df, quality_report_file)
        results['output_files']['quality_report'] = quality_report_file
        
        # Create quality plots
        quality_plots_file = f"{output_prefix}_quality_distributions.png"
        self.quality_analyzer.plot_quality_distributions(df, quality_plots_file)
        results['output_files']['quality_plots'] = quality_plots_file
        
        # Filter high-quality predictions
        high_quality_df = self.quality_analyzer.filter_high_quality_predictions(df)
        high_quality_file = f"{output_prefix}_high_quality_predictions.csv"
        high_quality_df.to_csv(high_quality_file, index=False)
        results['output_files']['high_quality_predictions'] = high_quality_file
        results['filtered_data']['high_quality'] = {
            'count': len(high_quality_df),
            'percentage': (len(high_quality_df) / len(df)) * 100
        }
        
        # Identify outliers
        outliers = self.quality_analyzer.identify_outliers(df)
        results['quality_assessment']['outliers'] = outliers
        
        return results
    
    def _perform_statistical_analysis(self, df: pd.DataFrame, 
                                   output_prefix: str) -> Dict[str, Any]:
        """Perform statistical analysis on AF3 data"""
        self.logger.info("Performing statistical analysis...")
        
        results = {
            'output_files': {},
            'statistical_summary': {},
            'hypothesis_tests': {}
        }
        
        # Get numeric columns for analysis
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        # Descriptive statistics
        stats_analysis = self.statistical_analyzer.analyze_dataframe_statistics(df, numeric_columns)
        results['statistical_summary'] = stats_analysis
        
        # Generate statistical report
        stats_report_file = f"{output_prefix}_statistical_report.txt"
        stats_report = self.statistical_analyzer.create_statistical_report(df, stats_report_file)
        results['output_files']['statistical_report'] = stats_report_file
        
        # Create statistical plots
        stats_plots_file = f"{output_prefix}_statistical_summary.png"
        self.statistical_analyzer.plot_statistical_summary(df, stats_plots_file)
        results['output_files']['statistical_plots'] = stats_plots_file
        
        # Correlation analysis
        if len(numeric_columns) > 1:
            correlation_file = f"{output_prefix}_correlation_matrix.png"
            self.statistical_analyzer.plot_correlation_matrix(df, correlation_file)
            results['output_files']['correlation_matrix'] = correlation_file
        
        # Confidence intervals for key metrics
        key_metrics = ['iptm', 'ptm', 'ranking_score']
        confidence_intervals = {}
        for metric in key_metrics:
            if metric in df.columns:
                ci = self.statistical_analyzer.calculate_confidence_intervals(df[metric])
                confidence_intervals[metric] = ci
        
        results['statistical_summary']['confidence_intervals'] = confidence_intervals
        
        return results
    
    def _perform_comparison_analysis(self, df: pd.DataFrame, 
                                   output_prefix: str) -> Dict[str, Any]:
        """Perform comparison analysis if multiple datasets are present"""
        self.logger.info("Performing comparison analysis...")
        
        results = {
            'output_files': {},
            'comparison_results': {}
        }
        
        # Check if we have fold groups to compare
        if 'fold_group' in df.columns:
            fold_groups = df['fold_group'].unique()
            if len(fold_groups) > 1:
                # Compare quality metrics across fold groups
                datasets = {}
                for group in fold_groups:
                    group_data = df[df['fold_group'] == group]
                    datasets[f"fold_group_{group}"] = group_data
                
                comparison_results = self.comparison_analyzer.compare_quality_metrics(
                    datasets, ['iptm', 'ptm', 'ranking_score']
                )
                results['comparison_results'] = comparison_results
                
                # Generate comparison report
                comparison_report_file = f"{output_prefix}_comparison_report.txt"
                comparison_report = self.comparison_analyzer.create_comparison_report(
                    comparison_results, comparison_report_file
                )
                results['output_files']['comparison_report'] = comparison_report_file
                
                # Create comparison plots
                comparison_plots_file = f"{output_prefix}_comparison_summary.png"
                self.comparison_analyzer.plot_comparison_summary(
                    comparison_results, comparison_plots_file
                )
                results['output_files']['comparison_plots'] = comparison_plots_file
        
        return results
    
    def _generate_comprehensive_report(self, df: pd.DataFrame, 
                                     workflow_results: Dict[str, Any],
                                     output_prefix: str) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        self.logger.info("Generating comprehensive report...")
        
        results = {
            'output_files': {}
        }
        
        # Generate comprehensive report
        comprehensive_report_file = f"{output_prefix}_comprehensive_report.txt"
        report_content = self._create_comprehensive_report_content(df, workflow_results)
        
        with open(comprehensive_report_file, 'w') as f:
            f.write(report_content)
        
        results['output_files']['comprehensive_report'] = comprehensive_report_file
        
        return results
    
    def _create_comprehensive_report_content(self, df: pd.DataFrame, 
                                           workflow_results: Dict[str, Any]) -> str:
        """Create comprehensive report content"""
        report_lines = []
        report_lines.append("AF3 Summary Statistics - Comprehensive Analysis Report")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Data Overview
        report_lines.append("DATA OVERVIEW")
        report_lines.append("-" * 20)
        report_lines.append(f"Total Predictions: {len(df)}")
        report_lines.append(f"Analysis Type: {workflow_results['analysis_type']}")
        report_lines.append("")
        
        # Quality Analysis Summary
        if 'quality' in workflow_results['analysis_results']:
            quality = workflow_results['analysis_results']['quality']
            report_lines.append("QUALITY ANALYSIS SUMMARY")
            report_lines.append("-" * 30)
            
            if 'quality_assessment' in quality:
                assessment = quality['quality_assessment']
                report_lines.append(f"Total Predictions: {assessment.get('total_predictions', 'N/A')}")
                
                if 'quality_breakdown' in assessment:
                    for metric, stats in assessment['quality_breakdown'].items():
                        report_lines.append(f"{metric.upper()}:")
                        report_lines.append(f"  - High Quality: {stats['high_quality_count']} ({stats['high_quality_percentage']:.1f}%)")
                        report_lines.append(f"  - Mean: {stats['mean_value']:.3f}")
                        report_lines.append(f"  - Threshold: {stats['threshold']}")
            
            if 'filtered_data' in quality and 'high_quality' in quality['filtered_data']:
                high_quality = quality['filtered_data']['high_quality']
                report_lines.append(f"High Quality Predictions: {high_quality['count']} ({high_quality['percentage']:.1f}%)")
            
            report_lines.append("")
        
        # Statistical Analysis Summary
        if 'statistics' in workflow_results['analysis_results']:
            stats = workflow_results['analysis_results']['statistics']
            report_lines.append("STATISTICAL ANALYSIS SUMMARY")
            report_lines.append("-" * 35)
            
            if 'statistical_summary' in stats:
                summary = stats['statistical_summary']
                if 'statistics' in summary:
                    for column, column_stats in summary['statistics'].items():
                        report_lines.append(f"{column.upper()}:")
                        report_lines.append(f"  - Mean: {column_stats['mean']:.3f}")
                        report_lines.append(f"  - Median: {column_stats['median']:.3f}")
                        report_lines.append(f"  - Std: {column_stats['std']:.3f}")
                        report_lines.append(f"  - Range: {column_stats['min']:.3f} - {column_stats['max']:.3f}")
            
            report_lines.append("")
        
        # Output Files
        report_lines.append("OUTPUT FILES")
        report_lines.append("-" * 15)
        for file_type, file_path in workflow_results['output_files'].items():
            report_lines.append(f"- {file_type}: {file_path}")
        
        return '\n'.join(report_lines)
    
    def _has_multiple_datasets(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame contains multiple datasets for comparison"""
        return 'fold_group' in df.columns and len(df['fold_group'].unique()) > 1 