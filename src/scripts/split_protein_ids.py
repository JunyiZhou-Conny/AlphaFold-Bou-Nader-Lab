def split_protein_ids(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Strip any leading/trailing whitespace
            line = line.strip()
            # Split the line by semicolon
            protein_ids = line.split(';')
            # Write each protein ID on a new line
            for protein_id in protein_ids:
                if protein_id:  # Ensure it's not an empty string
                    outfile.write(protein_id + '\n')

# Usage
split_protein_ids('AlphaFold/protein_ids.txt', 'AlphaFold/protein_ids_processed.txt') 