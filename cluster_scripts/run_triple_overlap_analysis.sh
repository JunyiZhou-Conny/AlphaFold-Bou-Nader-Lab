#!/bin/bash
#SBATCH --job-name=triple_overlap_analysis
#SBATCH --output=triple_overlap_analysis_%j.out
#SBATCH --error=triple_overlap_analysis_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4
#SBATCH --partition=compute

# Load any necessary modules
module load python/3.9

# Set up environment
export PYTHONPATH="/data7/Conny/scripts:$PYTHONPATH"

# Create output directory
mkdir -p /data7/Conny/Projects/Triple_Overlap_RLoop/results

# Run the analysis
echo "Starting Triple Overlap R-Loop analysis..."
python /data7/Conny/scripts/cluster_scripts/cluster_triple_overlap_analysis.py

echo "Analysis completed!" 