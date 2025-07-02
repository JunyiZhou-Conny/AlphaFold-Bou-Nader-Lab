# Dicer_685_Project Documentation

This is an **ongoing AlphaFold project** focused on analyzing protein interactions between Dicer (Q9UPY3 · DICER_HUMAN) and potential interacting proteins. The project demonstrates the evolution from scattered demo files to a properly organized hierarchical structure using the alphafold_core system.

## 📁 Project Structure

```
Dicer_685_Project/
├── data/                                  # 📊 Data files
│   ├── raw/                               # Original data files
│   │   └── venn2_overlap.tsv              # Original TSV file with gene names
│   └── processed/                         # Processed data files
│       ├── gene_to_protein_results.csv    # Gene query results
│       ├── protein_sequences.fasta        # Protein sequences
│       └── protein_metadata.json          # Protein metadata
├── alphafold_output/                      # 📈 AlphaFold3 outputs
│   ├── json_split/                        # JSON batches for AF3
│   │   └── gene_to_protein_corrected_20250620_103808/  # Timestamped output
│   │       ├── batches/                   # Batch files (30 jobs each)
│   │       │   ├── batch_001.json         # Batch 1
│   │       │   ├── batch_002.json         # Batch 2
│   │       │   └── ...                    # Additional batches
│   │       ├── gene_to_protein_corrected.csv  # Gene query results
│   │       ├── gene_to_protein_corrected.fasta # Protein sequences
│   │       ├── gene_to_protein_corrected_alphafold.json # Master JSON
│   │       └── gene_to_protein_corrected_summary.json # Workflow summary
│   ├── predictions/                       # 🔄 Future: AF3 prediction results
│   └── analysis/                          # 📋 Future: Analysis results
├── results/                               # 📊 Analysis results
│   ├── summaries/                         # 📋 Future: Summary statistics
│   ├── visualizations/                    # 📋 Future: Plots and charts
│   └── reports/                           # 📋 Future: Final reports
├── temp_demo_files/                       # 🗑️ Demo files (to be cleaned up)
│   ├── demo_workflow.csv                  # Demo CSV output
│   ├── demo_workflow.fasta                # Demo FASTA output
│   ├── demo_workflow_alphafold.json       # Demo JSON output
│   ├── demo_workflow_summary.json         # Demo summary
│   ├── step_by_step_demo.csv              # Step-by-step demo CSV
│   ├── step_by_step_demo.fasta            # Step-by-step demo FASTA
│   ├── step_by_step_demo_alphafold.json   # Step-by-step demo JSON
│   └── step_by_step_demo_summary.json     # Step-by-step demo summary
├── protein_interaction_batches/           # 📦 Batch files directory
├── protein_interaction_batches.zip        # 📦 Compressed batch files
├── protein_interaction_jobs.json          # 📄 Master JSON file (2.0MB)
├── dicer.fasta                            # 🧬 Dicer protein sequence
├── venn2_overlap.tsv                      # 📊 Original overlap data
├── venn2_overlap (2).tsv                  # 📊 Duplicate overlap data
├── run_af3_toy.sh                         # 🐚 Shell script for AF3 testing
├── run_organized_gene_to_protein.py       # ✅ DOCUMENTED - Main workflow script
├── run_gene_to_protein_task.py            # ✅ DOCUMENTED - Task execution script
├── split_corrected_json.py                # ✅ DOCUMENTED - JSON splitting utility
├── split_existing_json.py                 # ✅ DOCUMENTED - Existing JSON splitting
├── regenerate_batches.py                  # ✅ DOCUMENTED - Batch regeneration
├── modify_json.py                         # ✅ DOCUMENTED - JSON modification utility
├── test_structure.py                      # ✅ DOCUMENTED - Structure testing
└── [various system files]                 # .DS_Store and cache files
```

## 🔄 Workflow Analysis

### **Phase 1: Data Preparation & Gene Querying** ✅ **COMPLETED**
**Files Involved:**
- `data/raw/venn2_overlap.tsv` - **Input data** (gene names)
- `scripts/run_organized_gene_to_protein.py` - **Main workflow script**
- `alphafold_output/json_split/gene_to_protein_corrected_20250620_103808/` - **Output directory**

**Process:**
1. **Data Loading:** TSV file with gene names from overlap analysis
2. **Gene Querying:** Query UniProt API for protein accessions using gene names
3. **Data Processing:** Generate CSV, FASTA, and JSON formats
4. **Quality Control:** Handle failed queries and ambiguous results
5. **Output Generation:** Create organized output with timestamps

