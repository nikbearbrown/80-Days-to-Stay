import json
import re
import sys
from typing import Dict, List, Any
from collections import defaultdict

def normalize_state(state: str) -> str:
    """Normalize state codes to uppercase, handle variations."""
    if not state:
        return ""
    return state.strip().upper()

def is_excluded_industry(industry_name: str) -> bool:
    """Check if company is in an excluded industry category."""
    if not industry_name:
        return False
    
    industry_lower = industry_name.lower()
    
    excluded_keywords = [
        'real estate', 'realty', 'property', 'reit', 'residential',
        'pooled investment', 'hedge fund', 'private equity', 'investment fund',
        'oil', 'gas', 'petroleum', 'energy exploration',
        'agriculture', 'farming', 'agribusiness',
        'retail', 'store', 'shopping',
        'construction', 'contractor', 'building',
        'commercial',
        'restaurant', 'food service', 'hospitality'
    ]
    
    return any(keyword in industry_lower for keyword in excluded_keywords)

def extract_funding_amount(company_data: Dict[str, Any]) -> float:
    """Extract total offering amount from funding object."""
    try:
        funding = company_data.get('funding', {})
        
        # Try total_offering_amount
        if 'total_offering_amount' in funding:
            amount = funding['total_offering_amount']
            if amount is None:
                return 0.0
            if isinstance(amount, (int, float)):
                return float(amount)
            if isinstance(amount, str):
                cleaned = re.sub(r'[,$]', '', amount)
                return float(cleaned)
        
        # Fallback to total_amount_sold if offering amount is null
        if 'total_amount_sold' in funding:
            amount = funding['total_amount_sold']
            if amount and isinstance(amount, (int, float)):
                return float(amount)
        
        return 0.0
    except (ValueError, TypeError):
        return 0.0

def is_us_company(company_data: Dict[str, Any]) -> bool:
    """Check if company is US-based (not Europe or other international)."""
    company = company_data.get('company', {})
    address = company.get('address', {})
    
    state = address.get('state', '').strip().upper()
    
    # US states are 2-letter codes
    if state and len(state) == 2 and state.isalpha():
        # Exclude international codes
        non_us_codes = ['X0', 'X1', 'X2', 'X3']  # Common international placeholders
        if state not in non_us_codes:
            return True
    
    return False

