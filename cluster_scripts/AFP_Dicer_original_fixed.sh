#!/bin/bash

# === Activate env ===
source ~/.bashrc
conda activate AlphaPulldown

# === Set Variables ===
export MONOMER_OBJECTS_DIR="/data7/Conny/result_mmseqs2/"  
export BAIT_FILE="/data7/Conny/data/bait_list.txt"
export DATA_DIR="/data7/Conny/data/AF_GeneticDB/"
export NUM_CYCLE=3
export NUM_PREDICTIONS_PER_MODEL=1
export BASE_OUTPUT="/data7/Conny/result_mmseqs2/pulldown_results"

# === Set the correct Python path for the conda environment ===
export PYTHON_PATH=$(which python)
export RUN_SCRIPT_PATH=$(which run_multimer_jobs.py)

# === List of absolute target chunk files ===
TARGET_FILES=(
  "/data7/Conny/data/target_chunk_aa"
  "/data7/Conny/data/target_chunk_ab"
  "/data7/Conny/data/target_chunk_ac"
  "/data7/Conny/data/target_chunk_ad"
  "/data7/Conny/data/target_chunk_ae"
  "/data7/Conny/data/target_chunk_af"
  "/data7/Conny/data/target_chunk_ag"
  "/data7/Conny/data/target_chunk_ah"
)

# === Check if environment is properly activated ===
echo "Using Python: $PYTHON_PATH"
echo "Using script: $RUN_SCRIPT_PATH"
echo "Conda env: $CONDA_DEFAULT_ENV"

# === Run parallel jobs ===
for i in "${!TARGET_FILES[@]}"; do
  TARGET_FILE="${TARGET_FILES[$i]}"
  GPU_ID=$i
  OUTPUT_DIR="$BASE_OUTPUT/gpu_$i"
  LOG_FILE="$OUTPUT_DIR/run.log"
  mkdir -p "$OUTPUT_DIR"

  echo "[GPU $GPU_ID] Running bait + $(basename "$TARGET_FILE")"

  # Use explicit Python interpreter and full path to script
  CUDA_VISIBLE_DEVICES=$GPU_ID "$PYTHON_PATH" "$RUN_SCRIPT_PATH" \
    --mode=pulldown \
    --monomer_objects_dir="$MONOMER_OBJECTS_DIR" \
    --protein_lists="$(realpath "$BAIT_FILE"),$TARGET_FILE" \
    --output_path="$OUTPUT_DIR" \
    --data_dir="$DATA_DIR" \
    --num_cycle="$NUM_CYCLE" \
    --num_predictions_per_model="$NUM_PREDICTIONS_PER_MODEL" \
    > "$LOG_FILE" 2>&1 &

done

wait
echo "✅ All jobs running across 8 GPUs. Use 'watch -n 1 nvidia-smi' to monitor usage." 