# AlphaFold Project - Master Documentation

## 🎯 Project Overview
A comprehensive, hierarchical bioinformatics framework for AlphaFold-related tasks. Built with modularity, reusability, and maintainability in mind.

## 📁 Project Structure

```
AlphaFold/
├── alphafold_core/           # 🏗️ Core hierarchical system
│   ├── config.py            # Configuration management
│   ├── utils.py             # Shared utilities
│   ├── data/                # Data processing modules
│   ├── analysis/            # Analysis tools
│   ├── visualization/       # Plotting and reporting
│   └── pipeline/            # Workflow orchestration
├── examples/                # 📚 Documented usage examples
│   ├── gene_to_protein_demo.py    # ✅ DOCUMENTED
│   ├── rnh1_project_migration_examples.py  # ✅ CREATED
│   └── basic_usage.py             # 🔄 TO DOCUMENT
├── Project/                 # 📚 Active research projects
│   ├── RNH1_Q40740_Collab_Project/    # ✅ COMPLETED - First AlphaFold project
│   ├── Dicer_685_Project/             # 🔄 ONGOING - Current project
│   └── Triple_Overlap_DNA_RNA_Project/ # ✅ COMPLETED - Overlap analysis
├── Project_Documentation/   # 📖 Project-specific documentation
├── alphafold_output/        # 📊 Organized workflow outputs
└── Documentation/           # 📖 Project documentation
```

## 🏗️ Core System: `alphafold_core/`

### **Configuration (`config.py`)**
- Centralized configuration management
- API endpoints, timeouts, retry strategies
- Environment-specific settings

### **Data Processing (`data/`)**
- **`fetcher.py`** - UniProt API integration with rate limiting
- **`processor.py`** - Multi-format data processing (CSV, FASTA, JSON)
- **`json_processor.py`** - JSON file splitting and validation
- **`loader.py`** - Data loading utilities
- **`validator.py`** - Data validation tools

### **Analysis (`analysis/`)**
- **`comparison.py`** - Protein comparison tools
- **`overlap.py`** - Overlap analysis
- **`quality.py`** - Quality assessment
- **`statistics.py`** - Statistical analysis

### **Visualization (`visualization/`)**
- **`plots.py`** - Plotting utilities
- **`reports.py`** - Report generation

### **Pipelines (`pipeline/`)**
- **`workflows.py`** - Core workflow classes
- **`organized_workflows.py`** - Organized output management

## 📚 Documented Solutions

### ✅ **1. Gene-to-Protein Workflow**
**File:** `examples/gene_to_protein_demo.py`
**Documentation:** `GENE_TO_PROTEIN_DEMO_DOCUMENTATION.md`

**What it does:**
- Converts TSV files with gene names to protein data
- Queries UniProt API for protein sequences
- Generates multiple output formats (CSV, FASTA, JSON)
- Handles batch processing and organized outputs

**Key Features:**
- ✅ Comprehensive error handling
- ✅ Rate limiting for API calls
- ✅ Multiple output formats
- ✅ Batch processing capabilities
- ✅ Organized output directories

**Usage:**
```bash
python examples/gene_to_protein_demo.py
```

### ✅ **2. RNH1_Q40740_Collab_Project**
**Location:** `RNH1_Q40740_Collab_Project/`
**Documentation:** `RNH1_Q40740_COLLAB_PROJECT_DOCUMENTATION.md`

**What it does:**
- **First AlphaFold project** from last semester
- Analyzes protein interactions with RNH1 (Q40740)
- Uses AlphaPulldown and AlphaFold3 workflows
- Demonstrates evolution from scattered scripts to organized approach

**Key Components:**
- ✅ **Sequence Extraction:** `src/notebooks/SequenceExtract.ipynb` (DOCUMENTED)
- ✅ **Downstream Analysis:** `src/notebooks/Downsteam_analysis.ipynb` (DOCUMENTED)
- ✅ **Result Processing:** `src/scripts/AF3_Result_Table.py` (DOCUMENTED)
- 🔄 **Enhanced Results:** `src/scripts/AF3_Result_Tables.py` (TO DOCUMENT)
- 🔄 **Overlap Analysis:** `src/scripts/analyze_overlap.py` (TO DOCUMENT)

**Migration Status:**
- ✅ **Sequence Extraction:** Migrated to `ProteinSequenceFetcher`
- ✅ **JSON Generation:** Migrated to `DataProcessor`
- ✅ **Result Analysis:** Migrated to `QualityAnalyzer`
- ✅ **Downstream Analysis:** Migrated to `OverlapAnalyzer`
- 🔄 **Visualization:** Can be migrated to `alphafold_core/visualization/`

