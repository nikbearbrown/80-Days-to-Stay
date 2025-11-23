#!/usr/bin/env python3
"""
sec_unique.py - Remove duplicate companies from SEC data based on exact name, phone, and address matches
Usage: python sec_unique.py sec_companies_targets.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def normalize_field(value) -> str:
    """Normalize a field value for comparison."""
    if value is None:
        return ""
    return str(value).strip().lower()


def create_dedup_key(company_entry: Dict) -> Tuple[str, str, str]:
    """
    Create a deduplication key from company name, phone, and address.
    Returns a tuple of normalized (name, phone, address).
    """
    company = company_entry.get('company', {})
    
    # Get company name
    name = normalize_field(company.get('name'))
    
    # Get address info
    address = company.get('address', {})
    phone = normalize_field(address.get('phone'))
    
    # Build full address from components
    address_parts = [
        normalize_field(address.get('street1')),
        normalize_field(address.get('street2')),
        normalize_field(address.get('city')),
        normalize_field(address.get('state')),
        normalize_field(address.get('zip'))
    ]
    
    full_address = ' '.join(filter(None, address_parts))
    
    return (name, phone, full_address)


def deduplicate_companies(companies: List[Dict]) -> Tuple[List[Dict], int, Dict]:
    """
    Remove duplicate companies based on exact name, phone, and address matches.
    Returns (unique_companies, duplicate_count, duplicate_stats).
    """
    seen_keys = {}  # Maps key to first occurrence
    unique_companies = []
    duplicate_count = 0
    duplicate_examples = []
    
    for idx, company in enumerate(companies):
        key = create_dedup_key(company)
        
        # Skip if we've seen this exact combination before
        if key in seen_keys:
            duplicate_count += 1
            # Keep first 5 examples for reporting
            if len(duplicate_examples) < 5:
                original_idx = seen_keys[key]
                duplicate_examples.append({
                    'name': company.get('company', {}).get('name'),
                    'original_index': original_idx,
                    'duplicate_index': idx
                })
            continue
        
        seen_keys[key] = idx
        unique_companies.append(company)
    
    stats = {
        'duplicate_examples': duplicate_examples,
        'unique_keys': len(seen_keys)
    }
    
    return unique_companies, duplicate_count, stats


def main():
    if len(sys.argv) < 2:
        print("Usage: python sec_unique.py <input_json_file>")
        print("Example: python sec_unique.py sec_companies_targets.json")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    # Create output filename by inserting '_unique' before extension
    output_file = input_file.with_name(
        f"{input_file.stem}_unique{input_file.suffix}"
    )
    
    print(f"Reading from: {input_file}")
    print(f"Will write to: {output_file}")
    
    # Load the data
    print("\nLoading JSON data...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}")
        sys.exit(1)
    
    # Extract companies list
    if isinstance(data, dict) and 'companies' in data:
        companies = data['companies']
        metadata = data.get('metadata', {})
    else:
        print("Error: Expected JSON with 'companies' key")
        sys.exit(1)
    
    original_count = len(companies)
    print(f"\nOriginal count: {original_count:,} companies")
    if metadata:
        print(f"Date range: {metadata.get('date_range', {}).get('earliest_quarter')} to {metadata.get('date_range', {}).get('latest_quarter')}")
    
    # Deduplicate
    print("\nDeduplicating...")
    unique_companies, duplicate_count, stats = deduplicate_companies(companies)
    
    print(f"\n{'='*60}")
    print(f"RESULTS:")
    print(f"{'='*60}")
    print(f"Unique companies: {len(unique_companies):,}")
    print(f"Duplicates removed: {duplicate_count:,} ({duplicate_count/original_count*100:.1f}%)")
    print(f"Reduction: {original_count:,} → {len(unique_companies):,}")
    
    # Show examples of duplicates found
    if stats['duplicate_examples']:
        print(f"\nFirst {len(stats['duplicate_examples'])} duplicate examples:")
        for ex in stats['duplicate_examples']:
            print(f"  • {ex['name']} (indices: {ex['original_index']}, {ex['duplicate_index']})")
    
    # Update metadata
    output_data = data.copy()
    output_data['companies'] = unique_companies
    
    if 'metadata' in output_data:
        output_data['metadata']['total_companies'] = len(unique_companies)
        output_data['metadata']['duplicates_removed'] = duplicate_count
        output_data['metadata']['deduplication_date'] = str(Path(__file__).stat().st_mtime)
    
    # Write output
    print(f"\nWriting unique companies to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    input_size = input_file.stat().st_size
    output_size = output_file.stat().st_size
    
    print(f"✓ Complete!")
    print(f"  File size: {input_size:,} → {output_size:,} bytes ({(1-output_size/input_size)*100:.1f}% reduction)")


if __name__ == "__main__":
    main()