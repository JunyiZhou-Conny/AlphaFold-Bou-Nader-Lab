import os
import json

FASTA_PATH = "overlapping_proteins.fasta"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Nucleic acid sequences
DNA1 = "GGCTTAGAGCTTAATTGCTGAATCTGGTGC"
DNA2 = "ACATGTTGGATCCCACGTTGCATGCTGATAGCCTACTAGAGCTGTATGAATTCAAATGAC"
DNA3 = "GCACCAGATTCAGCAATTAAGCTCTAAGCC"
DNA4 = "GTCATTTGAATTCATGGCTTAGAGCTTAATTGCTGAATCTGGTGCTGGGATCCAACATGT"
RNA1 = "GCACCAGAUUCAGCAAUUAAGCUCUAAGCC"
RNA2 = "GGCUUAGAGCUUAAUUGCUGAAUCUGGUGC"

# Read FASTA
proteins = []
with open(os.path.join(OUTPUT_DIR, FASTA_PATH)) as f:
    name, seq = None, []
    for line in f:
        line = line.strip()
        if line.startswith('>'):
            if name:
                proteins.append((name, ''.join(seq)))
            name = line[1:]
            seq = []
        else:
            seq.append(line)
    if name:
        proteins.append((name, ''.join(seq)))

# Helper to build entries

def make_entry(name, seqs, tag):
    entry = {
        "name": f"{name}-{tag}",
        "modelSeeds": [],
        "sequences": [],
        "dialect": "alphafoldserver",
        "version": 1
    }
    for s in seqs:
        if s[0] == "proteinChain":
            entry["sequences"].append({"proteinChain": {"sequence": s[1], "count": 1}})
        elif s[0] == "dnaSequence":
            entry["sequences"].append({"dnaSequence": {"sequence": s[1], "count": 1}})
        elif s[0] == "rnaSequence":
            entry["sequences"].append({"rnaSequence": {"sequence": s[1], "count": 1}})
    return entry

# Build all four sets
ssDNA = []
Rloop = []
dsDNA = []
dsRNA = []

for name, seq in proteins:
    ssDNA.append(make_entry(name, [("proteinChain", seq), ("dnaSequence", DNA1)], "DNA1"))
    Rloop.append(make_entry(name, [("proteinChain", seq), ("dnaSequence", DNA2), ("dnaSequence", DNA4), ("rnaSequence", RNA1)], "Rloop"))
    dsDNA.append(make_entry(name, [("proteinChain", seq), ("dnaSequence", DNA1), ("dnaSequence", DNA3)], "dsDNA"))
    dsRNA.append(make_entry(name, [("proteinChain", seq), ("rnaSequence", RNA1), ("rnaSequence", RNA2)], "dsRNA"))

# Write JSON files
with open(os.path.join(OUTPUT_DIR, "ssDNA_predictions.json"), "w") as f:
    json.dump(ssDNA, f, indent=2)
with open(os.path.join(OUTPUT_DIR, "Rloop_predictions.json"), "w") as f:
    json.dump(Rloop, f, indent=2)
with open(os.path.join(OUTPUT_DIR, "dsDNA_predictions.json"), "w") as f:
    json.dump(dsDNA, f, indent=2)
with open(os.path.join(OUTPUT_DIR, "dsRNA_predictions.json"), "w") as f:
    json.dump(dsRNA, f, indent=2)

print("All JSON files generated!") 