### ✅ **3. Migration Examples**
**File:** `examples/rnh1_project_migration_examples.py`
**Status:** ✅ **CREATED**

**What it demonstrates:**
- **Example 1:** Sequence extraction migration (50+ lines → 5 lines)
- **Example 2:** JSON generation migration (Manual → Automatic)
- **Example 3:** Result analysis migration (Scattered → Organized)
- **Example 4:** Overlap analysis migration (One-off → Reusable)
- **Example 5:** Complete workflow migration (Multiple scripts → Single command)

**Benefits Demonstrated:**
- ✅ **Code Reduction:** 80% less code
- ✅ **Error Handling:** Manual → Automatic
- ✅ **Reusability:** One-off → Reusable components
- ✅ **Maintainability:** Scattered → Organized
- ✅ **Testing:** Difficult → Easy

### 🔄 **4. Basic Usage Examples** (TO DOCUMENT)
**File:** `examples/basic_usage.py`

**What it does:**
- Demonstrates core functionality usage
- Shows individual component usage
- Provides migration examples from old scripts

### 🔄 **5. Organized Workflows** (TO DOCUMENT)
**File:** `run_organized_gene_to_protein.py`

**What it does:**
- High-level workflow orchestration
- Organized output management
- Batch processing with structured outputs

## 🗑️ Cleanup Summary

### **Deleted Redundant Scripts:**
- ❌ `Senior Last Semester/src/scripts/fetch_protein_sequences.py`
- ❌ `Summer Project/src/26 Overlapped Analysis/create_protein_json.py`
- ❌ `Summer Project/src/26 Overlapped Analysis/create_protein_json_without_msa.py`
- ❌ `create_protein_interaction_json.py`

### **Deleted from RNH1 Project:**
- ❌ `RNH1_Q40740_Collab_Project/src/scripts/AlphaFold3_JSON_generator.py`
- ❌ `RNH1_Q40740_Collab_Project/src/scripts/JSON_generator.py`
- ❌ `RNH1_Q40740_Collab_Project/src/scripts/combine_json_files.py`
- ❌ `RNH1_Q40740_Collab_Project/src/scripts/split_protein_ids.py`

### **Replaced by:**
- ✅ `alphafold_core/data/fetcher.py` - `ProteinSequenceFetcher`
- ✅ `alphafold_core/data/processor.py` - `DataProcessor`
- ✅ `alphafold_core/pipeline/organized_workflows.py` - `OrganizedWorkflowManager`

## 🚀 Getting Started

### **Quick Start:**
```bash
# 1. Clone the repository
cd /Users/conny/Desktop/AlphaFold

# 2. Run the gene-to-protein demo
python examples/gene_to_protein_demo.py

# 3. Check organized outputs
ls alphafold_output/

# 4. View migration examples
python examples/rnh1_project_migration_examples.py
```

### **Core Workflows:**

#### **Gene-to-Protein Processing:**
```python
from alphafold_core.pipeline import GeneToProteinPipeline

pipeline = GeneToProteinPipeline()
results = pipeline.run_gene_to_protein_workflow(
    tsv_file="data/genes.tsv",
    gene_column="GENE",
    output_prefix="my_workflow"
)
```

#### **Organized Workflows:**
```python
from alphafold_core.pipeline import OrganizedWorkflowManager

workflow_manager = OrganizedWorkflowManager()
results = workflow_manager.run_gene_to_protein_workflow(
    input_file="data/genes.tsv",
    output_prefix="organized_workflow"
)
```

## 📊 Output Organization

### **Standard Outputs:**
- `{prefix}.csv` - Gene-to-protein mapping
- `{prefix}.fasta` - Protein sequences
- `{prefix}_alphafold.json` - AlphaFold3 job specifications
- `{prefix}_summary.json` - Processing statistics

### **Organized Outputs:**
```
alphafold_output/
└── gene_to_protein/
    └── {task_name}_{timestamp}/
        ├── raw/           # Original outputs
        ├── processed/     # Processed data
        ├── batches/       # Split JSON files
        ├── logs/          # Processing logs
        └── {task_name}_summary.json
```

## 🔧 Configuration

### **API Settings:**
```python
from alphafold_core.config import config

# UniProt API settings
config.uniprot_base_url = "https://rest.uniprot.org/uniprotkb"
config.max_retries = 3
config.request_timeout = 30
```

### **Rate Limiting:**
- Built-in rate limiting for UniProt API
- Automatic retry with exponential backoff
- Respects API rate limits

