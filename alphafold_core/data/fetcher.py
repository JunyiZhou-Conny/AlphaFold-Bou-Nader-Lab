"""
Data fetching module for AlphaFold Core
Handles fetching protein sequences and other biological data
"""

import requests
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from tqdm import tqdm
import time
import random
import logging
import datetime
from dataclasses import dataclass

from ..config import config
from ..utils import rate_limited_request, setup_logging


@dataclass
class SearchCriteria:
    """Configuration for UniProt search criteria"""
    organism_id: Optional[str] = "9606"  # Human by default
    reviewed_only: bool = True
    exact_match: bool = True
    max_results: int = 10
    include_synonyms: bool = True


class UniProtFetcher:
    """Fetches data from UniProt API with rate limiting and error handling"""
    
    def __init__(self, base_url: str = None, max_retries: int = None, timeout: int = None):
        self.base_url = base_url or config.uniprot_base_url
        self.max_retries = max_retries or config.max_retries
        self.timeout = timeout or config.request_timeout
        self.session = self._setup_session()
        self.logger = setup_logging()
    
    def _setup_session(self):
        """Configure requests session with retry strategy"""
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
    
    @rate_limited_request
    def fetch_protein_sequence(self, protein_id: str) -> Optional[str]:
        """Fetch protein sequence from UniProt"""
        try:
            url = f"{self.base_url}/{protein_id}"
            response = self.session.get(
                url,
                headers={"accept": "application/json"},
                params={"fields": ["sequence"]},
                timeout=self.timeout
            )
            
            if response.ok:
                data = response.json()
                sequence_info = data.get("sequence", {})
                return sequence_info.get("value", None)
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                self.logger.warning(f"Rate limit hit, waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self.fetch_protein_sequence(protein_id)  # Retry
            else:
                self.logger.warning(f"Failed to fetch {protein_id} (Status: {response.status_code})")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.warning(f"Timeout for {protein_id}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {protein_id}: {str(e)}")
            return None

    def _build_search_query(self, gene_name: str, criteria: SearchCriteria) -> str:
        """Build UniProt search query based on criteria"""
        query_parts = []
        
        # Gene name matching - use gene_exact for exact matching
        if criteria.exact_match:
            query_parts.append(f"gene_exact:{gene_name}")
        else:
            query_parts.append(f"gene:{gene_name}")
        
        # Organism filtering
        if criteria.organism_id:
            query_parts.append(f"organism_id:{criteria.organism_id}")
        
        # Reviewed status filtering
        if criteria.reviewed_only:
            query_parts.append("reviewed:true")
        
        return " AND ".join(query_parts)

    def _extract_protein_info(self, result: Dict, gene_name: str) -> Dict:
        """Extract protein information from UniProt result"""
        genes = result.get("genes", [])
        gene_info = genes[0] if genes else {}
        
        # Extract protein name from the correct path
        protein_name = "Unknown"
        if "proteinDescription" in result:
            recommended_name = result["proteinDescription"].get("recommendedName", {})
            if recommended_name and "fullName" in recommended_name:
                protein_name = recommended_name["fullName"].get("value", "Unknown")
        
        # Determine if entry is reviewed based on entryType
        is_reviewed = result.get("entryType", "").startswith("UniProtKB reviewed")
        
        return {
            "accession": result.get("primaryAccession"),
            "id": result.get("uniProtkbId"),
            "gene_names": gene_info.get("geneName", {}).get("value", gene_name),
            "protein_name": protein_name,
            "sequence": result.get("sequence", {}).get("value"),
            "organism": result.get("organism", {}).get("scientificName", "Unknown"),
            "reviewed": is_reviewed,
            "entry_type": result.get("entryType", "Unknown")
        }

    @rate_limited_request
    def search_by_gene_name_robust(self, gene_name: str, criteria: SearchCriteria = None) -> Optional[Dict]:
        """
        Robust gene search with multiple fallback strategies
        
        Strategy 1: Exact gene name + organism + reviewed
        Strategy 2: Exact gene name + organism (no reviewed filter)
        Strategy 3: Fuzzy gene name + organism + reviewed
        Strategy 4: Fuzzy gene name + organism (no reviewed filter)
        """
        if criteria is None:
            criteria = SearchCriteria()
        
        strategies = [
            # Strategy 1: Most strict
            SearchCriteria(
                organism_id=criteria.organism_id,
                reviewed_only=True,
                exact_match=True,
                max_results=criteria.max_results
            ),
            # Strategy 2: No reviewed filter
            SearchCriteria(
                organism_id=criteria.organism_id,
                reviewed_only=False,
                exact_match=True,
                max_results=criteria.max_results
            ),
            # Strategy 3: Fuzzy matching with reviewed
            SearchCriteria(
                organism_id=criteria.organism_id,
                reviewed_only=True,
                exact_match=False,
                max_results=criteria.max_results
            ),
            # Strategy 4: Most lenient
            SearchCriteria(
                organism_id=criteria.organism_id,
                reviewed_only=False,
                exact_match=False,
                max_results=criteria.max_results
            )
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                self.logger.debug(f"Trying strategy {i} for gene {gene_name}")
                result = self._search_with_strategy(gene_name, strategy)
                if result:
                    self.logger.info(f"Found protein for gene {gene_name} using strategy {i}")
                    return result
            except Exception as e:
                self.logger.warning(f"Strategy {i} failed for gene {gene_name}: {e}")
                continue
        
        self.logger.warning(f"All search strategies failed for gene {gene_name}")
        return None

    def _search_with_strategy(self, gene_name: str, criteria: SearchCriteria) -> Optional[Dict]:
        """Execute search with specific strategy"""
        query = self._build_search_query(gene_name, criteria)
        
        search_url = f"{self.base_url}/uniprotkb/search"
        params = {
            "query": query,
            "fields": "accession,gene_names,protein_name,organism_name,sequence",
            "format": "json",
            "size": criteria.max_results
        }
        response = self.session.get(
            search_url,
            headers={"accept": "application/json"},
            params=params,
            timeout=self.timeout
        )
        
        if response.ok:
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return None
            
            # If multiple results, prioritize reviewed entries
            if len(results) > 1:
                reviewed_results = [r for r in results if r.get("reviewed", False)]
                if reviewed_results:
                    results = reviewed_results
            
            # Take the first result (most relevant)
            result = results[0]
            protein_info = self._extract_protein_info(result, gene_name)
            
            # Add information about multiple results if applicable
            if len(data.get("results", [])) > 1:
                protein_info["multiple_results_found"] = True
                protein_info["total_results"] = len(data.get("results", []))
                protein_info["selected_result"] = "First reviewed entry" if any(r.get("reviewed", False) for r in data.get("results", [])) else "First result"
                protein_info["all_accessions"] = [r.get("primaryAccession") for r in data.get("results", [])]
                protein_info["all_protein_names"] = [r.get("proteinName", {}).get("value", "Unknown") for r in data.get("results", [])]
            else:
                protein_info["multiple_results_found"] = False
                protein_info["total_results"] = 1
                protein_info["selected_result"] = "Single result"
            
            return protein_info
        
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            self.logger.warning(f"Rate limit hit, waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return self._search_with_strategy(gene_name, criteria)  # Retry
        
        else:
            self.logger.warning(f"Failed to search for gene {gene_name} (Status: {response.status_code})")
            return None

    @rate_limited_request
    def search_by_gene_name(self, gene_name: str) -> Optional[Dict]:
        """Legacy method - now uses robust search with default criteria"""
        return self.search_by_gene_name_robust(gene_name, SearchCriteria())

    def search_multiple_genes_robust(self, gene_names: List[str], 
                                   criteria: SearchCriteria = None) -> Dict[str, Dict]:
        """Search multiple genes with robust strategies and detailed tracking"""
        if criteria is None:
            criteria = SearchCriteria()
        
        results = {}
        failed_queries = []
        strategy_stats = {1: 0, 2: 0, 3: 0, 4: 0}
        
        start_time = time.time()
        total = len(gene_names)
        print(f"[{datetime.datetime.now()}] Starting robust UniProt search for {total} genes...")
        print(f"Search criteria: organism={criteria.organism_id}, reviewed={criteria.reviewed_only}, exact={criteria.exact_match}")

        with tqdm(total=total, desc="Searching genes", ncols=100) as pbar:
            for idx, gene_name in enumerate(gene_names):
                gene_name = gene_name.strip()
                if gene_name and gene_name not in results:
                    # Try robust search
                    protein_info = self.search_by_gene_name_robust(gene_name, criteria)
                    if protein_info:
                        results[gene_name] = protein_info
                    else:
                        results[gene_name] = {"error": "Gene not found after all strategies"}
                        failed_queries.append(gene_name)
                
                pbar.update(1)
                
                # Print status every 10 genes or at the end
                if (idx + 1) % 10 == 0 or (idx + 1) == total:
                    elapsed = time.time() - start_time
                    success_count = len([r for r in results.values() if "error" not in r])
                    print(f"[{datetime.datetime.now()}] Processed {idx+1}/{total} genes. Success: {success_count}, Fail: {len(failed_queries)}. Elapsed: {elapsed:.1f}s")
        
        print(f"[{datetime.datetime.now()}] Robust UniProt search completed. Total time: {time.time() - start_time:.1f}s")
        self.logger.info(f"Successfully found: {len(results) - len(failed_queries)} genes")
        self.logger.info(f"Failed to find: {len(failed_queries)} genes")
        
        return results

    def search_multiple_genes(self, gene_names: List[str]) -> Dict[str, Dict]:
        """Legacy method - now uses robust search"""
        return self.search_multiple_genes_robust(gene_names, SearchCriteria())

    def fetch_multiple_sequences(self, protein_ids: List[str], 
                               output_file: str = "protein_sequences.fasta",
                               failed_queries_file: str = "failed_queries.csv") -> Dict[str, str]:
        """Fetch multiple protein sequences with progress tracking"""
        results = {}
        failed_queries = []
        
        for protein_id in tqdm(protein_ids, desc="Fetching sequences"):
            protein_id = protein_id.strip()
            if protein_id and protein_id not in results:
                sequence = self.fetch_protein_sequence(protein_id)
                if sequence:
                    results[protein_id] = sequence
                else:
                    results[protein_id] = "Sequence Not Found"
                    failed_queries.append(protein_id)
        
        # Save results
        self._save_sequences_to_fasta(results, output_file)
        if failed_queries:
            self._save_failed_queries(failed_queries, failed_queries_file)
        
        self.logger.info(f"Successfully retrieved: {len(results) - len(failed_queries)} sequences")
        self.logger.info(f"Failed to retrieve: {len(failed_queries)} sequences")
        
        return results
    
    def _save_sequences_to_fasta(self, sequences: Dict[str, str], output_file: str):
        """Save sequences to FASTA format"""
        with open(output_file, "w") as f:
            for protein_id, sequence in sequences.items():
                f.write(f">{protein_id}\n{sequence}\n")
        self.logger.info(f"Sequences saved to {output_file}")
    
    def _save_failed_queries(self, failed_queries: List[str], output_file: str):
        """Save failed queries to CSV"""
        pd.DataFrame({"protein_id": failed_queries}).to_csv(output_file, index=False)
        self.logger.info(f"Failed queries saved to {output_file}")


class ProteinSequenceFetcher:
    """High-level interface for protein sequence fetching operations"""
    
    def __init__(self):
        self.uniprot_fetcher = UniProtFetcher()
        self.logger = setup_logging()
    
    def fetch_from_excel(self, excel_file: str, column_name: str = "Protein IDs", 
                        header_row: int = 2) -> Dict[str, str]:
        """Fetch protein sequences from Excel file"""
        try:
            df = pd.read_excel(excel_file, header=header_row)
            protein_ids = df[column_name].dropna().unique()
            
            output_file = Path(excel_file).stem + "_sequences.fasta"
            failed_file = Path(excel_file).stem + "_failed_queries.csv"
            
            return self.uniprot_fetcher.fetch_multiple_sequences(
                protein_ids, output_file, failed_file
            )
        except Exception as e:
            self.logger.error(f"Error processing Excel file {excel_file}: {e}")
            return {}
    
    def fetch_from_csv(self, csv_file: str, column_name: str = "protein_id") -> Dict[str, str]:
        """Fetch protein sequences from CSV file"""
        try:
            df = pd.read_csv(csv_file)
            protein_ids = df[column_name].dropna().unique()
            
            output_file = Path(csv_file).stem + "_sequences.fasta"
            failed_file = Path(csv_file).stem + "_failed_queries.csv"
            
            return self.uniprot_fetcher.fetch_multiple_sequences(
                protein_ids, output_file, failed_file
            )
        except Exception as e:
            self.logger.error(f"Error processing CSV file {csv_file}: {e}")
            return {}
    
    def fetch_from_tsv(self, tsv_file: str, column_name: str = "GENE") -> Dict[str, Dict]:
        """Fetch protein information from TSV file with gene names"""
        try:
            df = pd.read_csv(tsv_file, sep='\t')
            gene_names = df[column_name].dropna().unique()
            
            self.logger.info(f"Found {len(gene_names)} unique genes in {tsv_file}")
            
            return self.uniprot_fetcher.search_multiple_genes(gene_names)
        except Exception as e:
            self.logger.error(f"Error processing TSV file {tsv_file}: {e}")
            return {}
    
    def fetch_from_tsv_robust(self, tsv_file: str, column_name: str = "GENE", 
                            criteria: SearchCriteria = None) -> Dict[str, Dict]:
        """Fetch protein information from TSV file with robust search strategies"""
        try:
            df = pd.read_csv(tsv_file, sep='\t')
            gene_names = df[column_name].dropna().unique()
            
            self.logger.info(f"Found {len(gene_names)} unique genes in {tsv_file}")
            
            return self.uniprot_fetcher.search_multiple_genes_robust(gene_names, criteria)
        except Exception as e:
            self.logger.error(f"Error processing TSV file {tsv_file}: {e}")
            return {}
    
    def fetch_from_list(self, protein_ids: List[str], 
                       output_file: str = "protein_sequences.fasta") -> Dict[str, str]:
        """Fetch protein sequences from a list of IDs"""
        failed_file = Path(output_file).stem + "_failed_queries.csv"
        return self.uniprot_fetcher.fetch_multiple_sequences(
            protein_ids, output_file, failed_file
        )
    
    def process_genes_to_proteins(self, tsv_file: str, column_name: str = "GENE") -> Dict[str, Dict]:
        """Process TSV file with genes and return comprehensive protein information"""
        return self.fetch_from_tsv(tsv_file, column_name)
    
    def process_genes_to_proteins_robust(self, tsv_file: str, column_name: str = "GENE",
                                       criteria: SearchCriteria = None) -> Dict[str, Dict]:
        """Process TSV file with genes using robust search strategies"""
        return self.fetch_from_tsv_robust(tsv_file, column_name, criteria) 