**Key Features:**
- ✅ **Organized Workflow:** Uses `OrganizedWorkflowManager` from alphafold_core
- ✅ **Timestamped Outputs:** Automatic timestamp-based directory creation
- ✅ **Comprehensive Logging:** Detailed logging and progress tracking
- ✅ **Multiple Formats:** CSV, FASTA, and JSON outputs generated automatically

### **Phase 2: JSON Organization & Batch Splitting** ✅ **COMPLETED**
**Files Involved:**
- `alphafold_output/json_split/gene_to_protein_corrected_20250620_103808/gene_to_protein_corrected_alphafold.json` - **Master JSON**
- `scripts/split_corrected_json.py` - **JSON splitting utility**
- `alphafold_output/json_split/gene_to_protein_corrected_20250620_103808/batches/` - **Batch files**

**Process:**
1. **Master JSON Creation:** Generate comprehensive JSON with all protein interactions
2. **Batch Splitting:** Split into smaller batches (30 jobs per batch for AlphaFold3 daily limits)
3. **Quality Validation:** Ensure each batch is properly formatted
4. **Distribution Preparation:** Ready for AlphaFold3 server submission

**Key Features:**
- ✅ **Automatic Splitting:** Configurable batch sizes (30 jobs per batch)
- ✅ **Format Validation:** Ensures proper JSON structure for AlphaFold3
- ✅ **Batch Organization:** Clear naming convention for easy tracking
- ✅ **Error Handling:** Graceful handling of splitting errors

### **Phase 3: AlphaFold3 Processing** 🔄 **PENDING**
**Files Involved:**
- `alphafold_output/json_split/gene_to_protein_corrected_20250620_103808/batches/` - **Input batches**
- `scripts/run_af3_toy.sh` - **AF3 submission script**
- `alphafold_output/predictions/` - **Future prediction results**

**Process:**
1. **Batch Submission:** Submit batch JSON files to AlphaFold3 server
2. **Progress Monitoring:** Track prediction progress and completion
3. **Result Collection:** Download and organize prediction results
4. **Quality Assessment:** Initial quality checks on predictions

**Status:** 🔄 **Pending - Ready for execution**

### **Phase 4: Result Analysis & Summary Statistics** 📋 **PLANNED**
**Files Involved:**
- `alphafold_output/predictions/` - **Prediction results** (future)
- `results/summaries/` - **Summary statistics** (future)
- `results/visualizations/` - **Plots and charts** (future)
- `results/reports/` - **Final reports** (future)

**Process:**
1. **Data Collection:** Gather all AlphaFold3 prediction results
2. **Quality Analysis:** Assess prediction quality using iptm, ptm, ranking_score
3. **Summary Statistics:** Generate comprehensive statistics
4. **Visualization:** Create plots and charts for analysis
5. **Report Generation:** Produce final analysis reports

**Status:** 📋 **Planned - Structure prepared**

## 📚 Documented Components

### ✅ **1. Organized Gene-to-Protein Workflow**
**File:** `scripts/run_organized_gene_to_protein.py`
**Status:** ✅ **FULLY DOCUMENTED**

**What it does:**
- Implements the main workflow using `OrganizedWorkflowManager` from alphafold_core
- Processes TSV files with gene names and converts them to protein data
- Generates organized output with timestamps and proper directory structure
- Creates multiple output formats (CSV, FASTA, JSON) automatically
- Provides comprehensive logging and progress tracking

**Key Features:**
- ✅ **Hierarchical Structure:** Uses alphafold_core's organized workflow system
- ✅ **Timestamped Outputs:** Automatic timestamp-based directory creation
- ✅ **Multiple Output Formats:** CSV, FASTA, and JSON generated simultaneously
- ✅ **Batch Splitting:** Automatic JSON splitting for AlphaFold3 daily limits
- ✅ **Comprehensive Logging:** Detailed logging and error reporting
- ✅ **Configuration Management:** No hard-coded paths, configurable parameters

**Workflow Implementation:**
```python
# Initialize the organized workflow manager
workflow_manager = OrganizedWorkflowManager(base_output_dir="alphafold_output")

# Run the organized workflow
results = workflow_manager.run_gene_to_protein_workflow(
    input_file=input_file,
    output_prefix="dicer_685_project",
    split_json=True,
    jobs_per_batch=30
)
```

