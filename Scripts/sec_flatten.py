import json
import csv
import sys
from typing import List, Dict, Any

def extract_funding_amount(company_data: Dict[str, Any]) -> float:
    """Extract total offering amount from funding object."""
    try:
        funding = company_data.get('funding', {})
        if 'total_offering_amount' in funding:
            amount = funding['total_offering_amount']
            if amount and isinstance(amount, (int, float)):
                return float(amount)
        if 'total_amount_sold' in funding:
            amount = funding['total_amount_sold']
            if amount and isinstance(amount, (int, float)):
                return float(amount)
        return 0.0
    except (ValueError, TypeError):
        return 0.0

def flatten_company(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract essential fields from nested company data."""
    company = company_data.get('company', {})
    address = company.get('address', {})
    funding = company_data.get('funding', {})
    filing = company_data.get('filing', {})
    
    # Get primary executive/contact
    related_persons = company_data.get('related_persons', [])
    primary_contact = ""
    if related_persons:
        first_person = related_persons[0]
        primary_contact = first_person.get('name', '')
    
    funding_amount = extract_funding_amount(company_data)
    
    return {
        'Company_Name': company.get('name', ''),
        'Street_Address': address.get('street1', ''),
        'City': address.get('city', ''),
        'State': address.get('state', ''),
        'Zip': address.get('zip', ''),
        'Phone': address.get('phone', ''),
        'Industry': company.get('industry', ''),
        'Entity_Type': company.get('entity_type', ''),
        'Year_Incorporated': company.get('year_incorporated', ''),
        'Funding_Amount': funding_amount,
        'Funding_Formatted': f"${funding_amount:,.0f}" if funding_amount > 0 else "$0",
        'Amount_Sold': funding.get('total_amount_sold', 0),
        'Investors': funding.get('number_of_investors', 0),
        'Filing_Date': filing.get('date_filed', ''),
        'Primary_Contact': primary_contact,
        'Accession_Number': company_data.get('accession_number', '')
    }

def convert_to_csv(input_file: str, output_file: str, top_n: int = 100):
    """Convert JSON to CSV with top N companies by funding."""
    
    print(f"Loading companies from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both formats
    if isinstance(data, dict) and 'companies' in data:
        companies = data['companies']
    else:
        companies = data
    
    print(f"Found {len(companies):,} companies")
    
    # Flatten all companies
    flattened = [flatten_company(c) for c in companies]
    
    # Sort by funding amount (descending)
    flattened.sort(key=lambda x: x['Funding_Amount'], reverse=True)
    
    # Take top N
    top_companies = flattened[:top_n] if top_n else flattened
    
    print(f"Exporting top {len(top_companies):,} companies to {output_file}...")
    
    # Write to CSV
    fieldnames = [
        'Company_Name',
        'Industry',
        'Funding_Formatted',
        'Funding_Amount',
        'City',
        'State',
        'Phone',
        'Street_Address',
        'Zip',
        'Entity_Type',
        'Year_Incorporated',
        'Amount_Sold',
        'Investors',
        'Filing_Date',
        'Primary_Contact',
        'Accession_Number'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(top_companies)
    
    # Print summary
    print("\n" + "="*60)
    print("CSV EXPORT SUMMARY")
    print("="*60)
    print(f"Total companies exported: {len(top_companies):,}")
    print(f"Output file: {output_file}")
    
    print("\n" + "="*60)
    print("TOP 5 BY FUNDING")
    print("="*60)
    for i, company in enumerate(top_companies[:5], 1):
        print(f"{i}. {company['Company_Name']}")
        print(f"   {company['City']}, {company['State']} - {company['Funding_Formatted']}")
        print(f"   Industry: {company['Industry']}")
    
    print("\n" + "="*60)
    print("FUNDING DISTRIBUTION")
    print("="*60)
    
    # Calculate distribution
    ranges = {
        '$1M-$5M': 0,
        '$5M-$10M': 0,
        '$10M-$25M': 0,
        '$25M-$50M': 0,
        '$50M+': 0
    }
    
    for company in top_companies:
        amount = company['Funding_Amount']
        if amount < 5_000_000:
            ranges['$1M-$5M'] += 1
        elif amount < 10_000_000:
            ranges['$5M-$10M'] += 1
        elif amount < 25_000_000:
            ranges['$10M-$25M'] += 1
        elif amount < 50_000_000:
            ranges['$25M-$50M'] += 1
        else:
            ranges['$50M+'] += 1
    
    for range_name, count in ranges.items():
        if count > 0:
            pct = count / len(top_companies) * 100
            print(f"{range_name:>12}: {count:>4} ({pct:>4.1f}%)")
    
    print("\n✓ CSV export complete!")

def main():
    """Main function with command-line support."""
    input_file = 'sec_companies_targets.json'
    output_file = 'sec_companies_top100.csv'
    top_n = 100
    
    # Parse arguments
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    if len(sys.argv) >= 4:
        try:
            top_n = int(sys.argv[3])
        except ValueError:
            print("Warning: Invalid number, using default top 100")
            top_n = 100
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python flatten_to_csv.py [input_file] [output_file] [top_n]")
        print("\nDefaults:")
        print("  input_file:  sec_companies_targets.json")
        print("  output_file: sec_companies_top100.csv")
        print("  top_n:       100 (use 0 for all companies)")
        print("\nExamples:")
        print("  python flatten_to_csv.py                          # Top 100")
        print("  python flatten_to_csv.py targets.json out.csv 50  # Top 50")
        print("  python flatten_to_csv.py targets.json all.csv 0   # All companies")
        sys.exit(0)
    
    try:
        convert_to_csv(input_file, output_file, top_n)
    except FileNotFoundError:
        print(f"\n❌ Error: Could not find '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()