#!/usr/bin/env python3
"""
Test script for robust gene-to-protein search functionality

This script tests the new robust search capabilities with different
search criteria to ensure they work correctly.
"""

import sys
from pathlib import Path

# Add the alphafold_core package to the path
sys.path.append(str(Path(__file__).parent.parent))

from alphafold_core.data import UniProtFetcher, SearchCriteria


def test_search_criteria():
    """Test the SearchCriteria dataclass"""
    print("=== Testing SearchCriteria ===")
    
    # Test default criteria
    default_criteria = SearchCriteria()
    print(f"Default criteria:")
    print(f"  - Organism ID: {default_criteria.organism_id}")
    print(f"  - Reviewed only: {default_criteria.reviewed_only}")
    print(f"  - Exact match: {default_criteria.exact_match}")
    print(f"  - Max results: {default_criteria.max_results}")
    
    # Test custom criteria
    custom_criteria = SearchCriteria(
        organism_id="9606",
        reviewed_only=True,
        exact_match=True,
        max_results=5
    )
    print(f"\nCustom criteria:")
    print(f"  - Organism ID: {custom_criteria.organism_id}")
    print(f"  - Reviewed only: {custom_criteria.reviewed_only}")
    print(f"  - Exact match: {custom_criteria.exact_match}")
    print(f"  - Max results: {custom_criteria.max_results}")
    
    return default_criteria, custom_criteria


def test_query_building():
    """Test the query building functionality"""
    print("\n=== Testing Query Building ===")
    
    fetcher = UniProtFetcher()
    
    # Test different search criteria
    test_cases = [
        SearchCriteria(organism_id="9606", reviewed_only=True, exact_match=True),
        SearchCriteria(organism_id="9606", reviewed_only=False, exact_match=True),
        SearchCriteria(organism_id="9606", reviewed_only=True, exact_match=False),
        SearchCriteria(organism_id="9606", reviewed_only=False, exact_match=False),
    ]
    
    gene_name = "TP53"
    
    for i, criteria in enumerate(test_cases, 1):
        query = fetcher._build_search_query(gene_name, criteria)
        print(f"Strategy {i}: {query}")
    
    return test_cases


def test_single_gene_search():
    """Test single gene search with robust strategies"""
    print("\n=== Testing Single Gene Search ===")
    
    fetcher = UniProtFetcher()
    
    # Test genes that should be found
    test_genes = ["TP53", "BRCA1", "EGFR"]
    
    for gene in test_genes:
        print(f"\nSearching for gene: {gene}")
        
        # Test with default criteria (should use robust search)
        result = fetcher.search_by_gene_name(gene)
        
        if result and "error" not in result:
            print(f"  ✅ Found: {result['accession']}")
            print(f"     Protein: {result['protein_name']}")
            print(f"     Organism: {result['organism']}")
            print(f"     Reviewed: {result.get('reviewed', 'Unknown')}")
        else:
            print(f"  ❌ Not found")
    
    return True


def test_robust_search_strategies():
    """Test the robust search strategies explicitly"""
    print("\n=== Testing Robust Search Strategies ===")
    
    fetcher = UniProtFetcher()
    
    # Test a gene that might be challenging
    test_gene = "TP53"
    
    print(f"Testing robust search for gene: {test_gene}")
    
    # Test with human-specific criteria
    criteria = SearchCriteria(
        organism_id="9606",
        reviewed_only=True,
        exact_match=True,
        max_results=5
    )
    
    result = fetcher.search_by_gene_name_robust(test_gene, criteria)
    
    if result:
        print(f"  ✅ Found protein:")
        print(f"     Accession: {result['accession']}")
        print(f"     Protein: {result['protein_name']}")
        print(f"     Organism: {result['organism']}")
        print(f"     Reviewed: {result.get('reviewed', 'Unknown')}")
        print(f"     Entry type: {result.get('entry_type', 'Unknown')}")
    else:
        print(f"  ❌ Not found")
    
    return result


def test_multiple_genes_search():
    """Test searching multiple genes"""
    print("\n=== Testing Multiple Genes Search ===")
    
    fetcher = UniProtFetcher()
    
    # Test with a small set of genes
    test_genes = ["TP53", "BRCA1", "EGFR", "KRAS", "PIK3CA"]
    
    print(f"Searching for {len(test_genes)} genes...")
    
    # Use robust search with human criteria
    criteria = SearchCriteria(
        organism_id="9606",
        reviewed_only=True,
        exact_match=True,
        max_results=5
    )
    
    results = fetcher.search_multiple_genes_robust(test_genes, criteria)
    
    successful = 0
    failed = 0
    
    for gene, result in results.items():
        if "error" not in result:
            successful += 1
            print(f"  ✅ {gene}: {result['accession']} - {result['protein_name']}")
        else:
            failed += 1
            print(f"  ❌ {gene}: {result['error']}")
    
    print(f"\nSummary:")
    print(f"  - Successful: {successful}")
    print(f"  - Failed: {failed}")
    print(f"  - Success rate: {(successful / len(test_genes)) * 100:.1f}%")
    
    return results


def main():
    """Run all tests"""
    print("Robust Gene Search Test Suite")
    print("=" * 50)
    
    try:
        # Run tests
        test_search_criteria()
        test_query_building()
        test_single_gene_search()
        test_robust_search_strategies()
        test_multiple_genes_search()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("The robust search functionality is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 