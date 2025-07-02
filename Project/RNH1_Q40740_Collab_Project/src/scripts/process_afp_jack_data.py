import pandas as pd
import os

# Read the filtered AFP_Jack data
afp_jack_data = pd.read_csv('/Users/conny/Desktop/AlphaFold/Project/RNH1_Q40740_Collab_Project/results/AFP_Jack_predictions_with_good_interpae.csv')
afp_jack_filtered = afp_jack_data[(afp_jack_data['iptm_ptm'] >= 0.5) & (afp_jack_data['iptm'] >= 0.6)]

# Extract target names by removing "Q04740_and_" prefix
target_names = afp_jack_filtered['jobs'].str.replace('Q04740_and_', '')

# Save to text file
with open('afp_Jack_target_names.txt', 'w') as f:
    for name in target_names:
        f.write(f"{name}\n")

# Save to Excel
target_df = pd.DataFrame({'Target_Names': target_names})
target_df.to_excel('afp_Jack_target_names.xlsx', index=False)

# Create a script to copy PDB files (optional - only if PDB files exist)
with open('copy_afp_jack_pdb_files.sh', 'w') as f:
    f.write('#!/bin/bash\n\n')
    f.write('source_dir="/Users/conny/Desktop/AlphaFold/Project/RNH1_Q40740_Collab_Project/results/ranked_pdbs"\n')
    f.write('dest_dir="/Users/conny/Desktop/AlphaFold/Project/RNH1_Q40740_Collab_Project/results/Best_Proteins_MMseqs2_Jack"\n\n')
    f.write('mkdir -p "$dest_dir"\n\n')
    
    for name in target_names:
        pdb_file = f"Q04740_and_{name}_ranked_0.pdb"
        f.write(f'cp "$source_dir/{pdb_file}" "$dest_dir/" 2>/dev/null || echo "PDB file not found: {pdb_file}"\n')

print("Scripts and files have been generated:")
print("1. afp_Jack_target_names.txt - Contains list of target names")
print("2. afp_Jack_target_names.xlsx - Excel file with target names")
print("3. copy_afp_jack_pdb_files.sh - Script to copy PDB files (optional)") 