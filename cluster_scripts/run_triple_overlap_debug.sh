#!/bin/bash
#SBATCH --job-name=triple_overlap_debug
#SBATCH --output=triple_overlap_debug_%j.out
#SBATCH --error=triple_overlap_debug_%j.err
#SBATCH --time=00:30:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=2
#SBATCH --partition=compute

# Load any necessary modules
module load python/3.9

# Set up environment
export PYTHONPATH="/data7/Conny/scripts:$PYTHONPATH"

# Create output directory
mkdir -p /data7/Conny/Projects/Triple_Overlap_RLoop/results

# Run the debug script
echo "Starting Triple Overlap R-Loop debug..."
python /data7/Conny/scripts/cluster_scripts/debug_triple_overlap.py

echo "Debug completed!" 