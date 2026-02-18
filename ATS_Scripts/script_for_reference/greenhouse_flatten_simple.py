#!/usr/bin/env python3
"""
Flatten Greenhouse jobs JSON to simple CSV with title, company_name, location.
"""

import argparse
import json
import csv
import sys
from pathlib import Path
from typing import List, Dict, Any


def flatten_job_simple(job: Dict[str, Any]) -> Dict[str, str]:
    """
    Flatten a job to just title, company_name, and location.
    """
    # Company name (prefer our metadata, fallback to job field)
    company_name = job.get('_company_name', job.get('company_name', ''))
    
    # Location (handle nested object)
    location = job.get('location', {})
    if isinstance(location, dict):
        location_str = location.get('name', '')
    else:
        location_str = str(location) if location else ''
    
    return {
        'title': job.get('title', ''),
        'company_name': company_name,
        'location': location_str
    }


def json_to_simple_csv(json_file: str, output_file: str = None) -> str:
    """
    Convert Greenhouse jobs JSON to simple CSV with title, company_name, location.
    
    Args:
        json_file: Path to input JSON file
        output_file: Path to output CSV file (optional, auto-generated if not provided)
    
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
    print(f"🔄 Extracting title, company, and location...\n")
    
    # Flatten all jobs
    flattened_jobs = []
    for i, job in enumerate(jobs, 1):
        try:
            flattened_jobs.append(flatten_job_simple(job))
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
        # Remove .json extension and add _simple.csv
        base_name = json_path.stem
        output_file = json_path.parent / f"{base_name}_simple.csv"
    else:
        output_file = Path(output_file)
    
    # Write to CSV
    print(f"\n💾 Writing to {output_file}...")
    
    fieldnames = ['title', 'company_name', 'location']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_jobs)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"📝 Jobs written: {len(flattened_jobs):,}")
    print(f"📋 Columns: 3 (title, company_name, location)")
    print(f"✅ Output file: {output_file}")
    print(f"📦 File size: {output_file.stat().st_size / 1024:.2f} KB")
    
    # Show first few rows as preview
    print(f"\n👀 Preview (first 5 rows):")
    print(f"{'Title':<50} {'Company':<40} {'Location':<30}")
    print("-" * 120)
    for job in flattened_jobs[:5]:
        title = job['title'][:47] + '...' if len(job['title']) > 50 else job['title']
        company = job['company_name'][:37] + '...' if len(job['company_name']) > 40 else job['company_name']
        location = job['location'][:27] + '...' if len(job['location']) > 30 else job['location']
        print(f"{title:<50} {company:<40} {location:<30}")
    
    return str(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Flatten Greenhouse jobs JSON to simple CSV (title, company_name, location)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s Greenhouse_jobs_2026-02-14.json
  %(prog)s input.json -o simple_jobs.csv
  %(prog)s data/jobs.json --output results/simple.csv
  
If no output file is specified, will create CSV with '_simple.csv' suffix.
Output format:
  title, company_name, location
        """
    )
    
    parser.add_argument(
        'json_file',
        help='Path to input JSON file (combined Greenhouse jobs)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Path to output CSV file (optional, auto-generated if not provided)'
    )
    
    args = parser.parse_args()
    
    json_to_simple_csv(args.json_file, args.output)


if __name__ == '__main__':
    main()