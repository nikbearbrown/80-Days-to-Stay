#!/usr/bin/env python3
"""
sec_domain_inference.py - Infer domain names from company names in SEC data
Usage: python sec_domain_inference.py [input_json_file]
Default: python sec_domain_inference.py (uses sec_companies_targets_unique.json)

This script runs fully automated and can be safely interrupted and resumed.
"""

import json
import sys
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# Domain patterns to try, in order of likelihood
DOMAIN_PATTERNS = [
    '.com',
    '.io',
    '.co',
    '.ai',
    '.tech',
    '.bio',
    '-bio.com',
    'bio.com',
    '.health',
    '.app',
    '.dev',
    '.net',
    '.org'
]

# Common company suffixes to remove
COMPANY_SUFFIXES = [
    r'\s+inc\.?$',
    r'\s+incorporated$',
    r'\s+llc\.?$',
    r'\s+ltd\.?$',
    r'\s+limited$',
    r'\s+corp\.?$',
    r'\s+corporation$',
    r'\s+co\.?$',
    r'\s+company$',
    r'\s+l\.?p\.?$',  # Limited Partnership
    r'\s+lp$',
    r'\s+plc\.?$',  # Public Limited Company
    r'\s+group$',
    r'\s+holdings?$',
    r'\s+ventures?$',
    r'\s+partners?$',
    r'\s+investments?$',
    r'\s+capital$',
    r'\s+fund$',
    r'\s+technologies$',
    r'\s+technology$',
    r'\s+tech$',
    r'\s+solutions?$',
    r'\s+services?$',
    r'\s+enterprises?$',
    r',?\s+llc\.?$',  # Handle ", LLC"
    r',?\s+inc\.?$',  # Handle ", Inc"
]