**Data Processing:**
- **Input:** TSV file with gene names from overlap analysis
- **Processing:** Gene name querying, protein sequence fetching, format conversion
- **Output:** 
  - `gene_to_protein_corrected.csv` - Gene query results
  - `gene_to_protein_corrected.fasta` - Protein sequences
  - `gene_to_protein_corrected_alphafold.json` - Master JSON file
  - `batches/` - Split JSON files for AlphaFold3

**Replaced by:**
- ✅ **`alphafold_core/pipeline/organized_workflows.py`** - `OrganizedWorkflowManager`
- ✅ **`alphafold_core/pipeline/workflows.py`** - `GeneToProteinPipeline`
- ✅ **`alphafold_core/data/fetcher.py`** - `ProteinSequenceFetcher`
- ✅ **`alphafold_core/data/processor.py`** - `DataProcessor`

### ✅ **2. JSON Processing and Batch Splitting**
**File:** `scripts/split_corrected_json.py`
**Status:** ✅ **FULLY DOCUMENTED**

**What it does:**
- Splits the master JSON file into smaller batches for AlphaFold3 processing
- Ensures each batch contains the optimal number of jobs (30 per batch)
- Validates JSON structure and format for AlphaFold3 compatibility
- Provides batch organization and naming conventions

**Key Features:**
- ✅ **Automatic Splitting:** Configurable batch sizes for AlphaFold3 daily limits
- ✅ **Format Validation:** Ensures proper JSON structure for server submission
- ✅ **Batch Organization:** Clear naming convention for easy tracking
- ✅ **Error Handling:** Graceful handling of splitting errors and validation

**Splitting Logic:**
```python
def split_json_file(json_file, output_dir, jobs_per_batch=30):
    """Split JSON file into batches for AlphaFold3 processing"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Split into batches
    batches = [data[i:i + jobs_per_batch] for i in range(0, len(data), jobs_per_batch)]
    
    # Save each batch
    for i, batch in enumerate(batches, 1):
        batch_file = output_dir / f"batch_{i:03d}.json"
        with open(batch_file, 'w') as f:
            json.dump(batch, f, indent=2)
```

**Data Processing:**
- **Input:** Master JSON file with all protein interaction jobs
- **Processing:** Batch splitting, format validation, file organization
- **Output:** Multiple batch JSON files ready for AlphaFold3 submission

**Replaced by:**
- ✅ **`alphafold_core/data/json_processor.py`** - `JSONProcessor` with `split_json_by_count` method
- ✅ **`alphafold_core/pipeline/organized_workflows.py`** - `split_existing_json` method

### ✅ **3. Task Execution and Management**
**File:** `scripts/run_gene_to_protein_task.py`
**Status:** ✅ **FULLY DOCUMENTED**

**What it does:**
- Provides a simplified interface for running gene-to-protein tasks
- Handles task execution with proper error handling and logging
- Manages workflow state and progress tracking
- Integrates with the organized workflow system

**Key Features:**
- ✅ **Simplified Interface:** Easy-to-use task execution wrapper
- ✅ **Error Handling:** Comprehensive error handling and recovery
- ✅ **Progress Tracking:** Real-time progress monitoring
- ✅ **State Management:** Maintains workflow state and history

**Task Execution:**
```python
def run_gene_to_protein_task(tsv_file, output_prefix="task"):
    """Run a gene-to-protein task with simplified interface"""
    try:
        workflow_manager = OrganizedWorkflowManager()
        results = workflow_manager.run_gene_to_protein_workflow(
            input_file=tsv_file,
            output_prefix=output_prefix,
            split_json=True
        )
        return results
    except Exception as e:
        print(f"Task execution failed: {e}")
        return None
```

**Replaced by:**
- ✅ **`alphafold_core/pipeline/organized_workflows.py`** - Integrated task management
- ✅ **`alphafold_core/pipeline/workflows.py`** - `GeneToProteinPipeline`

### ✅ **4. JSON Modification and Regeneration**
**Files:** `scripts/modify_json.py`, `scripts/regenerate_batches.py`
**Status:** ✅ **FULLY DOCUMENTED**

**What they do:**
- **`modify_json.py`:** Modifies existing JSON files for specific requirements
- **`regenerate_batches.py`:** Regenerates batch files from modified master JSON

**Key Features:**
- ✅ **JSON Modification:** Flexible JSON editing capabilities
- ✅ **Batch Regeneration:** Automatic batch recreation after modifications
- ✅ **Validation:** Ensures modified JSON maintains proper structure
- ✅ **Backup Management:** Creates backups before modifications

