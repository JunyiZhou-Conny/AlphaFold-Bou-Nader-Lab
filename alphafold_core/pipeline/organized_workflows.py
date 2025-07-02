"""
Organized workflows module for AlphaFold Core
Provides structured workflows with organized outputs and better naming
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .workflows import GeneToProteinPipeline
from ..data import JSONProcessor
from ..utils import setup_logging


class OrganizedWorkflowManager:
    """Manages organized workflows with structured outputs and better naming"""
    
    def __init__(self, base_output_dir: str = "alphafold_output"):
        self.logger = setup_logging()
        self.base_output_dir = Path(base_output_dir)
        self.json_processor = JSONProcessor()
        
        # Create base output directory
        self.base_output_dir.mkdir(exist_ok=True)
    
    def _create_task_directory(self, task_name: str, task_type: str) -> Path:
        """Create organized directory structure for a task"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_dir = self.base_output_dir / task_type / f"{task_name}_{timestamp}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (task_dir / "raw").mkdir(exist_ok=True)
        (task_dir / "processed").mkdir(exist_ok=True)
        (task_dir / "batches").mkdir(exist_ok=True)
        (task_dir / "logs").mkdir(exist_ok=True)
        
        return task_dir
    
    def _generate_task_name(self, input_file: Path, task_type: str) -> str:
        """Generate a meaningful task name based on input file"""
        # Remove common extensions and get base name
        base_name = input_file.stem
        
        # Clean up the name (remove common prefixes/suffixes)
        if base_name.startswith("demo_workflow"):
            base_name = base_name.replace("demo_workflow", "").strip("_")
        
        if not base_name:
            base_name = f"{task_type}_task"
        
        return base_name
    
    def run_gene_to_protein_workflow(self, 
                                   input_file: Path,
                                   output_prefix: Optional[str] = None,
                                   split_json: bool = True,
                                   jobs_per_batch: int = 30,
                                   **kwargs) -> Dict[str, Any]:
        """
        Run gene-to-protein workflow with organized outputs
        
        Args:
            input_file: Path to input TSV file with gene names
            output_prefix: Custom prefix for output files (optional)
            split_json: Whether to split the JSON file into batches
            jobs_per_batch: Number of jobs per batch (default: 30 for AlphaFold3)
            **kwargs: Additional arguments for GeneToProteinPipeline
            
        Returns:
            Dictionary with workflow results and file paths
        """
        # Generate task name and create directory structure
        task_name = self._generate_task_name(input_file, "gene_to_protein")
        if output_prefix:
            task_name = f"{output_prefix}_{task_name}"
        
        task_dir = self._create_task_directory(task_name, "gene_to_protein")
        
        self.logger.info(f"Starting gene-to-protein workflow: {task_name}")
        self.logger.info(f"Output directory: {task_dir}")
        
        # Initialize pipeline
        pipeline = GeneToProteinPipeline()
        
        # Run the pipeline with organized outputs
        start_time = time.time()
        
        try:
            # Process the data
            results = pipeline.process_tsv_file(
                input_file=input_file,
                output_csv=task_dir / "raw" / f"{task_name}.csv",
                output_fasta=task_dir / "raw" / f"{task_name}.fasta",
                output_json=task_dir / "raw" / f"{task_name}.json",
                **kwargs
            )
            
            processing_time = time.time() - start_time
            
            # Split JSON if requested
            split_files = []
            if split_json and results.get('json_file'):
                self.logger.info("Splitting JSON file into batches...")
                split_files = self.json_processor.split_json_by_count(
                    input_file=results['json_file'],
                    output_dir=task_dir / "batches",
                    jobs_per_file=jobs_per_batch,
                    prefix=task_name
                )
            
            # Create summary
            summary = {
                'task_name': task_name,
                'task_type': 'gene_to_protein',
                'input_file': str(input_file),
                'output_directory': str(task_dir),
                'processing_time_seconds': processing_time,
                'results': results,
                'split_files': [str(f) for f in split_files],
                'batch_count': len(split_files),
                'jobs_per_batch': jobs_per_batch,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save summary
            summary_file = task_dir / f"{task_name}_summary.json"
            import json
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"Workflow completed successfully!")
            self.logger.info(f"Processed {results.get('total_genes', 0)} genes")
            self.logger.info(f"Created {len(split_files)} batch files")
            self.logger.info(f"Summary saved to: {summary_file}")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            # Save error log
            error_log = task_dir / "logs" / "error.log"
            with open(error_log, 'w') as f:
                f.write(f"Error: {e}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            
            raise
    
    def run_custom_workflow(self, 
                          workflow_func,
                          task_name: str,
                          task_type: str = "custom",
                          **kwargs) -> Dict[str, Any]:
        """
        Run a custom workflow with organized outputs
        
        Args:
            workflow_func: Function to execute the workflow
            task_name: Name for the task
            task_type: Type of task (for organization)
            **kwargs: Arguments to pass to the workflow function
            
        Returns:
            Dictionary with workflow results
        """
        task_dir = self._create_task_directory(task_name, task_type)
        
        self.logger.info(f"Starting custom workflow: {task_name}")
        self.logger.info(f"Output directory: {task_dir}")
        
        start_time = time.time()
        
        try:
            # Run the workflow function
            results = workflow_func(output_dir=task_dir, **kwargs)
            
            processing_time = time.time() - start_time
            
            # Create summary
            summary = {
                'task_name': task_name,
                'task_type': task_type,
                'output_directory': str(task_dir),
                'processing_time_seconds': processing_time,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save summary
            summary_file = task_dir / f"{task_name}_summary.json"
            import json
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"Custom workflow completed successfully!")
            self.logger.info(f"Summary saved to: {summary_file}")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Custom workflow failed: {e}")
            # Save error log
            error_log = task_dir / "logs" / "error.log"
            with open(error_log, 'w') as f:
                f.write(f"Error: {e}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            
            raise
    
    def split_existing_json(self, 
                           json_file: Path,
                           output_prefix: str,
                           jobs_per_batch: int = 30,
                           output_dir: Optional[Path] = None) -> List[Path]:
        """
        Split an existing JSON file into batches
        
        Args:
            json_file: Path to existing JSON file
            output_prefix: Prefix for output batch files
            jobs_per_batch: Number of jobs per batch
            output_dir: Output directory (optional, uses default if not specified)
            
        Returns:
            List of created batch file paths
        """
        if output_dir is None:
            task_name = self._generate_task_name(json_file, "json_split")
            task_dir = self._create_task_directory(task_name, "json_split")
            output_dir = task_dir / "batches"
        
        self.logger.info(f"Splitting JSON file: {json_file}")
        self.logger.info(f"Output directory: {output_dir}")
        
        split_files = self.json_processor.split_json_by_count(
            input_file=json_file,
            output_dir=output_dir,
            jobs_per_file=jobs_per_batch,
            prefix=output_prefix
        )
        
        self.logger.info(f"Created {len(split_files)} batch files")
        return split_files
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get history of all workflows run"""
        history = []
        
        for task_type_dir in self.base_output_dir.iterdir():
            if task_type_dir.is_dir():
                for task_dir in task_type_dir.iterdir():
                    if task_dir.is_dir():
                        summary_files = list(task_dir.glob("*_summary.json"))
                        for summary_file in summary_files:
                            try:
                                import json
                                with open(summary_file, 'r') as f:
                                    summary = json.load(f)
                                history.append(summary)
                            except Exception as e:
                                self.logger.warning(f"Could not read summary file {summary_file}: {e}")
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return history
    
    def cleanup_old_workflows(self, days_to_keep: int = 30):
        """Clean up old workflow directories"""
        import shutil
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for task_type_dir in self.base_output_dir.iterdir():
            if task_type_dir.is_dir():
                for task_dir in task_type_dir.iterdir():
                    if task_dir.is_dir():
                        # Check if directory is old enough
                        dir_time = datetime.fromtimestamp(task_dir.stat().st_mtime)
                        if dir_time < cutoff_date:
                            try:
                                shutil.rmtree(task_dir)
                                deleted_count += 1
                                self.logger.info(f"Deleted old workflow: {task_dir}")
                            except Exception as e:
                                self.logger.error(f"Could not delete {task_dir}: {e}")
        
        self.logger.info(f"Cleanup completed: deleted {deleted_count} old workflow directories") 