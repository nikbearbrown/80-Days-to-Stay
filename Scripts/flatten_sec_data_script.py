import json
import csv
from datetime import datetime

def load_json(filename):
    """Load JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def flatten_company_data(company_data, url_data_dict):
    """Flatten company data into employment-focused fields"""
    
    accession = company_data.get('accession_number', '')
    company = company_data.get('company', {})
    funding = company_data.get('funding', {})
    company_age = company_data.get('company_age', {})
    related_persons = company_data.get('related_persons', [])
    
    # Get URL data if available
    url_info = url_data_dict.get(accession, {})
    domains = url_info.get('domains', {})
    
    # Build executive/director lists
    executives = []
    directors = []
    
    for person in related_persons:
        name = person.get('name', '')
        relationships = person.get('relationships', [])
        
        # Skip if name is None or empty
        if not name:
            continue
        
        if 'Executive Officer' in relationships:
            executives.append(name)
        if 'Director' in relationships and 'Executive Officer' not in relationships:
            directors.append(name)
    
    # Create flattened row
    row = {
        # Company basics
        'company_name': company.get('name', ''),
        'industry': company.get('industry', ''),
        'website': domains.get('primary', ''),
        
        # Location
        'city': company.get('address', {}).get('city', ''),
        'state': company.get('address', {}).get('state', ''),
        'zip_code': company.get('address', {}).get('zip', ''),
        'phone': company.get('address', {}).get('phone', ''),
        
        # Company maturity
        'year_incorporated': company.get('year_incorporated', ''),
        'company_age_years': company_age.get('years_since_incorporation', ''),
        
        # Funding info (shows growth/stability)
        'funding_stage': funding.get('stage_estimate', ''),
        'recent_funding_amount': funding.get('total_amount_sold', ''),
        'total_offering_amount': funding.get('total_offering_amount', ''),
        'number_of_investors': funding.get('number_of_investors', ''),
        'date_of_first_sale': funding.get('date_of_first_sale', ''),
        'funding_recency': company_age.get('funding_recency', ''),
        'months_since_funding': company_age.get('months_since_funding', ''),
        
        # Leadership (for research/networking)
        'executive_officers': '; '.join(executives[:5]),  # Limit to 5 to keep readable
        'board_directors': '; '.join(directors[:5]),
        
        # Reference info
        'accession_number': accession,
    }
    
    return row

def main():
    # Load data
    print("Loading SEC company data...")
    companies_data = load_json('sec_companies_targets.json')
    
    print("Loading verified URLs...")
    urls_data = load_json('sec_companies_targets_unique_verified_good.json')
    
    # Handle different JSON structures for URLs
    if isinstance(urls_data, dict):
        # Check for common data wrapper keys
        if 'data' in urls_data:
            urls = urls_data['data']
        elif 'companies' in urls_data:
            urls = urls_data['companies']
        elif 'results' in urls_data:
            urls = urls_data['results']
        else:
            # Assume dict values are the records
            urls = list(urls_data.values())
    elif isinstance(urls_data, list):
        urls = urls_data
    else:
        print(f"Unexpected URL data format: {type(urls_data)}")
        urls = []
    
    print(f"Found {len(urls)} verified URL records")
    
    # Handle companies data similarly
    if isinstance(companies_data, dict):
        # Check for common data wrapper keys
        if 'data' in companies_data:
            companies = companies_data['data']
        elif 'companies' in companies_data:
            companies = companies_data['companies']
        elif 'results' in companies_data:
            companies = companies_data['results']
        else:
            # Assume dict values are the records
            print("Dict structure detected - extracting values...")
            companies = list(companies_data.values())
    elif isinstance(companies_data, list):
        companies = companies_data
    else:
        print(f"Unexpected companies data format: {type(companies_data)}")
        companies = []
    
    # Flatten if nested lists
    if companies and isinstance(companies[0], list):
        print("Detected nested list structure, flattening...")
        flattened = []
        for item in companies:
            if isinstance(item, list):
                flattened.extend(item)
            else:
                flattened.append(item)
        companies = flattened
    
    print(f"Found {len(companies)} company records")
    
    # Debug: check first company structure
    if companies:
        print(f"First company type: {type(companies[0])}")
        if isinstance(companies[0], dict):
            print(f"Sample company keys: {list(companies[0].keys())[:8]}")
    
    # Create lookup dictionary for URLs by accession number
    url_dict = {}
    for item in urls:
        if isinstance(item, dict) and 'accession_number' in item:
            url_dict[item['accession_number']] = item
    
    print(f"Created URL lookup with {len(url_dict)} entries")
    
    print(f"Processing {len(companies)} companies...")
    
    # Flatten data
    flattened_data = []
    companies_with_urls = 0
    
    for company in companies:
        row = flatten_company_data(company, url_dict)
        flattened_data.append(row)
        
        if row['website']:
            companies_with_urls += 1
    
    # Write to CSV
    output_filename = 'student_employment_targets.csv'
    
    if flattened_data:
        fieldnames = flattened_data[0].keys()
        
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_data)
        
        print(f"\n✓ Successfully created {output_filename}")
        print(f"  Total companies: {len(flattened_data)}")
        print(f"  Companies with verified websites: {companies_with_urls}")
        print(f"  Companies without websites: {len(flattened_data) - companies_with_urls}")
    else:
        print("No data to write!")

if __name__ == "__main__":
    main()
