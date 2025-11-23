import pandas as pd
import json
import os
import sys
import argparse
from datetime import datetime

# Required TSV files
REQUIRED_FILES = [
    'FORMDSUBMISSION.tsv',
    'ISSUERS.tsv',
    'OFFERING.tsv',
    'RELATEDPERSONS.tsv'
]

def check_required_files(directory):
    """Check if all required TSV files exist in the directory"""
    missing_files = []
    found_files = []
    
    for filename in REQUIRED_FILES:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            found_files.append(filename)
        else:
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ Missing required files in '{directory}':")
        for f in missing_files:
            print(f"   - {f}")
        print(f"\n✅ Found files:")
        for f in found_files:
            print(f"   - {f}")
        print(f"\nExpected SEC Form D TSV files. Did you extract the ZIP file?")
        return False
    
    print(f"✅ All required files found in '{directory}'")
    return True

def create_startups_json(directory='.'):
    """Parse SEC Form D data and create MongoDB-ready JSON"""
    
    # Convert to absolute path
    directory = os.path.abspath(directory)
    
    print(f"\n🔍 Looking for TSV files in: {directory}\n")
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"❌ Directory does not exist: {directory}")
        return None
    
    # Check for required files
    if not check_required_files(directory):
        return None
    
    print(f"\n📂 Loading TSV files...")
    
    try:
        # Load the core files with correct column names
        submissions = pd.read_csv(
            os.path.join(directory, 'FORMDSUBMISSION.tsv'), 
            sep='\t', 
            low_memory=False
        )
        issuers = pd.read_csv(
            os.path.join(directory, 'ISSUERS.tsv'), 
            sep='\t', 
            low_memory=False
        )
        offerings = pd.read_csv(
            os.path.join(directory, 'OFFERING.tsv'), 
            sep='\t', 
            low_memory=False
        )
        people = pd.read_csv(
            os.path.join(directory, 'RELATEDPERSONS.tsv'), 
            sep='\t', 
            low_memory=False
        )
        
        print(f"   Loaded {len(submissions):,} submissions")
        print(f"   Loaded {len(issuers):,} issuers")
        print(f"   Loaded {len(offerings):,} offerings")
        print(f"   Loaded {len(people):,} related persons")
        
    except Exception as e:
        print(f"\n❌ Error loading TSV files: {e}")
        return None
    
    # Filter criteria
    TARGET_STATES = ['MA', 'CA', 'NY']
    MIN_FUNDING = 5_000_000
    TARGET_INDUSTRIES = [
        'Biotechnology',
        'Pharmaceuticals',
        'Pharmaceutical',
        'Medical Devices and Equipment',
        'Other Health Care',
        'Computers and Computer Equipment',
        'Computer Software and Services',
        'Internet and Information Services'
    ]
    
    print(f"\n🔎 Filtering startups...")
    print(f"   States: {', '.join(TARGET_STATES)}")
    print(f"   Min funding: ${MIN_FUNDING:,}")
    print(f"   Industries: {len(TARGET_INDUSTRIES)} target industries")
    
    # Step 1: Filter offerings for funded companies
    try:
        # Convert amount to numeric, handling any non-numeric values
        offerings['TOTALAMOUNTSOLD'] = pd.to_numeric(offerings['TOTALAMOUNTSOLD'], errors='coerce')
        
        funded = offerings[offerings['TOTALAMOUNTSOLD'] >= MIN_FUNDING].copy()
        
        # Filter by industry
        funded = funded[funded['INDUSTRYGROUPTYPE'].isin(TARGET_INDUSTRIES)].copy()
        
        print(f"\n   ✓ Found {len(funded):,} companies with ${MIN_FUNDING:,}+ funding in target industries")
        
    except Exception as e:
        print(f"\n❌ Error filtering offerings: {e}")
        return None
    
    # Step 2: Join with issuers and filter for target states
    try:
        funded_issuers = funded.merge(issuers, on='ACCESSIONNUMBER', how='inner')
        target_companies = funded_issuers[
            funded_issuers['STATEORCOUNTRY'].isin(TARGET_STATES)
        ].copy()
        
        print(f"   ✓ Found {len(target_companies):,} companies in target states")
        
    except Exception as e:
        print(f"\n❌ Error joining with issuers: {e}")
        return None
    
    # Step 3: Join with submission info
    try:
        target_companies = target_companies.merge(
            submissions[['ACCESSIONNUMBER', 'FILING_DATE', 'SUBMISSIONTYPE']], 
            on='ACCESSIONNUMBER',
            how='left'
        )
    except Exception as e:
        print(f"⚠️  Warning: Could not join submission info: {e}")
    
    # Step 4: Build the JSON structure
    print(f"\n📝 Building JSON documents...")
    startups = []
    
    for idx, (_, row) in enumerate(target_companies.iterrows(), 1):
        accession = row['ACCESSIONNUMBER']
        
        if idx % 10 == 0:
            print(f"   Processing {idx}/{len(target_companies)}...", end='\r')
        
        # Get all related persons for this company
        company_people = people[people['ACCESSIONNUMBER'] == accession]
        
        # Build related persons array
        related_persons = []
        for _, person in company_people.iterrows():
            # Combine first, middle, last name
            name_parts = [
                clean_value(person.get('FIRSTNAME')),
                clean_value(person.get('MIDDLENAME')),
                clean_value(person.get('LASTNAME'))
            ]
            full_name = ' '.join([p for p in name_parts if p])
            
            # Combine relationships
            relationships = []
            for rel_col in ['RELATIONSHIP_1', 'RELATIONSHIP_2', 'RELATIONSHIP_3']:
                rel = clean_value(person.get(rel_col))
                if rel:
                    relationships.append(rel)
            
            person_data = {
                'name': full_name if full_name else None,
                'first_name': clean_value(person.get('FIRSTNAME')),
                'middle_name': clean_value(person.get('MIDDLENAME')),
                'last_name': clean_value(person.get('LASTNAME')),
                'relationships': relationships,
                'city': clean_value(person.get('CITY')),
                'state': clean_value(person.get('STATEORCOUNTRY'))
            }
            
            related_persons.append(person_data)
        
        # Build the startup document
        startup = {
            'accession_number': accession,
            'company': {
                'name': clean_value(row.get('ENTITYNAME')),
                'address': {
                    'street1': clean_value(row.get('STREET1')),
                    'street2': clean_value(row.get('STREET2')),
                    'city': clean_value(row.get('CITY')),
                    'state': clean_value(row.get('STATEORCOUNTRY')),
                    'zip': clean_value(row.get('ZIPCODE')),
                    'phone': clean_value(row.get('ISSUERPHONENUMBER'))
                },
                'entity_type': clean_value(row.get('ENTITYTYPE')),
                'year_incorporated': clean_int(row.get('YEAROFINC_VALUE_ENTERED')),
                'industry': clean_value(row.get('INDUSTRYGROUPTYPE'))
            },
            'funding': {
                'total_offering_amount': clean_float(row.get('TOTALOFFERINGAMOUNT')),
                'total_amount_sold': clean_float(row.get('TOTALAMOUNTSOLD')),
                'total_remaining': clean_float(row.get('TOTALREMAINING')),
                'number_of_investors': clean_int(row.get('TOTALNUMBERALREADYINVESTED')),
                'date_of_first_sale': clean_value(row.get('SALE_DATE'))
            },
            'filing': {
                'date_filed': clean_value(row.get('FILING_DATE')),
                'submission_type': clean_value(row.get('SUBMISSIONTYPE')),
                'is_amendment': clean_value(row.get('ISAMENDMENT')) == 'Y'
            },
            'related_persons': related_persons,
            'metadata': {
                'added_to_database': datetime.now().isoformat(),
                'source_directory': directory,
                'prediction_scores': {
                    'international_hiring': None,
                    'recent_grad_hiring': None
                }
            }
        }
        
        startups.append(startup)
    
    print(f"   Processing {len(target_companies)}/{len(target_companies)}... Done!")
    
    # Create final JSON structure
    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'source_directory': directory,
            'filters': {
                'states': TARGET_STATES,
                'min_funding': MIN_FUNDING,
                'industries': TARGET_INDUSTRIES
            },
            'total_startups': len(startups),
            'total_executives': sum(len(s['related_persons']) for s in startups)
        },
        'startups': startups
    }
    
    # Write to file
    output_file = 'startups.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ SUCCESS!")
    print(f"   Created: {output_file}")
    print(f"   Startups: {len(startups):,}")
    print(f"   Executives/Directors: {sum(len(s['related_persons']) for s in startups):,}")
    
    # Print sample
    if startups:
        print(f"\n📄 Sample startup:")
        sample = startups[0]
        print(f"   Company: {sample['company']['name']}")
        print(f"   Location: {sample['company']['address']['city']}, {sample['company']['address']['state']}")
        print(f"   Funding: ${sample['funding']['total_amount_sold']:,.0f}")
        print(f"   Industry: {sample['company']['industry']}")
        print(f"   Executives: {len(sample['related_persons'])}")
    
    return output

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

def main():
    parser = argparse.ArgumentParser(
        description='Parse SEC Form D data into MongoDB-ready JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use current directory
  python3 sec_form_d.py
  
  # Specify a directory
  python3 sec_form_d.py /path/to/2025Q1_d
  python3 sec_form_d.py ./2025Q1_d
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory containing TSV files (default: current directory)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SEC Form D → MongoDB JSON Converter")
    print("=" * 60)
    
    result = create_startups_json(args.directory)
    
    if result:
        print("\n" + "=" * 60)
        print("Next steps:")
        print("  1. Review startups.json")
        print("  2. Import to MongoDB:")
        print("     mongoimport --db startups --collection companies \\")
        print("                 --file startups.json --jsonArray")
        print("=" * 60)
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()