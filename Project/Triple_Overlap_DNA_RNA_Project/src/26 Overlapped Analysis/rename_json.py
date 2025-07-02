import os
import re

# Set the directory containing your files
folder = "/Users/conny/Desktop/folds_2025_06_12_16_32/27_overlapped_json"

# Regex to extract accession (e.g., o00567)
pattern = re.compile(r'_\d+_([0-9a-zA-Z]+)_')

for filename in os.listdir(folder):
    if os.path.isfile(os.path.join(folder, filename)):
        match = pattern.search(filename)
        if match:
            accession = match.group(1)  # Do NOT prepend 'o'
            ext = os.path.splitext(filename)[1]
            new_name = accession + ext
            src = os.path.join(folder, filename)
            dst = os.path.join(folder, new_name)
            if not os.path.exists(dst):
                os.rename(src, dst)
                print(f"Renamed {filename} -> {new_name}")
            else:
                print(f"Skipped {filename}: {new_name} already exists")
        else:
            print(f"Skipped {filename}: no accession found")