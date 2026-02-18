#!/usr/bin/env python3
"""
Flatten Lever jobs JSON to CSV format.
Supports both full and simple output modes.
"""

import argparse
import json
import csv
import sys
from pathlib import Path
from typing import Dict, Any


def flatten_job_full(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a Lever job dictionary with all fields.
    """
    flattened = {}
    
    # Direct fields
    flattened['job_id'] = job.get('id', '')
    flattened['title'] = job.get('text', '')
    flattened['hosted_url'] = job.get('hostedUrl', '')
    flattened['apply_url'] = job.get('applyUrl', '')
    flattened['country'] = job.get('country', '')
    flattened['workplace_type'] = job.get('workplaceType', '')
    
    # Date fields
    flattened['created_at'] = job.get('createdAt', '')
    
    # Company fields (from metadata we added)
    flattened['company_name'] = job.get('_company_name', '')
    flattened['company_slug'] = job.get('_company_slug', '')
    flattened['company_lever_url'] = job.get('_company_lever_url', '')
    
    # Categories (nested object)
    categories = job.get('categories', {})
    if isinstance(categories, dict):
        flattened['department'] = categories.get('department', '')
        flattened['team'] = categories.get('team', '')
        flattened['commitment'] = categories.get('commitment', '')
        flattened['location'] = categories.get('location', '')
    else:
        flattened['department'] = ''
        flattened['team'] = ''
        flattened['commitment'] = ''
        flattened['location'] = ''
    
    # Description fields
    flattened['description_plain'] = job.get('descriptionPlain', '')
    flattened['additional_plain'] = job.get('additionalPlain', '')
    
    return flattened


def flatten_job_simple(job: Dict[str, Any]) -> Dict[str, str]:
    """
    Flatten a Lever job to just title, company_name, and location.
    """
    # Company name (prefer our metadata)
    company_name = job.get('_company_name', '')
    
    # Location from categories
    categories = job.get('categories', {})
    if isinstance(categories, dict):
        location = categories.get('location', '')
    else:
        location = ''
    
    return {
        'title': job.get('text', ''),
        'company_name': company_name,
        'location': location
    }


def json_to_csv(json_file: str, output_file: str = None, simple: bool = False) -> str:
    """
    Convert Lever jobs JSON to CSV.
    
    Args:
        json_file: Path to input JSON file
        output_file: Path to output CSV file (optional, auto-generated if not provided)
        simple: If True, output only title, company_name, location
    
    Returns:
        Path to the output CSV file
    """
    # Load JSON data
    json_path = Path(json_file)
    
    if not json_path.exists():
        print(f"❌ Error: File '{json_file}' not found")
        sys.exit(1)
    
    print(f"📖 Reading {json_file}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file - {e}")
        sys.exit(1)
    
    # Extract jobs array
    jobs = data.get('jobs', [])
    
    if not jobs:
        print("⚠️  Warning: No jobs found in JSON file")
        sys.exit(1)
    
    print(f"📊 Found {len(jobs):,} jobs")
    
    if simple:
        print(f"🔄 Extracting title, company, and location...\n")
        flatten_func = flatten_job_simple
        suffix = "_simple"
    else:
        print(f"🔄 Flattening all data...\n")
        flatten_func = flatten_job_full
        suffix = ""
    
    # Flatten all jobs
    flattened_jobs = []
    for i, job in enumerate(jobs, 1):
        try:
            flattened_jobs.append(flatten_func(job))
        except Exception as e:
            print(f"  ⚠️  Error processing job {i}: {e}")
            continue
        
        if i % 1000 == 0:
            print(f"  Processed {i:,} jobs...")
    
    if not flattened_jobs:
        print("❌ Error: No jobs could be processed")
        sys.exit(1)
    
    # Generate output filename if not provided
    if output_file is None:
        base_name = json_path.stem
        output_file = json_path.parent / f"{base_name}{suffix}.csv"
    else:
        output_file = Path(output_file)
    
    # Write to CSV
    print(f"\n💾 Writing to {output_file}...")
    
    fieldnames = list(flattened_jobs[0].keys())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_jobs)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"📝 Jobs written: {len(flattened_jobs):,}")
    print(f"📋 Columns: {len(fieldnames)}")
    print(f"✅ Output file: {output_file}")
    
    file_size_kb = output_file.stat().st_size / 1024
    if file_size_kb > 1024:
        print(f"📦 File size: {file_size_kb / 1024:.2f} MB")
    else:
        print(f"📦 File size: {file_size_kb:.2f} KB")
    
    if simple:
        # Show column names
        print(f"\n📊 Columns: {', '.join(fieldnames)}")
        
        # Show preview
        print(f"\n👀 Preview (first 5 rows):")
        print(f"{'Title':<50} {'Company':<40} {'Location':<30}")
        print("-" * 120)
        for job in flattened_jobs[:5]:
            title = job['title'][:47] + '...' if len(job['title']) > 50 else job['title']
            company = job['company_name'][:37] + '...' if len(job['company_name']) > 40 else job['company_name']
            location = job['location'][:27] + '...' if len(job['location']) > 30 else job['location']
            print(f"{title:<50} {company:<40} {location:<30}")
    else:
        # Show column names
        print(f"\n📊 Columns included:")
        for field in fieldnames:
            print(f"   • {field}")
    
    return str(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Flatten Lever jobs JSON to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full output (all fields)
  %(prog)s Lever_jobs_2026-02-14.json
  %(prog)s input.json -o output.csv
  
  # Simple output (title, company_name, location only)
  %(prog)s Lever_jobs_2026-02-14.json --simple
  %(prog)s input.json -o simple.csv --simple
  
If no output file is specified:
  - Full mode: creates CSV with same name as input
  - Simple mode: creates CSV with '_simple.csv' suffix
        """
    )
    
    parser.add_argument(
        'json_file',
        help='Path to input JSON file (combined Lever jobs)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Path to output CSV file (optional, auto-generated if not provided)'
    )
    
    parser.add_argument(
        '-s', '--simple',
        action='store_true',
        help='Output only title, company_name, and location (simple mode)'
    )
    
    args = parser.parse_args()
    
    json_to_csv(args.json_file, args.output, args.simple)


if __name__ == '__main__':
    main()