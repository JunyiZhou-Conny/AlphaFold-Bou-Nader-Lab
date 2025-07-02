import os

# === USER INPUTS ===
uniprot_id_file = "/data7/Conny/data/protein_ids.txt"  # one UniProt ID per line
organism_folder = "Saccharomyces_cerevisiae"
output_download_script = "download_found.sh"
# Specify your desired download location (use absolute path for clarity)
output_features_dir = "/data7/Conny/data/FeaturePickleDB"


# === GET YOUR IDs ===
with open(uniprot_id_file, "r") as f:
    target_ids = set(line.strip() for line in f if line.strip())

# === GET FILES IN S3 DIR USING MC ===
print("Getting file list from S3...")
stream = os.popen(f"mc ls embl/alphapulldown/input_features/{organism_folder}")
lines = stream.read().splitlines()

# Parse available IDs from files
available_ids = set()
for line in lines:
    parts = line.strip().split()
    if len(parts) == 0:
        continue
    filename = parts[-1]
    if filename.endswith(".pkl.xz") or filename.endswith(".json.xz"):
        base = filename.split("_")[0]
        available_ids.add(base)

# Find which ones exist
found = sorted(target_ids & available_ids)
not_found = sorted(target_ids - available_ids)

print(f"Found {len(found)} / {len(target_ids)} proteins in database.")
print(f"Missing {len(not_found)} proteins.")

# Write found and not found proteins to files
with open("found_proteins.txt", "w") as f:
    f.write("\n".join(found))

with open("missing_proteins.txt", "w") as f:
    f.write("\n".join(not_found))

print("Written found proteins to: found_proteins.txt")
print("Written missing proteins to: missing_proteins.txt")

# === WRITE DOWNLOAD SCRIPT ===
with open(output_download_script, "w") as f:
    f.write("#!/bin/bash\n\n")
    # Create output directory
    f.write(f"mkdir -p {output_features_dir}\n\n")
    for pid in found:
        f.write(f"mc cp embl/alphapulldown/input_features/{organism_folder}/{pid}.pkl.xz {output_features_dir}/\n")

print(f"Download script written to: {output_download_script}")
print("You can now run:  bash download_found.sh")
