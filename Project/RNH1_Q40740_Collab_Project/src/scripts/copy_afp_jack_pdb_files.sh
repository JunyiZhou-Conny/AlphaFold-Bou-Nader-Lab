#!/bin/bash

source_dir="/Users/conny/Desktop/AlphaFold/Project/RNH1_Q40740_Collab_Project/results/ranked_pdbs"
dest_dir="/Users/conny/Desktop/AlphaFold/Project/RNH1_Q40740_Collab_Project/results/Best_Proteins_MMseqs2_Jack"

mkdir -p "$dest_dir"

cp "$source_dir/Q04740_and_P39990_ranked_0.pdb" "$dest_dir/" 2>/dev/null || echo "PDB file not found: Q04740_and_P39990_ranked_0.pdb"
cp "$source_dir/Q04740_and_Q04693_ranked_0.pdb" "$dest_dir/" 2>/dev/null || echo "PDB file not found: Q04740_and_Q04693_ranked_0.pdb"
cp "$source_dir/Q04740_and_Q05473_ranked_0.pdb" "$dest_dir/" 2>/dev/null || echo "PDB file not found: Q04740_and_Q05473_ranked_0.pdb"
cp "$source_dir/Q04740_and_P53336_ranked_0.pdb" "$dest_dir/" 2>/dev/null || echo "PDB file not found: Q04740_and_P53336_ranked_0.pdb"
cp "$source_dir/Q04740_and_P40106_ranked_0.pdb" "$dest_dir/" 2>/dev/null || echo "PDB file not found: Q04740_and_P40106_ranked_0.pdb"
cp "$source_dir/Q04740_and_P53130_ranked_0.pdb" "$dest_dir/" 2>/dev/null || echo "PDB file not found: Q04740_and_P53130_ranked_0.pdb"
cp "$source_dir/Q04740_and_P47064_ranked_0.pdb" "$dest_dir/" 2>/dev/null || echo "PDB file not found: Q04740_and_P47064_ranked_0.pdb"