**Replaced by:**
- ✅ **`alphafold_core/data/processor.py`** - `modify_json_structure` method
- ✅ **`alphafold_core/data/json_processor.py`** - `JSONProcessor` with modification capabilities

### ✅ **5. Structure Testing and Validation**
**File:** `scripts/test_structure.py`
**Status:** ✅ **FULLY DOCUMENTED**

**What it does:**
- Tests and validates the structure of generated files
- Ensures proper formatting and compatibility
- Provides quality checks for AlphaFold3 submission
- Generates validation reports

**Key Features:**
- ✅ **Structure Validation:** Comprehensive file structure testing
- ✅ **Format Checking:** Ensures proper JSON, CSV, and FASTA formats
- ✅ **Compatibility Testing:** Validates AlphaFold3 compatibility
- ✅ **Quality Reporting:** Generates detailed validation reports

**Replaced by:**
- ✅ **`alphafold_core/utils.py`** - `test_file_structure`, `validate_alphafold_json_structure` functions
- ✅ **`alphafold_core/analysis/quality.py`** - `QualityAnalyzer` for structure validation

## 🗑️ Redundant Scripts Analysis

### **🔄 Keep for Documentation:**
- `scripts/run_organized_gene_to_protein.py` - **Main workflow script** (✅ DOCUMENTED)
- `scripts/split_corrected_json.py` - **JSON splitting utility** (✅ DOCUMENTED)
- `scripts/run_gene_to_protein_task.py` - **Task execution script** (✅ DOCUMENTED)

### **🔄 Keep for Current Use:**
- `scripts/regenerate_batches.py` - **Batch regeneration utility**
- `scripts/modify_json.py` - **JSON modification utility**
- `scripts/test_structure.py` - **Structure testing utility**

### **🗑️ Clean Up (Demo Files):**
- `temp_demo_files/demo_workflow*` - **Demo files** (to be removed)
- `temp_demo_files/step_by_step_demo*` - **Step-by-step demo files** (to be removed)

### **🔄 Consolidate into alphafold_core:**
- All utility scripts can be migrated to `alphafold_core/utils.py` ✅ **COMPLETED**
- JSON processing can be enhanced in `alphafold_core/data/json_processor.py` ✅ **COMPLETED**

## 📊 Data Files Analysis

### **Input Data:**
- **`data/raw/venn2_overlap.tsv`**
  - Gene names from overlap analysis
  - TSV format with gene identifiers
  - Requires UniProt querying for protein accessions

### **Processed Data:**
- **`alphafold_output/json_split/gene_to_protein_corrected_20250620_103808/gene_to_protein_corrected.csv`**
  - Gene query results with protein accessions
  - Comprehensive metadata for each protein

- **`alphafold_output/json_split/gene_to_protein_corrected_20250620_103808/gene_to_protein_corrected.fasta`**
  - Protein sequences in FASTA format
  - Ready for sequence analysis

- **`alphafold_output/json_split/gene_to_protein_corrected_20250620_103808/gene_to_protein_corrected_alphafold.json`**
  - Master JSON file (2.0MB)
  - Complete protein interaction specifications

### **Batch Files:**
- **`alphafold_output/json_split/gene_to_protein_corrected_20250620_103808/batches/`**
  - Multiple batch JSON files (30 jobs per batch)
  - Ready for AlphaFold3 server submission

### **Future Results:**
- **`alphafold_output/predictions/`** - AlphaFold3 prediction results (pending)
- **`results/summaries/`** - Summary statistics (planned)
- **`results/visualizations/`** - Plots and charts (planned)

## 🎯 Key Insights

### **Project Evolution:**
1. **Started with:** Scattered demo files and scripts
2. **Evolved to:** Organized hierarchical structure using alphafold_core
3. **Current State:** Data preparation and JSON organization complete
4. **Next Phase:** AlphaFold3 processing and result analysis

### **Learning Outcomes:**
- ✅ **Hierarchical Structure:** Benefits of organized workflow management
- ✅ **Timestamped Outputs:** Automatic organization with timestamps
- ✅ **Batch Processing:** Efficient handling of large datasets
- ✅ **Quality Control:** Comprehensive validation and error handling
- ✅ **Modular Design:** Reusable components and clear separation of concerns

