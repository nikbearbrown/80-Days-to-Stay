import json
import os
from datetime import datetime
from collections import defaultdict
import pandas as pd

def combine_and_deduplicate(input_dir='processed', output_file='startups_master.json', stats_file='startups_stats.csv'):
    """
    Combine all quarterly JSON files and deduplicate
    Generate statistics CSV
    """
    
    print("=" * 70)
    print("SEC Form D Combiner & Deduplicator")
    print("=" * 70)
    
    # Find all JSON files
    json_files = sorted([f for f in os.listdir(input_dir) if f.startswith('companies_sec_') and f.endswith('.json')])
    
    if not json_files:
        print(f"❌ No JSON files found in {input_dir}")
        return
    
    print(f"\n📂 Found {len(json_files)} quarterly JSON files")
    print(f"   From: {json_files[0]}")
    print(f"   To:   {json_files[-1]}\n")
    
    all_companies = []
    quarters_processed = []
    
    # Load all files
    for json_file in json_files:
        filepath = os.path.join(input_dir, json_file)
        with open(filepath, 'r') as f:
            data = json.load(f)
            companies = data.get('companies', [])
            quarter = data['metadata']['quarter']
            
            all_companies.extend(companies)
            quarters_processed.append(quarter)
            
            print(f"✅ Loaded {json_file}: {len(companies):,} companies")
    
    print(f"\n   Total before dedup: {len(all_companies):,} companies")
    
    # Deduplicate by accession_number (keep most recent)
    print(f"\n🔄 Deduplicating...")
    unique_companies = {}
    
    for company in all_companies:
        acc_num = company['accession_number']
        if acc_num not in unique_companies:
            unique_companies[acc_num] = company
        else:
            # Keep the one with more recent filing (lower months_since_funding)
            existing = unique_companies[acc_num]
            existing_months = existing['company_age'].get('months_since_funding')
            company_months = company['company_age'].get('months_since_funding')
            
            # Handle None values - treat None as very old (999)
            if existing_months is None:
                existing_months = 999
            if company_months is None:
                company_months = 999
            
            if company_months < existing_months:
                unique_companies[acc_num] = company
    
    final_companies = list(unique_companies.values())
    
    # Sort by funding recency (handle None values)
    final_companies.sort(key=lambda x: x['company_age'].get('months_since_funding') if x['company_age'].get('months_since_funding') is not None else 999)
    
    print(f"   After dedup: {len(final_companies):,} unique companies")
    
    # Create master JSON
    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'quarters_processed': quarters_processed,
            'total_companies': len(final_companies),
            'total_executives': sum(len(c['related_persons']) for c in final_companies),
            'date_range': {
                'earliest_quarter': quarters_processed[0] if quarters_processed else None,
                'latest_quarter': quarters_processed[-1] if quarters_processed else None
            }
        },
        'companies': final_companies
    }
    
    # Write master JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Created master JSON: {output_file}")
    print(f"   File size: {os.path.getsize(output_file) / (1024*1024):.1f} MB")
    
    # Generate statistics
    print(f"\n📊 Generating statistics CSV...")
    generate_statistics_csv(final_companies, stats_file)
    print(f"✅ Created statistics: {stats_file}")
    
    # Summary
    print(f"\n{'=' * 70}")
    print("Summary")
    print("=" * 70)
    print(f"📊 Total unique companies: {len(final_companies):,}")
    print(f"👥 Total executives: {sum(len(c['related_persons']) for c in final_companies):,}")
    print(f"📅 Quarters: {len(quarters_processed)}")

def generate_statistics_csv(companies, stats_file):
    """Generate comprehensive statistics CSV"""
    
    stats_rows = []
    
    # Overall statistics
    total = len(companies)
    over_5m = sum(1 for c in companies if c['funding']['total_amount_sold'] and c['funding']['total_amount_sold'] >= 5_000_000)
    
    stats_rows.append({
        'category': 'OVERALL',
        'subcategory': 'All Companies',
        'total_companies': total,
        'companies_over_5m': over_5m,
        'percent_over_5m': f"{(over_5m/total*100):.1f}%" if total > 0 else "0%"
    })
    
    # By State
    state_counts = defaultdict(lambda: {'total': 0, 'over_5m': 0})
    for c in companies:
        state = c['company']['address']['state']
        if state:
            state_counts[state]['total'] += 1
            amount = c['funding']['total_amount_sold']
            if amount and amount >= 5_000_000:
                state_counts[state]['over_5m'] += 1
    
    for state, counts in sorted(state_counts.items(), key=lambda x: x[1]['total'], reverse=True):
        stats_rows.append({
            'category': 'BY STATE',
            'subcategory': state,
            'total_companies': counts['total'],
            'companies_over_5m': counts['over_5m'],
            'percent_over_5m': f"{(counts['over_5m']/counts['total']*100):.1f}%" if counts['total'] > 0 else "0%"
        })
    
    # By Industry
    industry_counts = defaultdict(lambda: {'total': 0, 'over_5m': 0})
    for c in companies:
        industry = c['company']['industry']
        if industry:
            industry_counts[industry]['total'] += 1
            amount = c['funding']['total_amount_sold']
            if amount and amount >= 5_000_000:
                industry_counts[industry]['over_5m'] += 1
    
    for industry, counts in sorted(industry_counts.items(), key=lambda x: x[1]['total'], reverse=True):
        stats_rows.append({
            'category': 'BY INDUSTRY',
            'subcategory': industry,
            'total_companies': counts['total'],
            'companies_over_5m': counts['over_5m'],
            'percent_over_5m': f"{(counts['over_5m']/counts['total']*100):.1f}%" if counts['total'] > 0 else "0%"
        })
    
    # Write CSV
    df = pd.DataFrame(stats_rows)
    df.to_csv(stats_file, index=False)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Combine quarterly JSON files and generate statistics')
    parser.add_argument('--input-dir', default='processed', help='Directory with quarterly JSON files')
    parser.add_argument('--output', default='startups_master.json', help='Output master JSON file')
    parser.add_argument('--stats', default='startups_stats.csv', help='Output statistics CSV file')
    
    args = parser.parse_args()
    
    combine_and_deduplicate(args.input_dir, args.output, args.stats)