## 📈 Benefits of the New System

### **Before (Scattered Scripts):**
- ❌ 50+ individual scripts
- ❌ Hard-coded paths
- ❌ No error handling
- ❌ Difficult to maintain
- ❌ Not reusable

### **After (Hierarchical System):**
- ✅ 1 core system with 5 modules
- ✅ Configuration management
- ✅ Comprehensive error handling
- ✅ Highly maintainable
- ✅ Fully reusable
- ✅ Organized outputs
- ✅ Batch processing

## 📖 Documentation Status

### ✅ **Completed:**
- `GENE_TO_PROTEIN_DEMO_DOCUMENTATION.md` - Comprehensive demo documentation
- `RNH1_Q40740_COLLAB_PROJECT_DOCUMENTATION.md` - First project documentation
- `LEGACY_SCRIPTS_MIGRATION.md` - Migration guide for old scripts
- `MASTER_DOCUMENTATION.md` - This master index

### 🔄 **To Document:**
- `examples/basic_usage.py` - Core usage examples
- `run_organized_gene_to_protein.py` - Organized workflows
- `RNH1_Q40740_Collab_Project/src/notebooks/ridof_repeat.ipynb` - Data cleaning workflow
- `RNH1_Q40740_Collab_Project/src/scripts/AF3_Result_Tables.py` - Enhanced result processing
- `RNH1_Q40740_Collab_Project/src/scripts/analyze_overlap.py` - Overlap analysis
- `alphafold_core/` modules - Individual module documentation

## 🎯 Next Steps

1. **Document `examples/basic_usage.py`** - Core usage patterns
2. **Document `run_organized_gene_to_protein.py`** - Organized workflows
3. **Document remaining RNH1 project components** - Analysis and data cleaning workflows
4. **Create module documentation** for `alphafold_core/` components
5. **Add unit tests** for core components
6. **Create user guide** for common workflows

## 📞 Support

For questions or issues:
1. Check the specific documentation files
2. Review the migration guide for old functionality
3. Examine the example scripts for usage patterns
4. Refer to the core system documentation

## 🔄 Daily Maintenance Checklist

### **When Wrapping Up Work Each Day:**

**IMPORTANT:** This checklist should be performed by asking the AI assistant to read this section and execute the verification tasks. 

**To perform daily maintenance:**
1. **Ask the AI:** "Please read the daily maintenance checklist in MASTER_DOCUMENTATION.md and perform the verification tasks"
2. **The AI will:** Verify project trees, check for new files, update documentation, and report any issues found
3. **You review:** The AI's findings and approve any changes

#### **1. Project Tree Verification** 🔍
**Purpose:** Ensure all project documentation accurately reflects the current file structure.

**AI Tasks:**
- [ ] **Verify RNH1_Q40740_Collab_Project structure** in `Project_Documentation/RNH1_Q40740_COLLAB_PROJECT_DOCUMENTATION.md`
  - [ ] Check `src/scripts/` directory for new/removed scripts
  - [ ] Check `src/notebooks/` directory for new notebooks
  - [ ] Verify `data/` and `results/` directories match documentation
  - [ ] Update any new files added to the project

- [ ] **Verify Dicer_685_Project structure** in `Project_Documentation/DICER_685_PROJECT_DOCUMENTATION.md`
  - [ ] Check for new scripts in project root or `scripts/` directory
  - [ ] Verify `alphafold_output/` structure matches documentation
  - [ ] Update any new batch files or results
  - [ ] Check for new data files in `data/` directory

- [ ] **Verify Triple_Overlap_DNA_RNA_Project structure** in `Project_Documentation/TRIPLE_OVERLAP_DNA_RNA_PROJECT_DOCUMENTATION.md`
  - [ ] Check `src/P1/`, `src/P2/`, `src/P3/` directories for new files
  - [ ] Verify `src/Aggregate/` and `src/26 Overlapped Analysis/` contents
  - [ ] Update any new analysis results or processed files

#### **2. New Script Documentation** 📝
**Purpose:** Document any new scripts or notebooks created during the day.

**AI Tasks:**
- [ ] **Identify new scripts** in any project directory
- [ ] **Document new scripts** with:
  - [ ] Purpose and functionality
  - [ ] Input/output specifications
  - [ ] Key features and capabilities
  - [ ] Usage examples
  - [ ] Dependencies and requirements
- [ ] **Update project documentation** to include new scripts
- [ ] **Add to master documentation** if it's a reusable component

#### **3. alphafold_core Updates** 🏗️
**Purpose:** Track any changes to the core system.

