import pandas as pd
import os

# Read the filtered AFP data
afp_data = pd.read_csv('/data7/Conny/result_csv/afp_predictions_with_good_interpae_cutoff_100.csv')
afp_filtered = afp_data[(afp_data['iptm_ptm'] >= 0.5) & (afp_data['iptm'] >= 0.6)]

# Extract target names by removing "Q04740_and_" prefix
target_names = afp_filtered['jobs'].str.replace('Q04740_and_', '')

# Save to text file
with open('afp_target_names.txt', 'w') as f:
    for name in target_names:
        f.write(f"{name}\n")

# Save to Excel
target_df = pd.DataFrame({'Target_Names': target_names})
target_df.to_excel('afp_target_names.xlsx', index=False)

# Create directory for PDB files if it doesn't exist
pdb_dir = '/data7/Conny/result_mmseqs2/pulldown_results/ranked_pdbs/Best_Proteins_MMseqs2'
if not os.path.exists(pdb_dir):
    os.makedirs(pdb_dir)

# Create a script to copy PDB files
with open('copy_pdb_files.sh', 'w') as f:
    f.write('#!/bin/bash\n\n')
    f.write('source_dir="/data7/Conny/result_mmseqs2/pulldown_results/ranked_pdbs"\n')
    f.write('dest_dir="/data7/Conny/result_mmseqs2/pulldown_results/ranked_pdbs/Best_Proteins_MMseqs2"\n\n')
    
    for name in target_names:
        pdb_file = f"Q04740_and_{name}_ranked_0.pdb"
        f.write(f'cp "$source_dir/{pdb_file}" "$dest_dir/"\n')

print("Scripts and files have been generated:")
print("1. afp_target_names.txt - Contains list of target names")
print("2. afp_target_names.xlsx - Excel file with target names")
print("3. copy_pdb_files.sh - Script to copy PDB files to Best_Proteins_MMseqs2 directory") 