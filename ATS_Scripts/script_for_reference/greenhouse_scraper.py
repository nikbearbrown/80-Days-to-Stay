#!/usr/bin/env python3
"""
Greenhouse ATS Job Scraper
Checks if companies use Greenhouse and saves their job listings.
"""

import argparse
import json
import os
import sys
import time
import re
from pathlib import Path
from typing import List, Tuple
import requests


def normalize_company_name(name: str) -> str:
    """Convert company name to Greenhouse URL format."""
    # Common company suffixes to remove
    suffixes = [
        r',?\s+Inc\.?',
        r',?\s+LLC\.?',
        r',?\s+L\.L\.C\.?',
        r',?\s+Corp\.?',
        r',?\s+Corporation',
        r',?\s+L\.P\.?',
        r',?\s+LP\.?',
        r',?\s+Ltd\.?',
        r',?\s+Limited',
        r',?\s+Co\.?',
        r',?\s+Company',
        r',?\s+PLC\.?',
        r',?\s+LTD\.?',
        r',?\s+Liability\s+Co\.?',
        r',?\s+Ltd\s+Liability\s+Co\.?',
    ]
    
    # Remove suffixes (case insensitive)
    cleaned = name
    for suffix in suffixes:
        cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
    
    # Remove any remaining commas, periods, spaces, and special chars
    cleaned = cleaned.strip()
    cleaned = re.sub(r'[,.\s\-&\']', '', cleaned)
    
    return cleaned.lower()


def read_companies_from_file(filepath: str) -> List[str]:
    """Read company names from file, trying multiple encodings."""
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                companies = [line.strip() for line in f if line.strip()]
                if companies:
                    return companies
        except (UnicodeDecodeError, UnicodeError):
            continue
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found")
            sys.exit(1)
    
    # If all encodings fail
    print(f"Error: Could not decode file '{filepath}' with any supported encoding")
    sys.exit(1)


def check_greenhouse(company_name: str, timeout: int = 10) -> Tuple[bool, dict]:
    """
    Check if a company uses Greenhouse and return their jobs.
    
    Returns:
        (uses_greenhouse: bool, jobs_data: dict)
    """
    normalized = normalize_company_name(company_name)
    url = f"https://boards-api.greenhouse.io/v1/boards/{normalized}/jobs"
    
    try:
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 404:
            return False, {}
        
        if response.status_code == 200:
            return True, response.json()
        
        print(f"  ⚠️  Unexpected status {response.status_code} for {company_name}")
        return False, {}
        
    except requests.exceptions.Timeout:
        print(f"  ⏱️  Timeout fetching {company_name}")
        return False, {}
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error fetching {company_name}: {e}")
        return False, {}


def save_jobs(company_name: str, jobs_data: dict, base_dir: str = "greenhouse_jobs") -> bool:
    """Save jobs JSON to company subdirectory."""
    try:
        # Create base directory if it doesn't exist
        base_path = Path(base_dir)
        base_path.mkdir(exist_ok=True)
        
        # Create company subdirectory
        normalized = normalize_company_name(company_name)
        company_dir = base_path / normalized
        company_dir.mkdir(exist_ok=True)
        
        # Save jobs data
        jobs_file = company_dir / "jobs.json"
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        
        # Also save a metadata file with original company name
        metadata = {
            "original_name": company_name,
            "normalized_name": normalized,
            "job_count": len(jobs_data.get('jobs', [])),
            "url": f"https://boards.greenhouse.io/{normalized}"
        }
        
        meta_file = company_dir / "metadata.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error saving {company_name}: {e}")
        return False


def process_companies(companies: List[str], output_dir: str = "greenhouse_jobs", delay: float = 0.5):
    """Process list of companies and save Greenhouse data."""
    results = {
        'found': [],
        'not_found': [],
        'errors': []
    }
    
    print(f"\n🔍 Checking {len(companies)} companies for Greenhouse ATS...\n")
    
    for i, company in enumerate(companies, 1):
        normalized = normalize_company_name(company)
        display_name = f"{company} → {normalized}" if company != normalized else company
        
        print(f"[{i}/{len(companies)}] {display_name}...", end=' ')
        
        uses_greenhouse, jobs_data = check_greenhouse(company)
        
        if uses_greenhouse:
            job_count = len(jobs_data.get('jobs', []))
            print(f"✅ Found! ({job_count} jobs)")
            
            if save_jobs(company, jobs_data, output_dir):
                results['found'].append((company, normalized, job_count))
            else:
                results['errors'].append(company)
        else:
            print("❌ Not using Greenhouse (or no jobs)")
            results['not_found'].append(company)
        
        # Be respectful with rate limiting
        if i < len(companies):
            time.sleep(delay)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✅ Using Greenhouse: {len(results['found'])}")
    for company, normalized, count in results['found']:
        if company != normalized:
            print(f"   • {company} [{normalized}] ({count} jobs)")
        else:
            print(f"   • {company} ({count} jobs)")
    print(f"\n❌ Not using Greenhouse: {len(results['not_found'])}")
    print(f"⚠️  Errors: {len(results['errors'])}")
    
    if results['found']:
        print(f"\n📁 Data saved to: {output_dir}/")


def main():
    parser = argparse.ArgumentParser(
        description='Check companies for Greenhouse ATS and save job listings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Databricks, Inc." HubSpot "Duolingo, Inc."
  %(prog)s -f companies.txt -o data/greenhouse
  %(prog)s "Coca Cola Company" Microsoft Apple --delay 1.0
  
The script automatically strips common suffixes like Inc., LLC, Corp., L.P., etc.
        """
    )
    
    parser.add_argument(
        'companies',
        nargs='*',
        help='Company names to check'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Read company names from file (one per line)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='greenhouse_jobs',
        help='Output directory (default: greenhouse_jobs)'
    )
    
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=0.5,
        help='Delay between requests in seconds (default: 0.5)'
    )
    
    args = parser.parse_args()
    
    # Get company list from either command line or file
    companies = []
    
    if args.file:
        companies = read_companies_from_file(args.file)
    
    if args.companies:
        companies.extend(args.companies)
    
    if not companies:
        parser.print_help()
        sys.exit(1)
    
    process_companies(companies, args.output, args.delay)


if __name__ == '__main__':
    main()