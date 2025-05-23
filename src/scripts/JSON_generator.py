import json
import yaml
from Bio import SeqIO
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Entity:
    id: str
    type: str  # protein, dna, rna, ligand, ion
    name: str
    sequence: Optional[str] = None
    modifications: List[Dict] = None
    glycans: List[Dict] = None
    count: int = 1
    useStructureTemplate: bool = False
    maxTemplateDate: Optional[str] = None

class AlphaFoldJobGenerator:
    def __init__(self, config_file: str, fasta_file: str):
        """
        Initialize the job generator with configuration and FASTA file
        
        Args:
            config_file (str): Path to YAML configuration file
            fasta_file (str): Path to FASTA file containing sequences
        """
        self.config = self._load_config(config_file)
        self.sequences = self._load_sequences(fasta_file)
        self.entities = self._initialize_entities()

    def _load_config(self, config_file: str) -> Dict:
        """Load and validate configuration file"""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def _load_sequences(self, fasta_file: str) -> Dict[str, str]:
        """Load sequences from FASTA file"""
        sequences = {}
        for record in SeqIO.parse(fasta_file, "fasta"):
            sequences[record.id] = str(record.seq)
        return sequences

    def _initialize_entities(self) -> Dict[str, Entity]:
        """Initialize Entity objects from configuration"""
        entities = {}
        for entity_id, entity_data in self.config['entities'].items():
            if entity_id not in self.sequences:
                raise ValueError(f"Sequence not found for entity {entity_id}")
            
            entity = Entity(
                id=entity_id,
                type=entity_data['type'],
                name=entity_data['name'],
                sequence=self.sequences[entity_id],
                modifications=entity_data.get('modifications', []),
                glycans=entity_data.get('glycans', []),
                count=entity_data.get('count', 1),
                useStructureTemplate=entity_data.get('useStructureTemplate', False),
                maxTemplateDate=entity_data.get('maxTemplateDate')
            )
            entities[entity_id] = entity
        return entities

    def _create_sequence_entry(self, entity: Entity) -> Dict:
        """Create a sequence entry for the JSON output"""
        if entity.type == 'protein':
            entry = {
                "proteinChain": {
                    "sequence": entity.sequence,
                    "count": entity.count,
                    "useStructureTemplate": entity.useStructureTemplate
                }
            }
            if entity.modifications:
                entry["proteinChain"]["modifications"] = entity.modifications
            if entity.glycans:
                entry["proteinChain"]["glycans"] = entity.glycans
            if entity.maxTemplateDate:
                entry["proteinChain"]["maxTemplateDate"] = entity.maxTemplateDate
                
        elif entity.type in ['dna', 'rna']:
            entry = {
                f"{entity.type}Sequence": {
                    "sequence": entity.sequence,
                    "count": entity.count
                }
            }
            if entity.modifications:
                entry[f"{entity.type}Sequence"]["modifications"] = entity.modifications
                
        elif entity.type in ['ligand', 'ion']:
            entry = {
                entity.type: {
                    entity.type: entity.sequence,
                    "count": entity.count
                }
            }
            
        return entry

    def generate_jobs(self, output_dir: str):
        """Generate JSON files for each job defined in the configuration"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for job in self.config['jobs']:
            job_name = job['name']
            entity_ids = job['entities']
            
            # Create job entry
            job_entry = {
                "name": job_name,
                "modelSeeds": [],
                "sequences": [],
                "dialect": "alphafoldserver",
                "version": 1
            }
            
            # Add sequences for each entity
            for entity_id in entity_ids:
                if entity_id not in self.entities:
                    raise ValueError(f"Entity {entity_id} not found in configuration")
                entity = self.entities[entity_id]
                sequence_entry = self._create_sequence_entry(entity)
                job_entry["sequences"].append(sequence_entry)
            
            # Write job to file
            output_file = output_path / f"{job_name}.json"
            with open(output_file, 'w') as f:
                json.dump([job_entry], f, indent=2)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate AlphaFold3 JSON jobs')
    parser.add_argument('config_file', help='Path to YAML configuration file')
    parser.add_argument('fasta_file', help='Path to FASTA file containing sequences')
    parser.add_argument('output_dir', help='Directory to save output JSON files')
    
    args = parser.parse_args()
    
    generator = AlphaFoldJobGenerator(args.config_file, args.fasta_file)
    generator.generate_jobs(args.output_dir)

if __name__ == "__main__":
    main()