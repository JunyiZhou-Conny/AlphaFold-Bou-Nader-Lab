import os
import re

# Set the directory containing your files
folder = "/Users/conny/Desktop/folds_2025_06_12_16_32/27_overlapped_cif"  # <-- change this to your folder

# Regex to extract accession (e.g., o00567)
pattern = re.compile(r'_\d+_([0-9a-zA-Z]+)_')

for filename in os.listdir(folder):
    # Only process files (not directories)
    if os.path.isfile(os.path.join(folder, filename)):
        match = pattern.search(filename)
        if match:
            accession = f"o{match.group(1)}"
            ext = os.path.splitext(filename)[1]
            new_name = accession + ext
            src = os.path.join(folder, filename)
            dst = os.path.join(folder, new_name)
            # Avoid overwriting files
            if not os.path.exists(dst):
                os.rename(src, dst)
                print(f"Renamed {filename} -> {new_name}")
            else:
                print(f"Skipped {filename}: {new_name} already exists")
        else:
            print(f"Skipped {filename}: no accession found")