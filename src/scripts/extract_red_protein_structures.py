import os
import shutil
from pathlib import Path

# Paths (update these if needed for your cluster)
RED_PROTEIN_IDS_FILE = '/data7/Conny/specific_proteins/red_proteins/red_protein_ids.txt'
AF3_SOURCE_ROOT = '/data7/Conny/result_AF3/AF3'
AFP_SOURCE_ROOT = '/data7/Conny/result_mmseqs2/pulldown_results/gpu_all'
AF3_DEST = '/data7/Conny/specific_proteins/red_proteins/AF3'
AFP_DEST = '/data7/Conny/specific_proteins/red_proteins/AFP'
Q04740 = 'q04740'

# Ensure destination directories exist
os.makedirs(AF3_DEST, exist_ok=True)
os.makedirs(AFP_DEST, exist_ok=True)

def read_protein_ids(filepath):
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]

def find_cif_file(protein_id):
    # Traverse all subfolders in AF3_SOURCE_ROOT
    for root, dirs, files in os.walk(AF3_SOURCE_ROOT):
        # Look for folder names containing both q04740 and the protein_id
        if Q04740 in root.lower() and protein_id.lower() in root.lower():
            for file in files:
                if file.endswith('_model_0.cif'):
                    return os.path.join(root, file)
    return None

def find_pdb_file(protein_id):
    folder = f'Q04740_and_{protein_id}'
    pdb_path = os.path.join(AFP_SOURCE_ROOT, folder, 'ranked_0.pdb')
    return pdb_path if os.path.isfile(pdb_path) else None

def main():
    protein_ids = read_protein_ids(RED_PROTEIN_IDS_FILE)
    log = []
    for pid in protein_ids:
        # AF3 (CIF)
        cif_src = find_cif_file(pid)
        cif_dst = os.path.join(AF3_DEST, f'AF3_{pid}.cif')
        if cif_src:
            shutil.copy2(cif_src, cif_dst)
            log.append(f'Copied CIF for {pid}: {cif_src} -> {cif_dst}')
        else:
            log.append(f'MISSING CIF for {pid}')
        # AFP (PDB)
        pdb_src = find_pdb_file(pid)
        pdb_dst = os.path.join(AFP_DEST, f'AFP_{pid}.pdb')
        if pdb_src:
            shutil.copy2(pdb_src, pdb_dst)
            log.append(f'Copied PDB for {pid}: {pdb_src} -> {pdb_dst}')
        else:
            log.append(f'MISSING PDB for {pid}')
    # Write log
    with open('extract_red_protein_structures.log', 'w') as f:
        for line in log:
            print(line)
            f.write(line + '\n')

if __name__ == '__main__':
    main() 