def clean_company_name(name: str) -> str:
    """
    Clean company name for domain inference.
    Remove suffixes, special characters, and normalize.
    """
    if not name:
        return ""
    
    # Convert to lowercase
    cleaned = name.lower().strip()
    
    # Remove common suffixes (case insensitive)
    for suffix_pattern in COMPANY_SUFFIXES:
        cleaned = re.sub(suffix_pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Remove special characters but keep hyphens and spaces temporarily
    cleaned = re.sub(r'[^\w\s-]', '', cleaned)
    
    # Replace spaces and underscores with hyphens
    cleaned = re.sub(r'[\s_]+', '-', cleaned)
    
    # Remove multiple consecutive hyphens
    cleaned = re.sub(r'-+', '-', cleaned)
    
    # Remove leading/trailing hyphens
    cleaned = cleaned.strip('-')
    
    return cleaned


def infer_domain(company_name: str, max_patterns: int = 5) -> List[str]:
    """
    Infer possible domain names from company name.
    Returns list of domain patterns to try.
    """
    if not company_name:
        return []
    
    cleaned = clean_company_name(company_name)
    
    if not cleaned:
        return []
    
    # Generate domain candidates
    domains = []
    
    # Try first N patterns
    for pattern in DOMAIN_PATTERNS[:max_patterns]:
        if pattern.startswith('-'):
            # Pattern like '-bio.com' 
            domain = cleaned + pattern
        elif pattern.startswith('.'):
            # Pattern like '.com'
            domain = cleaned + pattern
        else:
            # Pattern like 'bio.com' (replace last part)
            domain = cleaned + '.' + pattern
        
        domains.append(domain)
    
    # Also try without hyphens for .com (common case)
    if '-' in cleaned and '.com' in DOMAIN_PATTERNS[:max_patterns]:
        no_hyphen = cleaned.replace('-', '')
        domains.insert(1, no_hyphen + '.com')  # High priority
    
    # Remove duplicates while preserving order
    seen = set()
    unique_domains = []
    for d in domains:
        if d not in seen:
            seen.add(d)
            unique_domains.append(d)
    
    return unique_domains


def save_checkpoint(output_file: Path, data: Dict, stats: Dict):
    """Save progress checkpoint."""
    # Update metadata
    if 'metadata' in data:
        data['metadata']['domain_inference'] = {
            'processed': stats['processed'],
            'total': stats['total'],
            'with_domains': stats['with_domains'],
            'last_checkpoint': datetime.now().isoformat()
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    elapsed = time.time() - stats['start_time']
    rate = stats['processed'] / elapsed if elapsed > 0 else 0
    print(f"💾 Checkpoint saved | Progress: {stats['processed']:,}/{stats['total']:,} | Rate: {rate:.1f}/sec")


def find_last_processed_index(companies: List[Dict]) -> int:
    """Find the index of the last processed company."""
    for i in range(len(companies) - 1, -1, -1):
        if 'inferred_domains' in companies[i]:
            return i + 1
    return 0


def main():
    # Default input file
    default_input = "sec_companies_targets_unique.json"
    
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        input_file = Path(default_input)
    
    if not input_file.exists():
        print(f"❌ Error: File '{input_file}' not found")
        if len(sys.argv) == 1:
            print(f"Usage: python {sys.argv[0]} [input_json_file]")
            print(f"Default: python {sys.argv[0]} (uses {default_input})")
        sys.exit(1)
    
    # Generate output filename
    output_file = input_file.with_name(
        f"{input_file.stem}_urls{input_file.suffix}"
    )
    
    print(f"{'='*70}")
    print(f"SEC Domain Inference Tool - Automated Run")
    print(f"{'='*70}")
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nLoading data...")
    
    # Load the data
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {input_file}: {e}")
        sys.exit(1)
    
    # Extract companies list
    if isinstance(data, dict) and 'companies' in data:
        companies = data['companies']
        metadata = data.get('metadata', {})
    else:
        print("❌ Error: Expected JSON with 'companies' key")
        sys.exit(1)
    
    total_companies = len(companies)
    print(f"Loaded {total_companies:,} companies")
    
    # Check if we're resuming from a previous run
    start_index = 0
    if output_file.exists():
        print(f"\n📂 Found existing output file: {output_file}")
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            existing_companies = existing_data.get('companies', [])
            start_index = find_last_processed_index(existing_companies)
            
            if start_index > 0:
                print(f"🔄 Resuming from index {start_index:,} ({start_index/total_companies*100:.1f}% complete)")
                data = existing_data  # Use existing data
                companies = existing_companies
            else:
                print(f"⚠️  No processed data found in output file, starting fresh")
        except Exception as e:
            print(f"⚠️  Could not resume: {e}")
            print(f"Starting fresh...")
            start_index = 0
    
    if start_index == 0:
        print(f"\n🚀 Starting fresh domain inference...")
    
    print(f"Domain patterns per company: {len(DOMAIN_PATTERNS[:5])}")
    print(f"Checkpoint interval: Every 1000 companies")
    print(f"{'='*70}\n")
    
    # Process companies
    start_time = time.time()
    checkpoint_interval = 1000
    with_domains_count = 0
    
    for i in range(start_index, total_companies):
        company_entry = companies[i]
        company = company_entry.get('company', {})
        company_name = company.get('name', '')
        
        # Infer domain patterns
        inferred_domains = infer_domain(company_name)
        
        # Add inferred domains to the company entry
        company_entry['inferred_domains'] = {
            'domains': inferred_domains,
            'verified': None,
            'checked': False,
            'inferred_at': datetime.now().isoformat()
        }
        
        if inferred_domains:
            with_domains_count += 1
        
        # Periodic progress update (every 1000)
        if (i + 1) % 1000 == 0 or i == start_index:
            elapsed = time.time() - start_time
            rate = (i + 1 - start_index) / elapsed if elapsed > 0 else 0
            pct_done = ((i + 1) / total_companies) * 100
            pct_with_domains = (with_domains_count / (i + 1 - start_index)) * 100 if (i + 1 - start_index) > 0 else 0
            
            print(f"{'='*70}")
            print(f"Progress: {i+1:,} / {total_companies:,} ({pct_done:.1f}%)")
            print(f"Rate: {rate:.1f} companies/sec | Elapsed: {elapsed:.0f}s")
            print(f"With domains: {with_domains_count:,} ({pct_with_domains:.1f}%)")
            print(f"Current: {company_name[:60]}")
            if inferred_domains:
                print(f"Domains: {', '.join(inferred_domains[:3])}")
            print('='*70)
        
        # Checkpoint save every 1000
        if (i + 1) % checkpoint_interval == 0:
            data['companies'] = companies
            save_checkpoint(output_file, data, {
                'processed': i + 1,
                'total': total_companies,
                'with_domains': with_domains_count,
                'start_time': start_time
            })
    
    # Calculate final statistics
    total_with_domains = sum(1 for c in companies if c.get('inferred_domains', {}).get('domains'))
    total_without_domains = total_companies - total_with_domains
    total_elapsed = time.time() - start_time
    
    print(f"\n{'='*70}")
    print(f"✅ COMPLETED!")
    print(f"{'='*70}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
    print(f"\nRESULTS:")
    print(f"  Total companies: {total_companies:,}")
    print(f"  With inferred domains: {total_with_domains:,} ({total_with_domains/total_companies*100:.1f}%)")
    print(f"  Without domains: {total_without_domains:,} ({total_without_domains/total_companies*100:.1f}%)")
    print(f"  Average rate: {total_companies/total_elapsed:.1f} companies/sec")
    
    # Update metadata
    if 'metadata' in data:
        data['metadata']['domain_inference'] = {
            'completed_at': datetime.now().isoformat(),
            'total_processed': total_companies,
            'with_domains': total_with_domains,
            'without_domains': total_without_domains,
            'patterns_tried': len(DOMAIN_PATTERNS[:5]),
            'success_rate': total_with_domains / total_companies if total_companies > 0 else 0,
            'processing_time_seconds': total_elapsed
        }
    
    # Save final output
    data['companies'] = companies
    print(f"\n💾 Saving final output to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    input_size = input_file.stat().st_size
    output_size = output_file.stat().st_size
    
    print(f"✅ Complete!")
    print(f"   Output: {output_file}")
    print(f"   File size: {input_size:,} → {output_size:,} bytes ({(1-output_size/input_size)*100:.1f}% reduction)")
    
    # Show some examples
    print(f"\n{'='*70}")
    print("Sample domain inferences (first 10 companies):")
    print('='*70)
    for i, company_entry in enumerate(companies[:10]):
        company = company_entry.get('company', {})
        name = company.get('name', '')
        domains = company_entry.get('inferred_domains', {}).get('domains', [])
        if domains:
            print(f"{i+1}. {name}")
            print(f"   → {', '.join(domains[:3])}")
    
    print(f"\n{'='*70}")
    print("🎉 Domain inference complete! You can now proceed to domain verification.")
    print('='*70)


if __name__ == "__main__":
    main()