#!/bin/bash

# Script to extract model_0.cif files from test folds and rename them to protein_id
# Usage: ./extract_model_0_files.sh

# Set source and destination directories
SOURCE_DIR="/data7/Conny/Projects/Dicer_685/AF3_Server/data/Dicer/folds_all"
DEST_DIR="/data7/Conny/Projects/Dicer_685/AF3_Server/data/Dicer/visualization"

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Counter for processed files
count=0

echo "Starting extraction of model_0.cif files..."
echo "Source: $SOURCE_DIR"
echo "Destination: $DEST_DIR"
echo "----------------------------------------"

# Find all model_0.cif files and process them
find "$SOURCE_DIR" -name "*model_0.cif" | while read -r file; do
    # Extract the filename
    filename=$(basename "$file")
    
    # Extract protein ID using regex
    # Pattern: fold_test_fold_job_*_q9upy3_*_model_0.cif
    # We want the part after the last underscore before "_model_0.cif"
    if [[ $filename =~ fold_test_fold_job_[0-9]+_([^_]+)_([^_]+)_model_0\.cif ]]; then
        protein_id="${BASH_REMATCH[1]}_${BASH_REMATCH[2]}"
        
        # Create new filename
        new_filename="${protein_id}.cif"
        dest_path="$DEST_DIR/$new_filename"
        
        # Copy the file
        cp "$file" "$dest_path"
        
        if [ $? -eq 0 ]; then
            echo "✓ Copied: $filename -> $new_filename"
            ((count++))
        else
            echo "✗ Failed to copy: $filename"
        fi
    else
        echo "✗ Could not extract protein ID from: $filename"
    fi
done

echo "----------------------------------------"
echo "Extraction complete! Processed $count files."
echo "Files are now in: $DEST_DIR" 