**AI Tasks:**
- [ ] **Check for new modules** in `alphafold_core/`
- [ ] **Verify existing modules** haven't been modified
- [ ] **Update module documentation** if changes were made
- [ ] **Test core functionality** to ensure nothing is broken
- [ ] **Update examples** if core API has changed

#### **4. Output Organization** 📊
**Purpose:** Ensure all outputs are properly organized and documented.

**AI Tasks:**
- [ ] **Check `alphafold_output/`** for new workflow outputs
- [ ] **Verify organized workflow outputs** have proper timestamps
- [ ] **Document any new output formats** or structures
- [ ] **Clean up temporary files** in project directories
- [ ] **Update output documentation** if new patterns emerge

#### **5. Migration Status Updates** 🔄
**Purpose:** Track progress on migrating old scripts to the new system.

**AI Tasks:**
- [ ] **Identify any new legacy scripts** that could be migrated
- [ ] **Update migration examples** if new patterns are discovered
- [ ] **Document migration benefits** for new scripts
- [ ] **Update migration status** in project documentation

#### **6. Documentation Synchronization** 📖
**Purpose:** Ensure all documentation is consistent and up-to-date.

**AI Tasks:**
- [ ] **Update master documentation** with any new projects or components
- [ ] **Verify cross-references** between documentation files
- [ ] **Check for broken links** or outdated references
- [ ] **Update "Last Updated" timestamps** for modified files
- [ ] **Review documentation completeness** for new components

#### **7. Code Quality Checks** ✅
**Purpose:** Maintain code quality and consistency.

**AI Tasks:**
- [ ] **Check for syntax errors** in new scripts
- [ ] **Verify import statements** are correct
- [ ] **Test basic functionality** of new scripts
- [ ] **Check for hard-coded paths** that should be configurable
- [ ] **Verify error handling** is appropriate

#### **8. Project Status Updates** 📈
**Purpose:** Track overall project progress and status.

**AI Tasks:**
- [ ] **Update project status** (✅ COMPLETED, 🔄 ONGOING, 📋 PLANNED)
- [ ] **Document any blockers** or issues encountered
- [ ] **Update next steps** based on daily progress
- [ ] **Note any dependencies** or waiting items

### **Quick Commands for AI Reference** 🤖

**When the AI performs verification, it can use these commands:**

```bash
# Check project structures
ls -la Project/RNH1_Q40740_Collab_Project/src/scripts/
ls -la Project/RNH1_Q40740_Collab_Project/src/notebooks/
ls -la Project/Dicer_685_Project/
ls -la Project/Triple_Overlap_DNA_RNA_Project/src/

# Find new files created today
find Project/ -type f -mtime -1 -name "*.py" -o -name "*.ipynb" -o -name "*.md"

# Check for new directories created today
find Project/ -type d -mtime -1
```

### **Documentation Update Template** 📋

**When the AI documents new components, it should use this template:**

```markdown
### ✅ **X. [Component Name]**
**File:** `path/to/component.py`
**Status:** ✅ **NEWLY DOCUMENTED**

**What it does:**
- Brief description of functionality
- Key features and capabilities
- Input/output specifications

**Key Features:**
- ✅ Feature 1
- ✅ Feature 2
- ✅ Feature 3

**Usage:**
```python
# Example usage code
```

**Replaced by:** (if applicable)
- ✅ **`alphafold_core/module/component.py`** - `ComponentName`
```

### **Priority Levels** 🎯

- **🔴 HIGH PRIORITY:** Project tree verification, new script documentation
- **🟡 MEDIUM PRIORITY:** Output organization, documentation synchronization
- **🟢 LOW PRIORITY:** Code quality checks, migration status updates

### **Weekly Maintenance** 📅

**Every Friday, the AI should also check:**
- [ ] **Archive completed projects** to separate documentation
- [ ] **Review overall system architecture** for improvements
- [ ] **Update master documentation** with any architectural changes
- [ ] **Plan next week's priorities** based on current status

### **How to Request Daily Maintenance** 📞

**Simply ask the AI:**
> "Please read the daily maintenance checklist in MASTER_DOCUMENTATION.md and perform the verification tasks for today."

**The AI will then:**
1. Read this section
2. Perform all verification tasks
3. Update documentation as needed
4. Report findings and any issues
5. Ask for approval before making changes

**Note:** The scripts (`migration_helper.py` and `daily_verification.sh`) are kept for quick reference but are not used for actual maintenance tasks.

---

**Last Updated:** December 2024  
**Project Status:** ✅ Core system complete, documentation in progress  
**Maintenance Status:** ✅ Daily checklist implemented 