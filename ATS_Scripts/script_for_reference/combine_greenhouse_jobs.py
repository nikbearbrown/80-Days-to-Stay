#!/usr/bin/env python3
"""
Combine all Greenhouse job JSON files into a single dated file.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def combine_greenhouse_jobs(input_dir: str = "greenhouse_jobs", output_dir: str = ".") -> str:
    """
    Combine all jobs.json files from company subdirectories into a single file.
    
    Returns:
        Path to the combined output file
    """
    base_path = Path(input_dir)
    
    if not base_path.exists():
        print(f"❌ Error: Directory '{input_dir}' not found")
        sys.exit(1)
    
    # Get all company subdirectories
    company_dirs = [d for d in base_path.iterdir() if d.is_dir()]
    
    if not company_dirs:
        print(f"❌ Error: No company directories found in '{input_dir}'")
        sys.exit(1)
    
    print(f"🔍 Found {len(company_dirs)} company directories")
    print(f"📦 Combining job data...\n")
    
    all_jobs = []
    companies_processed = 0
    companies_with_jobs = 0
    total_jobs = 0
    
    for company_dir in sorted(company_dirs):
        jobs_file = company_dir / "jobs.json"
        metadata_file = company_dir / "metadata.json"
        
        if not jobs_file.exists():
            continue
        
        try:
            # Load jobs data
            with open(jobs_file, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            
            # Load metadata for company info
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            jobs = jobs_data.get('jobs', [])
            
            # Add company context to each job
            company_name = metadata.get('original_name', company_dir.name)
            company_url = metadata.get('url', '')
            
            for job in jobs:
                job['_company_name'] = company_name
                job['_company_greenhouse_url'] = company_url
                job['_company_slug'] = company_dir.name
                all_jobs.append(job)
            
            companies_processed += 1
            if len(jobs) > 0:
                companies_with_jobs += 1
                total_jobs += len(jobs)
                print(f"  ✓ {company_name}: {len(jobs)} jobs")
        
        except Exception as e:
            print(f"  ⚠️  Error processing {company_dir.name}: {e}")
            continue
    
    # Create output filename with today's date
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = Path(output_dir) / f"Greenhouse_jobs_{today}.json"
    
    # Create combined output structure
    output_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_companies": companies_processed,
            "companies_with_jobs": companies_with_jobs,
            "total_jobs": total_jobs,
            "source_directory": input_dir
        },
        "jobs": all_jobs
    }
    
    # Write combined file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"📊 Companies processed: {companies_processed}")
    print(f"💼 Companies with jobs: {companies_with_jobs}")
    print(f"🎯 Total jobs collected: {total_jobs:,}")
    print(f"\n✅ Combined file created: {output_file}")
    print(f"📦 File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    return str(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Combine all Greenhouse job JSON files into a single dated file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s -i greenhouse_jobs -o combined_data
  %(prog)s --input-dir ./data/greenhouse --output-dir ./exports
  
Output file will be named: Greenhouse_jobs_YYYY-MM-DD.json
        """
    )
    
    parser.add_argument(
        '-i', '--input-dir',
        default='greenhouse_jobs',
        help='Input directory containing company subdirectories (default: greenhouse_jobs)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default='.',
        help='Output directory for combined file (default: current directory)'
    )
    
    args = parser.parse_args()
    
    combine_greenhouse_jobs(args.input_dir, args.output_dir)


if __name__ == '__main__':
    main()