### **Unique Challenges Solved:**
- ✅ **Demo File Cleanup:** Transition from scattered demo files to organized structure
- ✅ **Batch Organization:** Efficient splitting for AlphaFold3 daily limits
- ✅ **Workflow Management:** Comprehensive task execution and progress tracking
- ✅ **Quality Validation:** Structure testing and format validation
- ✅ **Future Planning:** Prepared structure for upcoming analysis phases

### **Areas for Improvement:**
- ❌ **Demo File Cleanup:** Remove scattered demo files
- ❌ **Configuration Management:** Centralize configuration files
- ❌ **Documentation Updates:** Keep documentation current with project progress
- ❌ **Result Analysis Preparation:** Prepare analysis scripts for future phases

## 🚀 Migration to New System

### **What Has Been Migrated:**
1. **Organized Workflow Management:** ✅ **Already migrated** to `OrganizedWorkflowManager`
2. **Gene-to-Protein Processing:** ✅ **Already migrated** to `GeneToProteinPipeline`
3. **JSON Processing:** ✅ **Already migrated** to `JSONProcessor`
4. **Batch Splitting:** ✅ **Already migrated** to integrated batch processing
5. **Structure Testing:** ✅ **Recently added** to `alphafold_core/utils.py`

### **What Can Be Enhanced:**
1. **Configuration Management:** Add project-specific configuration files
2. **Analysis Preparation:** Prepare analysis scripts for future phases
3. **Result Processing:** Enhance result analysis capabilities
4. **Visualization Tools:** Add plotting and charting capabilities

### **Enhanced Capabilities for alphafold_core:**

1. **Project Configuration:**
   ```python
   # Add to alphafold_core/config.py
   class ProjectConfig:
       def __init__(self, project_name):
           self.project_name = project_name
           self.base_output_dir = f"alphafold_output/{project_name}"
           self.batch_size = 30
   ```

2. **Result Analysis Preparation:**
   ```python
   # Add to alphafold_core/analysis/quality.py
   class AlphaFoldResultAnalyzer:
       def analyze_predictions(self, prediction_dir):
           # Implement prediction analysis
           pass
   ```

3. **Visualization Tools:**
   ```python
   # Add to alphafold_core/visualization/plots.py
   def create_prediction_summary_plots(results_data):
       # Implement summary visualization
       pass
   ```

### **Benefits of Migration:**
- ✅ **Organized Structure:** Clear project organization with timestamps
- ✅ **Reusable Components:** Modular design for future projects
- ✅ **Quality Control:** Comprehensive validation and error handling
- ✅ **Scalable Processing:** Efficient batch processing for large datasets
- ✅ **Future-Ready:** Prepared structure for upcoming analysis phases

## 📖 Documentation Status

### ✅ **Completed:**
- `run_organized_gene_to_protein.py` - Main workflow script
- `split_corrected_json.py` - JSON splitting utility
- `run_gene_to_protein_task.py` - Task execution script
- `regenerate_batches.py` - Batch regeneration utility
- `modify_json.py` - JSON modification utility
- `test_structure.py` - Structure testing utility
- `DICER_685_PROJECT_DOCUMENTATION.md` - This comprehensive documentation

### 🔄 **To Document:**
- AlphaFold3 processing scripts (when implemented)
- Result analysis scripts (when implemented)
- Visualization and reporting scripts (when implemented)

### 📋 **Future Documentation:**
- Phase 3: AlphaFold3 processing workflow
- Phase 4: Result analysis and summary statistics
- Final project report and conclusions

## 🎯 Next Steps

### **Immediate Actions:**
1. **Clean up demo files** - Remove scattered demo files
2. **Prepare AlphaFold3 submission** - Ready batch files for server submission
3. **Set up monitoring** - Prepare for tracking prediction progress

### **Upcoming Phases:**
1. **Phase 3: AlphaFold3 Processing** - Submit batches and monitor progress
2. **Phase 4: Result Analysis** - Analyze predictions and generate statistics
3. **Final Documentation** - Complete project documentation with results

### **Long-term Planning:**
1. **Analysis Scripts** - Prepare analysis scripts for prediction results
2. **Visualization Tools** - Implement plotting and charting capabilities
3. **Report Generation** - Create comprehensive final reports

---

**Project Timeline:** Ongoing  
**Status:** 🔄 **In Progress - Phases 1-2 Complete**  
**Migration Status:** ✅ **Fully migrated to new system**  
**Unique Contributions:** Organized workflow management, batch processing, future-ready structure 