def filter_companies(input_file: str, output_file: str, 
                    target_states: List[str] = None,
                    min_funding: float = 1_000_000) -> Dict[str, Any]:
    """
    Filter SEC companies based on criteria.
    
    Args:
        input_file: Path to sec_companies_master.json
        output_file: Path to output sec_companies_targets.json
        target_states: List of state codes to keep (default: MA, CA, NY, WA, TX, IL)
        min_funding: Minimum funding amount (default: $1M)
    
    Returns:
        Dictionary with filtering statistics
    """
    
    if target_states is None:
        target_states = ['MA', 'CA', 'NY', 'WA', 'TX', 'IL']
    
    target_states = [s.upper() for s in target_states]
    
    print(f"Loading companies from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both formats: direct array or object with metadata
    if isinstance(data, dict) and 'companies' in data:
        companies = data['companies']
        metadata = data.get('metadata', {})
        print(f"Data source: {metadata.get('date_range', {})}")
    else:
        companies = data
        metadata = {}
    
    initial_count = len(companies)
    print(f"Initial company count: {initial_count:,}")
    
    # Statistics tracking
    stats = {
        'initial_count': initial_count,
        'removed_by_funding': 0,
        'removed_by_location': 0,
        'removed_by_industry': 0,
        'removed_by_country': 0,
        'final_count': 0,
        'by_state': defaultdict(int),
        'by_funding_range': defaultdict(int),
        'by_industry': defaultdict(int)
    }
    
    filtered_companies = []
    
    print("\nApplying filters...")
    print(f"  → Minimum funding: ${min_funding:,}")
    print(f"  → Target states: {', '.join(target_states)}")
    print(f"  → Excluded industries: Real Estate, Pooled Investment, Oil/Gas, etc.\n")
    
    for company_data in companies:
        company = company_data.get('company', {})
        address = company.get('address', {})
        
        # Filter 1: Check if US-based
        if not is_us_company(company_data):
            stats['removed_by_country'] += 1
            continue
        
        # Filter 2: Check funding threshold
        funding = extract_funding_amount(company_data)
        if funding < min_funding:
            stats['removed_by_funding'] += 1
            continue
        
        # Filter 3: Check state
        state = normalize_state(address.get('state', ''))
        
        if state not in target_states:
            stats['removed_by_location'] += 1
            continue
        
        # Filter 4: Check industry exclusions
        industry = company.get('industry', '')
        if is_excluded_industry(industry):
            stats['removed_by_industry'] += 1
            continue
        
        # Passed all filters - add to results
        filtered_companies.append(company_data)
        
        # Track statistics
        stats['by_state'][state] += 1
        
        # Funding range
        if funding < 5_000_000:
            stats['by_funding_range']['$1M-$5M'] += 1
        elif funding < 10_000_000:
            stats['by_funding_range']['$5M-$10M'] += 1
        elif funding < 25_000_000:
            stats['by_funding_range']['$10M-$25M'] += 1
        elif funding < 50_000_000:
            stats['by_funding_range']['$25M-$50M'] += 1
        else:
            stats['by_funding_range']['$50M+'] += 1
        
        # Industry
        if industry:
            stats['by_industry'][industry] += 1
    
    stats['final_count'] = len(filtered_companies)
    
    # Create output structure matching input format
    output_data = {
        'metadata': {
            'filtered_from': input_file,
            'generated_at': metadata.get('generated_at', ''),
            'original_total': initial_count,
            'filtered_total': stats['final_count'],
            'filters_applied': {
                'min_funding': min_funding,
                'target_states': target_states,
                'excluded_industries': [
                    'Real Estate', 'Pooled Investment', 'Oil/Gas',
                    'Agriculture', 'Retail', 'Construction'
                ]
            }
        },
        'companies': filtered_companies
    }
    
    # Save filtered companies
    print(f"\nSaving {stats['final_count']:,} companies to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    print("\n" + "="*60)
    print("FILTERING RESULTS")
    print("="*60)
    print(f"Initial companies:        {stats['initial_count']:>10,}")
    print(f"Removed (non-US):         {stats['removed_by_country']:>10,}")
    print(f"Removed (funding < $1M):  {stats['removed_by_funding']:>10,}")
    print(f"Removed (wrong state):    {stats['removed_by_location']:>10,}")
    print(f"Removed (excluded ind):   {stats['removed_by_industry']:>10,}")
    print(f"Final target companies:   {stats['final_count']:>10,}")
    print(f"Retention rate:           {stats['final_count']/stats['initial_count']*100:>9.1f}%")
    
    print("\n" + "="*60)
    print("COMPANIES BY STATE")
    print("="*60)
    for state in sorted(stats['by_state'].keys()):
        count = stats['by_state'][state]
        pct = count / stats['final_count'] * 100
        print(f"{state:>4}: {count:>6,} ({pct:>5.1f}%)")
    
    print("\n" + "="*60)
    print("COMPANIES BY FUNDING RANGE")
    print("="*60)
    funding_order = ['$1M-$5M', '$5M-$10M', '$10M-$25M', '$25M-$50M', '$50M+']
    for range_name in funding_order:
        count = stats['by_funding_range'][range_name]
        if count > 0:
            pct = count / stats['final_count'] * 100
            print(f"{range_name:>12}: {count:>6,} ({pct:>5.1f}%)")
    
    print("\n" + "="*60)
    print("TOP 10 INDUSTRIES")
    print("="*60)
    sorted_industries = sorted(
        stats['by_industry'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    for industry, count in sorted_industries:
        pct = count / stats['final_count'] * 100
        industry_name = industry[:40] + '...' if len(industry) > 40 else industry
        print(f"{industry_name:>43}: {count:>5,} ({pct:>4.1f}%)")
    
    # Sample companies
    print("\n" + "="*60)
    print("SAMPLE FILTERED COMPANIES (First 5)")
    print("="*60)
    for i, company_data in enumerate(filtered_companies[:5], 1):
        company = company_data.get('company', {})
        address = company.get('address', {})
        funding_obj = company_data.get('funding', {})
        
        name = company.get('name', 'Unknown')
        state = address.get('state', '??')
        funding = extract_funding_amount(company_data)
        industry = company.get('industry', 'Not specified')
        
        print(f"\n{i}. {name}")
        print(f"   State: {state}")
        print(f"   Funding: ${funding:,.0f}")
        print(f"   Industry: {industry[:50]}")
    
    print("\n" + "="*60)
    
    return stats

def main():
    """Main function with command-line argument support."""
    # Default values
    input_file = 'sec_companies_master.json'
    output_file = 'sec_companies_targets.json'
    
    # Check for command-line arguments
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    
    # Show usage
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python filter_sec_companies.py [input_file] [output_file]")
        print("\nDefaults:")
        print("  input_file:  sec_companies_master.json")
        print("  output_file: sec_companies_targets.json")
        print("\nExample:")
        print("  python filter_sec_companies.py my_companies.json filtered_output.json")
        sys.exit(0)
    
    # Run the filter
    try:
        stats = filter_companies(
            input_file=input_file,
            output_file=output_file,
            target_states=['MA', 'CA', 'NY', 'WA', 'TX', 'IL'],
            min_funding=1_000_000
        )
        
        print("\n✓ Filtering complete!")
        print(f"✓ Output saved to: {output_file}")
        print(f"✓ Ready for domain inference (next step)")
        
    except FileNotFoundError:
        print(f"\n❌ Error: Could not find input file '{input_file}'")
        print("Make sure the file exists in the current directory.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"\n❌ Error: File '{input_file}' is not valid JSON")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()