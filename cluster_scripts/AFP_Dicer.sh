#!/bin/bash

# Configuration - adjust these paths for your cluster setup
MONOMER_OBJECTS_DIR="/data7/Conny/Projects/Dicer_685/JackFeatureDB_Pickle"
BAIT_FILE="/data7/Conny/Projects/Dicer_685/bait_protein.txt"
DATA_DIR="/data7/Conny/data/AF_GeneticDB/"
BASE_OUTPUT="/data7/Conny/Projects/Dicer_685/AFP_Dicer_Output"
RUN_SCRIPT="/programs/x86_64-linux/alphapulldown/2.0.1/miniconda/bin/run_multimer_jobs.py"
CONDA_PYTHON="/programs/x86_64-linux/alphapulldown/2.0.1/miniconda/bin/python"

# Create a wrapper script to ensure subprocesses use the right Python
cat > /tmp/python_wrapper.sh << 'EOF'
#!/bin/bash
source /programs/x86_64-linux/alphapulldown/2.0.1/miniconda/etc/profile.d/conda.sh
conda activate alphapulldown
exec /programs/x86_64-linux/alphapulldown/2.0.1/miniconda/bin/python "$@"
EOF
chmod +x /tmp/python_wrapper.sh

# Activate the conda environment
source /programs/x86_64-linux/alphapulldown/2.0.1/miniconda/etc/profile.d/conda.sh
conda activate alphapulldown

# Set environment variables to ensure subprocesses use the right Python
export PATH="/programs/x86_64-linux/alphapulldown/2.0.1/miniconda/bin:$PATH"
export CONDA_DEFAULT_ENV="alphapulldown"
export CONDA_PREFIX="/programs/x86_64-linux/alphapulldown/2.0.1/miniconda/envs/alphapulldown"
export PYTHONPATH="/programs/x86_64-linux/alphapulldown/2.0.1/miniconda/lib/python3.10/site-packages:$PYTHONPATH"

# Create output directories
mkdir -p $BASE_OUTPUT/gpu_{0..7}

# Target files array with full paths
TARGET_FILES=(
  /data7/Conny/Projects/Dicer_685/target_chunk_aa.txt
  /data7/Conny/Projects/Dicer_685/target_chunk_ab.txt
  /data7/Conny/Projects/Dicer_685/target_chunk_ac.txt
  /data7/Conny/Projects/Dicer_685/target_chunk_ad.txt
  /data7/Conny/Projects/Dicer_685/target_chunk_ae.txt
  /data7/Conny/Projects/Dicer_685/target_chunk_af.txt
  /data7/Conny/Projects/Dicer_685/target_chunk_ag.txt
  /data7/Conny/Projects/Dicer_685/target_chunk_ah.txt
)

# Check if required files exist
echo "Checking required files..."
if [ ! -f "$RUN_SCRIPT" ]; then
    echo "ERROR: Run script not found at $RUN_SCRIPT"
    exit 1
fi

if [ ! -f "$BAIT_FILE" ]; then
    echo "ERROR: Bait file not found at $BAIT_FILE"
    exit 1
fi

for target_file in "${TARGET_FILES[@]}"; do
    if [ ! -f "$target_file" ]; then
        echo "ERROR: Target file not found: $target_file"
        exit 1
    fi
done

# Function to check if protein pickle files exist
check_protein_files() {
    local protein_list_file=$1
    local missing_proteins=()
    
    while IFS= read -r protein; do
        if [ -n "$protein" ] && [ "$protein" != "Not Found" ]; then
            if [ ! -f "$MONOMER_OBJECTS_DIR/${protein}.pkl" ]; then
                missing_proteins+=("$protein")
            fi
        fi
    done < "$protein_list_file"
    
    if [ ${#missing_proteins[@]} -gt 0 ]; then
        echo "WARNING: Missing pickle files for proteins: ${missing_proteins[*]}"
        echo "You may need to download these files or check the protein accessions."
        return 1
    fi
    return 0
}

echo "All required files found. Starting parallel jobs..."

# Function to run job on specific GPU
run_job() {
    local gpu_id=$1
    local target_file=$2
    
    echo "Starting job on GPU $gpu_id with target file: $target_file"
    
    # Create temporary combined protein list file
    local temp_protein_list="/tmp/protein_list_gpu_${gpu_id}.txt"
    cat "$BAIT_FILE" "$target_file" > "$temp_protein_list"
    
    # Check for missing protein files
    if ! check_protein_files "$temp_protein_list"; then
        echo "Skipping GPU $gpu_id due to missing protein files"
        rm -f "$temp_protein_list"
        return 1
    fi
    
    # Create a modified environment for this job
    local job_env_file="/tmp/job_env_gpu_${gpu_id}.sh"
    cat > "$job_env_file" << EOF
#!/bin/bash
source /programs/x86_64-linux/alphapulldown/2.0.1/miniconda/etc/profile.d/conda.sh
conda activate alphapulldown
export PATH="/programs/x86_64-linux/alphapulldown/2.0.1/miniconda/bin:\$PATH"
export CONDA_DEFAULT_ENV="alphapulldown"
export CONDA_PREFIX="/programs/x86_64-linux/alphapulldown/2.0.1/miniconda/envs/alphapulldown"
export PYTHONPATH="/programs/x86_64-linux/alphapulldown/2.0.1/miniconda/lib/python3.10/site-packages:\$PYTHONPATH"
EOF
    
    # Run the job with explicit conda Python path and environment
    CUDA_VISIBLE_DEVICES=$gpu_id bash -c "source $job_env_file && $CONDA_PYTHON $RUN_SCRIPT --mode=pulldown --monomer_objects_dir=$MONOMER_OBJECTS_DIR --protein_lists=$temp_protein_list --output_path=$BASE_OUTPUT/gpu_$gpu_id --data_dir=$DATA_DIR --num_cycle=3 --num_predictions_per_model=1" > "$BASE_OUTPUT/gpu_$gpu_id/run.log" 2>&1 &
    
    echo "Job started on GPU $gpu_id (PID: $!)"
    
    # Clean up temporary files
    rm -f "$temp_protein_list" "$job_env_file"
}

# Start jobs on all GPUs
for i in ${!TARGET_FILES[@]}; do
    run_job $i "${TARGET_FILES[$i]}"
done

# Wait for all jobs to complete
echo "All jobs started. Waiting for completion..."
wait

echo "All jobs completed!"
echo "Summary report saved to: $BASE_OUTPUT/job_summary.txt"

# Generate summary
echo "=== Job Summary ===" > "$BASE_OUTPUT/job_summary.txt"
echo "Completed at: $(date)" >> "$BASE_OUTPUT/job_summary.txt"
echo "" >> "$BASE_OUTPUT/job_summary.txt"

for i in {0..7}; do
    if [ -f "$BASE_OUTPUT/gpu_$i/run.log" ]; then
        echo "GPU $i log:" >> "$BASE_OUTPUT/job_summary.txt"
        tail -5 "$BASE_OUTPUT/gpu_$i/run.log" >> "$BASE_OUTPUT/job_summary.txt"
        echo "" >> "$BASE_OUTPUT/job_summary.txt"
    fi
done

# Clean up wrapper script
rm -f /tmp/python_wrapper.sh