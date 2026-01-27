# SEC,DOL & USCIS Data

## Overview

This script processes and flattens data from SEC (Securities and Exchange Commission) filings and DOL (Department of Labor) records to create a unified dataset for identifying potential H-1B sponsoring employers among funded startups.

## Project Structure

```
├── Data/
│   ├── SEC_data_flattend.csv          # Initial flattened CSV from master SEC JSON
│   └── SEC_DOL_H1b_data_mapped.csv    # Final merged file with H-1B mapping
│
└── Scripts/
    └── [Python scripts for data processing]
```

## Data Files

### `SEC_data_flattend.csv`
The initial flattened CSV extracted from the master SEC JSON file. Contains raw firmographic and funding data from SEC filings.

### `SEC_DOL_H1b_data_mapped.csv`
The final output file with H-1B mapping complete. This file merges values from all sources (SEC, DOL, USCIS) and contains `null` values where data is not available.

## Key Columns

### Firmographic Details
| Column | Description |
|--------|-------------|
| `company_name` | Legal name of the employer |
| `industry` | Primary industry classification |
| `website` | Company website URL |
| `city` / `state` | Headquarters location |

### Funding Indicators
| Column | Description |
|--------|-------------|
| `total_funding` | Total capital raised by the company over time |
| `latest_funding_amount` | Most recent funding round size |
| `latest_funding_date` | Date of most recent funding round |
| `latest_funding_stage` | Stage of latest round (Seed, Series A, etc.) |

These funding metrics help indicate a company's financial capacity and potential near-term hiring appetite.

### H-1B Sponsorship History
| Column | Description |
|--------|-------------|
| `Approval_Rate` | Historical H-1B petition approval percentage |
| `Total Approvals` | Count of approved H-1B petitions |
| `Total Denials` | Count of denied H-1B petitions |
| `median_salary_offered` | Typical salary levels for sponsored roles |
| `top_job_titles_sponsored` | Common roles previously sponsored |

> **Note:** `Null` values in sponsorship fields do not necessarily mean the company does not sponsor H-1B visas—it indicates that our available data does not contain a trace of sponsorship activity for that company.

### Additional Columns

The remaining columns (executive officers, board members, year incorporated, company age, contact details, etc.) provide supplementary information for employer research and outreach efforts.

## Usage

This dataset enables users to:
- Filter companies by funding stage and amount
- Identify employers with proven H-1B sponsorship track records
- Prioritize outreach based on approval rates and sponsored job titles
- Research company backgrounds for targeted applications
