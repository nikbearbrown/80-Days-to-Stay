import pandas as pd
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def process_single_quarter(quarter_dir, output_dir='processed'):
    """
    Process a single quarterly folder and save as JSON
    
    Args:
        quarter_dir: Path to quarterly folder (e.g., '2023Q2_d')
        output_dir: Directory to save processed JSON files
    """
    
    quarter_name = os.path.basename(quarter_dir)
    
    # Check for required files
    required_files = ['FORMDSUBMISSION.tsv', 'ISSUERS.tsv', 'OFFERING.tsv', 'RELATEDPERSONS.tsv']
    missing = [f for f in required_files if not os.path.exists(os.path.join(quarter_dir, f))]
    
    if missing:
        print(f"⏭️  {quarter_name:15s} - Missing files: {', '.join(missing)}")
        return None
    
    try:
        # Load data
        submissions = pd.read_csv(os.path.join(quarter_dir, 'FORMDSUBMISSION.tsv'), sep='\t', low_memory=False)
        issuers = pd.read_csv(os.path.join(quarter_dir, 'ISSUERS.tsv'), sep='\t', low_memory=False)
        offerings = pd.read_csv(os.path.join(quarter_dir, 'OFFERING.tsv'), sep='\t', low_memory=False)
        people = pd.read_csv(os.path.join(quarter_dir, 'RELATEDPERSONS.tsv'), sep='\t', low_memory=False)
        
        # Join everything - NO FILTERING
        all_companies = offerings.merge(issuers, on='ACCESSIONNUMBER', how='inner')
        all_companies = all_companies.merge(
            submissions[['ACCESSIONNUMBER', 'FILING_DATE', 'SUBMISSIONTYPE']], 
            on='ACCESSIONNUMBER',
            how='left'
        )
        
        # Convert amount to numeric
        all_companies['TOTALAMOUNTSOLD'] = pd.to_numeric(all_companies['TOTALAMOUNTSOLD'], errors='coerce')
        
        # Process each company
        startups = []
        for _, row in all_companies.iterrows():
            accession = row['ACCESSIONNUMBER']
            company_people = people[people['ACCESSIONNUMBER'] == accession]
            
            # Build related persons
            related_persons = []
            for _, person in company_people.iterrows():
                name_parts = [
                    clean_value(person.get('FIRSTNAME')),
                    clean_value(person.get('MIDDLENAME')),
                    clean_value(person.get('LASTNAME'))
                ]
                full_name = ' '.join([p for p in name_parts if p])
                
                relationships = []
                for rel_col in ['RELATIONSHIP_1', 'RELATIONSHIP_2', 'RELATIONSHIP_3']:
                    rel = clean_value(person.get(rel_col))
                    if rel:
                        relationships.append(rel)
                
                related_persons.append({
                    'name': full_name if full_name else None,
                    'first_name': clean_value(person.get('FIRSTNAME')),
                    'middle_name': clean_value(person.get('MIDDLENAME')),
                    'last_name': clean_value(person.get('LASTNAME')),
                    'relationships': relationships,
                    'city': clean_value(person.get('CITY')),
                    'state': clean_value(person.get('STATEORCOUNTRY'))
                })
            
            # Calculate company age and funding recency
            year_inc = clean_int(row.get('YEAROFINC_VALUE_ENTERED'))
            current_year = datetime.now().year
            years_since_inc = (current_year - year_inc) if year_inc else None
            
            # Parse filing date and calculate recency
            filing_date = clean_value(row.get('FILING_DATE'))
            months_since_funding = None
            funding_recency = None
            
            if filing_date:
                try:
                    for fmt in ['%d-%b-%Y', '%Y-%m-%d', '%m/%d/%Y']:
                        try:
                            file_dt = datetime.strptime(filing_date, fmt)
                            months_since_funding = (datetime.now() - file_dt).days // 30
                            
                            if months_since_funding < 6:
                                funding_recency = "very_recent"
                            elif months_since_funding < 12:
                                funding_recency = "recent"
                            elif months_since_funding < 24:
                                funding_recency = "moderate"
                            else:
                                funding_recency = "older"
                            break
                        except:
                            continue
                except:
                    pass
            
            # Estimate stage based on amount
            amount_sold = clean_float(row.get('TOTALAMOUNTSOLD'))
            stage_estimate = None
            if amount_sold:
                if amount_sold < 2_000_000:
                    stage_estimate = "Pre-Seed"
                elif amount_sold < 5_000_000:
                    stage_estimate = "Seed"
                elif amount_sold < 15_000_000:
                    stage_estimate = "Series A"
                elif amount_sold < 40_000_000:
                    stage_estimate = "Series B"
                elif amount_sold < 100_000_000:
                    stage_estimate = "Series C"
                else:
                    stage_estimate = "Series D+"
            
            state = clean_value(row.get('STATEORCOUNTRY'))
            industry = clean_value(row.get('INDUSTRYGROUPTYPE'))
            
            startup = {
                'accession_number': accession,
                'company': {
                    'name': clean_value(row.get('ENTITYNAME')),
                    'address': {
                        'street1': clean_value(row.get('STREET1')),
                        'street2': clean_value(row.get('STREET2')),
                        'city': clean_value(row.get('CITY')),
                        'state': state,
                        'zip': clean_value(row.get('ZIPCODE')),
                        'phone': clean_value(row.get('ISSUERPHONENUMBER'))
                    },
                    'entity_type': clean_value(row.get('ENTITYTYPE')),
                    'year_incorporated': year_inc,
                    'industry': industry
                },
                'funding': {
                    'total_offering_amount': clean_float(row.get('TOTALOFFERINGAMOUNT')),
                    'total_amount_sold': amount_sold,
                    'total_remaining': clean_float(row.get('TOTALREMAINING')),
                    'number_of_investors': clean_int(row.get('TOTALNUMBERALREADYINVESTED')),
                    'date_of_first_sale': clean_value(row.get('SALE_DATE')),
                    'stage_estimate': stage_estimate
                },
                'filing': {
                    'date_filed': filing_date,
                    'submission_type': clean_value(row.get('SUBMISSIONTYPE')),
                    'quarter': quarter_name
                },
                'company_age': {
                    'years_since_incorporation': years_since_inc,
                    'months_since_funding': months_since_funding,
                    'funding_recency': funding_recency
                },
                'related_persons': related_persons,
                'metadata': {
                    'source_quarter': quarter_name,
                    'processed_date': datetime.now().isoformat(),
                    'prediction_scores': {
                        'international_hiring': None,
                        'recent_grad_hiring': None
                    }
                }
            }
            
            startups.append(startup)
        
        # Create output
        output = {
            'metadata': {
                'quarter': quarter_name,
                'generated_at': datetime.now().isoformat(),
                'total_companies': len(startups),
                'total_executives': sum(len(s['related_persons']) for s in startups)
            },
            'companies': startups
        }
        
        # Save to file
        Path(output_dir).mkdir(exist_ok=True)
        output_file = os.path.join(output_dir, f'companies_sec_{quarter_name}.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {quarter_name:15s} - {len(startups):4d} companies → {os.path.basename(output_file)}")
        
        return output
        
    except Exception as e:
        print(f"❌ {quarter_name:15s} - Error: {e}")
        return None

def process_all_quarters_individually(data_dir='.', output_dir='processed'):
    """Process all quarters and save each as separate JSON"""
    
    print("=" * 70)
    print("SEC Form D Quarter-by-Quarter Processor")
    print("=" * 70)
    
    # Find all quarterly directories
    quarter_dirs = []
    for item in sorted(os.listdir(data_dir)):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and ('Q' in item or 'q' in item):
            quarter_dirs.append(item_path)
    
    if not quarter_dirs:
        print(f"❌ No quarterly directories found in {os.path.abspath(data_dir)}")
        return
    
    print(f"\n📂 Found {len(quarter_dirs)} quarterly directories")
    print(f"📁 Output directory: {os.path.abspath(output_dir)}\n")
    
    processed = []
    failed = []
    
    for quarter_dir in quarter_dirs:
        result = process_single_quarter(quarter_dir, output_dir)
        if result:
            processed.append(os.path.basename(quarter_dir))
        else:
            failed.append(os.path.basename(quarter_dir))
    
    # Summary
    print(f"\n{'=' * 70}")
    print("Summary")
    print("=" * 70)
    print(f"✅ Processed: {len(processed)} quarters")
    print(f"❌ Failed: {len(failed)} quarters")
    print(f"📁 JSON files saved to: {os.path.abspath(output_dir)}/")
    
    if failed:
        print(f"\n⚠️  Failed quarters: {', '.join(failed)}")

def clean_value(val):
    """Clean pandas values - convert NaN to None"""
    if pd.isna(val):
        return None
    return str(val).strip() if val else None

def clean_float(val):
    """Convert to float, handle NaN"""
    if pd.isna(val):
        return None
    try:
        return float(val)
    except:
        return None

def clean_int(val):
    """Convert to int, handle NaN"""
    if pd.isna(val):
        return None
    try:
        return int(float(val))
    except:
        return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Process SEC Form D quarters individually')
    parser.add_argument('--output-dir', default='processed', help='Output directory for JSON files')
    
    args = parser.parse_args()
    
    process_all_quarters_individually('.', args.output_dir)