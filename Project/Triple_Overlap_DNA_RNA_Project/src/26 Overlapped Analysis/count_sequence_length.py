def count_sequence_lengths(fasta_file):
    """
    Count the length of each sequence in a FASTA file.
    
    Args:
        fasta_file (str): Path to the FASTA file
        
    Returns:
        dict: Dictionary with sequence IDs as keys and sequence lengths as values
    """
    sequence_lengths = {}
    current_id = None
    current_sequence = ""
    
    with open(fasta_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                # If we have a previous sequence, save its length
                if current_id:
                    sequence_lengths[current_id] = len(current_sequence)
                # Start new sequence
                current_id = line[1:]  # Remove the '>' character
                current_sequence = ""
            else:
                # Add to current sequence
                current_sequence += line
    
    # Don't forget to add the last sequence
    if current_id:
        sequence_lengths[current_id] = len(current_sequence)
    
    return sequence_lengths

if __name__ == "__main__":
    # Example usage
    fasta_file = "/Users/conny/Desktop/AlphaFold/Summer Project/src/26 Overlapped Analysis/overlapping_proteins.fasta"
    lengths = count_sequence_lengths(fasta_file)
    
    # Print results
    print("Sequence lengths:")
    for seq_id, length in lengths.items():
        print(f"{seq_id}: {length} amino acids") 