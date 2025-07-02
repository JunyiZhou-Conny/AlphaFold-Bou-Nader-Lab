# Research Log for Charles

## ToDo:

1. Check `missing_proteins.txt` for Feature Database
2. Investigate MMseqs2 issues

## Major Reference Links

- **UniProt:**
  Protein sequences: https://www.uniprot.org
  REST access: https://www.uniprot.org/uniprotkb/Q04740/entry
- **AlphaPullDown:**
  Paper: https://academic.oup.com/bioinformatics/article/39/1/btac749/6839971
  GitHub: https://github.com/KosinskiLab/AlphaPulldown
- **AF2-multimer:**
  Tutorial: https://sbgrid.org//wiki/examples/alphafold2
  GitHub: https://github.com/google-deepmind/alphafold#readme
- **AF3:**
  Server: https://alphafoldserver.com/welcome
  GitHub: https://github.com/google-deepmind/alphafold3

## Common Tools and Command Lines

```
# Local to cloud
scp /Users/conny/Desktop/AlphaFold/test_sequence.fasta jzho349@kilimanjaro.biochem.emory.edu:/data7/Conny/data

# Cloud to local
scp -r jzho349@kilimanjaro.biochem.emory.edu:/data7/Conny/result_mmseqs2/pulldown_results/gpu_0/run.log ~/Downloads/

# Split protein sequences into 8 chunks
split -n l/8 --suffix-length=2 --additional-suffix=.txt unique_protein_ids_Jack.txt target_chunk_Jack_

# Move folder files into a single folder
mkdir -p gpu_all
cp gpu_{0..7}/* gpu_all/

```

## Expected Output from AF3

1. `mmCIF`: predicted 3D structure of the protein complex
2. `pLDDT`: per-residue confidence score

## AlphaPulldown Big Picture – Two Steps

1. `create_individual_features.py`: generates MSA + template search and produces `.pkl` files
2. `run_multimer_jobs.py`: structure prediction using the `.pkl` files

## Basic Setup

```
# Create conda environment
conda create -n AlphaPulldown -c omnia -c bioconda -c conda-forge \
  python==3.11 openmm==8.0 pdbfixer==1.9 kalign2 hhsuite hmmer modelcif

# Activate and install JAX
conda activate AlphaPulldown
pip install -U "jax[cuda12]"
```

## Feature Generation Methods

### MMseqs2 (no parallelism yet)

```
NUM_SEQ=$(grep -c "^>" protein_sequences.fasta)
export FASTA_PATH="/data7/Conny/data/protein_sequences.fasta"
export DATA_DIR="/data7/Conny/data/AF_GeneticDB"
export OUTPUT_DIR="/data7/Conny/result_mmseqs2"
export MAX_TEMPLATE_DATE="2025-03-25"

for ((i=0; i<$NUM_SEQ; i++)); do
  echo "Processing sequence index $i"
  create_individual_features.py \
    --fasta_paths="$FASTA_PATH" \
    --data_dir="$DATA_DIR" \
    --output_dir="$OUTPUT_DIR" \
    --skip_existing=True \
    --use_mmseqs2=True \
    --max_template_date="2050-01-01" \
    --seq_index=$i || {
    echo "[WARN] Failed to process sequence $i"
    echo $i >> failed_indexes.txt
  }
done
```

### JackHMMer (with parallelism)

```
NUM_SEQ=$(grep -c "^>" /data7/Conny/data/protein_sequences.fasta)
export FASTA_PATH="/data7/Conny/data/protein_sequences.fasta"
export DATA_DIR="/data7/Conny/data/AF_GeneticDB"
export OUTPUT_DIR="/data7/Conny/result_JackHMMer"
export MAX_TEMPLATE_DATE="2025-03-29"
FAILED_LOG="/data7/Conny/result_JackHMMer/failed_indexes_JackHMMer.txt"
MAX_JOBS=16

rm -f "$FAILED_LOG"

for ((i=0; i<$NUM_SEQ; i++)); do
  (
    echo "Processing sequence index $i"
    create_individual_features.py \
      --fasta_paths="$FASTA_PATH" \
      --data_dir="$DATA_DIR" \
      --output_dir="$OUTPUT_DIR" \
      --skip_existing=True \
      --use_mmseqs2=False \
      --max_template_date="2050-01-01" \
      --seq_index=$i || {
      echo "[WARN] Failed to process sequence $i"
      echo $i >> "$FAILED_LOG"
    }
  ) &
  while (( $(jobs -r | wc -l) >= MAX_JOBS )); do sleep 1; done

done
wait
echo "[INFO] All sequence jobs complete."
```

## Understanding `create_individual_features.py`

- Runs entirely on CPU
- Outputs `.pkl` files
- Requires **Genetic Database**: `/data7/Conny/data/AF_GeneticDB`
- Supports 3 methods:
  - JackHMMer / HHblits
  - MMseqs2
  - Pickle file download from AlphaPulldown

Genetic DB install:

```
# Run full download script (takes ~19 hrs)
bash download_all_data.sh /data7/Conny/data/AF_GeneticDB
```

Feature DB install:

```
# Download mc client
curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
mkdir -p $HOME/bin
mv mc $HOME/bin/
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Download example pickle
mc cp embl/alphapulldown/input_features/Saccharomyces_cerevisiae/Q01329.pkl.xz /data7/Conny/data/JackFeaturePickleDB

# Decompress all
xz -dk *.xz
```

## Multimer Prediction

Use `run_multimer_jobs.py` in pulldown mode:

```
source ~/.bashrc
conda activate AlphaPulldown

export MONOMER_OBJECTS_DIR="/data7/Conny/result_mmseqs2/"
export BAIT_FILE="/data7/Conny/data/bait_list.txt"
export DATA_DIR="/data7/Conny/data/AF_GeneticDB/"
export NUM_CYCLE=3
export NUM_PREDICTIONS_PER_MODEL=1
export BASE_OUTPUT="/data7/Conny/result_mmseqs2/pulldown_results"

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

for i in "${!TARGET_FILES[@]}"; do
  TARGET_FILE="${TARGET_FILES[$i]}"
  GPU_ID=$i
  OUTPUT_DIR="$BASE_OUTPUT/gpu_$i"
  LOG_FILE="$OUTPUT_DIR/run.log"
  mkdir -p "$OUTPUT_DIR"

  echo "[GPU $GPU_ID] Running bait + $(basename "$TARGET_FILE")"
  CUDA_VISIBLE_DEVICES=$GPU_ID run_multimer_jobs.py \
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
```

## [TO BE CONTINUED: Result Analysis Cleanup in Next Update] ✅