#!/usr/bin/env python3
"""
Flatten Greenhouse jobs JSON to CSV format.
"""

import argparse
import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def flatten_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a job dictionary, handling nested objects.
    """
    flattened = {}
    
    # Direct fields
    flattened['job_id'] = job.get('id', '')
    flattened['internal_job_id'] = job.get('internal_job_id', '')
    flattened['requisition_id'] = job.get('requisition_id', '')
    flattened['title'] = job.get('title', '')
    flattened['absolute_url'] = job.get('absolute_url', '')
    flattened['language'] = job.get('language', '')
    flattened['education'] = job.get('education', '')
    
    # Date fields
    flattened['first_published'] = job.get('first_published', '')
    flattened['updated_at'] = job.get('updated_at', '')
    
    # Company fields (from metadata we added)
    flattened['company_name'] = job.get('_company_name', job.get('company_name', ''))
    flattened['company_slug'] = job.get('_company_slug', '')
    flattened['company_greenhouse_url'] = job.get('_company_greenhouse_url', '')
    
    # Location (nested object)
    location = job.get('location', {})
    if isinstance(location, dict):
        flattened['location'] = location.get('name', '')
    else:
        flattened['location'] = str(location) if location else ''
    
    # Metadata (nested, could be None)
    metadata = job.get('metadata')
    flattened['metadata'] = json.dumps(metadata) if metadata else ''
    
    # Data compliance (array - just flag if exists)
    data_compliance = job.get('data_compliance', [])
    flattened['has_gdpr_compliance'] = any(
        dc.get('type') == 'gdpr' for dc in data_compliance if isinstance(dc, dict)
    )
    
    return flattened


def json_to_csv(json_file: str, output_file: str = None) -> str:
    """
    Convert Greenhouse jobs JSON to CSV.
    
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
    print(f"🔄 Flattening data...\n")
    
    # Flatten all jobs
    flattened_jobs = []
    for i, job in enumerate(jobs, 1):
        try:
            flattened_jobs.append(flatten_job(job))
        except Exception as e:
            print(f"  ⚠️  Error flattening job {i}: {e}")
            continue
        
        if i % 1000 == 0:
            print(f"  Processed {i:,} jobs...")
    
    if not flattened_jobs:
        print("❌ Error: No jobs could be flattened")
        sys.exit(1)
    
    # Generate output filename if not provided
    if output_file is None:
        # Remove .json extension and add .csv
        base_name = json_path.stem
        output_file = json_path.parent / f"{base_name}.csv"
    else:
        output_file = Path(output_file)
    
    # Write to CSV
    print(f"\n💾 Writing to {output_file}...")
    
    # Get all fieldnames (in case some jobs have different fields)
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
    print(f"📦 File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Show column names
    print(f"\n📊 Columns included:")
    for field in fieldnames:
        print(f"   • {field}")
    
    return str(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Flatten Greenhouse jobs JSON to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s Greenhouse_jobs_2026-02-14.json
  %(prog)s input.json -o output.csv
  %(prog)s data/jobs.json --output results/flattened.csv
  
If no output file is specified, will create CSV with same name as input file.
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
    
    json_to_csv(args.json_file, args.output)


if __name__ == '__main__':
    main()