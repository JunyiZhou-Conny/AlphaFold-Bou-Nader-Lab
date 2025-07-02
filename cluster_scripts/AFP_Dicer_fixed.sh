#!/bin/bash

# Configuration - adjust these paths for your cluster setup
MONOMER_OBJECTS_DIR="/data7/Conny/Projects/Dicer_685/JackFeatureDB_Pickle"
BAIT_FILE="/data7/Conny/Projects/Dicer_685/bait_protein.txt"
DATA_DIR="/data7/Conny/data/AF_GeneticDB/"
BASE_OUTPUT="/data7/Conny/Projects/Dicer_685/AFP_Dicer_Output"
RUN_SCRIPT="/programs/x86_64-linux/alphapulldown/2.0.1/miniconda/bin/run_multimer_jobs.py"

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

# Check if all required files exist
echo "Checking required files..."
for file in "${TARGET_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "ERROR: Target file not found: $file"
        exit 1
    fi
done

if [[ ! -f "$BAIT_FILE" ]]; then
    echo "ERROR: Bait file not found: $BAIT_FILE"
    exit 1
fi

if [[ ! -d "$MONOMER_OBJECTS_DIR" ]]; then
    echo "ERROR: Monomer objects directory not found: $MONOMER_OBJECTS_DIR"
    exit 1
fi

if [[ ! -d "$DATA_DIR" ]]; then
    echo "ERROR: Data directory not found: $DATA_DIR"
    exit 1
fi

if [[ ! -f "$RUN_SCRIPT" ]]; then
    echo "ERROR: Run script not found: $RUN_SCRIPT"
    exit 1
fi

echo "All required files found. Starting parallel jobs..."

# Run jobs on 8 GPUs in parallel
for i in ${!TARGET_FILES[@]}; do
    echo "Starting job on GPU $i with target file: ${TARGET_FILES[$i]}"
    
    # Create output directory for this GPU
    mkdir -p "$BASE_OUTPUT/gpu_$i"
    
    # Run AlphaPulldown with bait and target as separate protein lists
    # Format: --protein_lists=<bait_file>,<target_file>
    CUDA_VISIBLE_DEVICES=$i "$RUN_SCRIPT" \
        --mode=pulldown \
        --monomer_objects_dir="$MONOMER_OBJECTS_DIR" \
        --protein_lists="$BAIT_FILE,${TARGET_FILES[$i]}" \
        --output_path="$BASE_OUTPUT/gpu_$i" \
        --data_dir="$DATA_DIR" \
        --num_cycle=3 \
        --num_predictions_per_model=1 \
        > "$BASE_OUTPUT/gpu_$i/run.log" 2>&1 &
    
    echo "Job started on GPU $i (PID: $!)"
done

echo "All jobs submitted. Waiting for completion..."
wait

echo "All jobs completed!"

# Optional: Generate a summary report
echo "Generating summary report..."
echo "=== Job Summary ===" > "$BASE_OUTPUT/job_summary.txt"
echo "Completed at: $(date)" >> "$BASE_OUTPUT/job_summary.txt"
echo "" >> "$BASE_OUTPUT/job_summary.txt"

for i in {0..7}; do
    if [[ -f "$BASE_OUTPUT/gpu_$i/run.log" ]]; then
        echo "GPU $i log file: $BASE_OUTPUT/gpu_$i/run.log" >> "$BASE_OUTPUT/job_summary.txt"
        echo "Target file: ${TARGET_FILES[$i]}" >> "$BASE_OUTPUT/job_summary.txt"
        echo "---" >> "$BASE_OUTPUT/job_summary.txt"
    fi
done

echo "Summary report saved to: $BASE_OUTPUT/job_summary.txt" 