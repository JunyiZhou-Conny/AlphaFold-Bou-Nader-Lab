import os
import shutil

# Set the directory to search (change this to your target directory)
base_dir = "/Users/conny/Desktop/triple_overlap_af3_cluster"

# Output folders
cif_folder = os.path.join(base_dir, "cluster_overlapped_cif")
json_folder = os.path.join(base_dir, "cluster_overlapped_json")

# Create output folders if they don't exist
os.makedirs(cif_folder, exist_ok=True)
os.makedirs(json_folder, exist_ok=True)

# Walk through the directory tree
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith("_model.cif"):
            src = os.path.join(root, file)
            dst = os.path.join(cif_folder, file)
            shutil.move(src, dst)
            print(f"Moved {src} -> {dst}")
        elif file.endswith("_summary_confidences.json"):
            src = os.path.join(root, file)
            dst = os.path.join(json_folder, file)
            shutil.move(src, dst)
            print(f"Moved {src} -> {dst}")

print("Done organizing files!")