# Day 07

_Documentation coming soon..._


I'll search for the official government databases that contain H1B sponsorship and visa filing information.Perfect! Here are the key government databases for H1B sponsorship and visa filing data:

## **Primary Data Sources**

### **1. Department of Labor (DOL) - LCA Disclosure Data**
**Main Page:** https://www.dol.gov/agencies/eta/foreign-labor/performance

This is the primary source with **millions** of Labor Condition Application (LCA) records. The most recent data covers October 2024 through June 2025 (Q3 FY2025).

**Download Links for LCA Programs (H-1B, H-1B1, E-3):**
- Latest Q3 FY2025: https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Disclosure_Data_FY2025_Q3.xlsx
- Historical data available back to FY2008 on the same page

**Key Features:**
- Contains company names, addresses, job titles, wage data, case status
- Updated quarterly
- Includes all certified LCA applications (required before H-1B petition filing)
- Excel format with record layouts provided

### **2. USCIS H-1B Employer Data Hub**
**Main Page:** https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub

**Download Files:** https://www.uscis.gov/archive/h-1b-employer-data-hub-files

**Key Features:**
- Data from FY2009 through FY2025 (Q4)
- Includes approval and denial rates by employer
- Initial and continuing employment data
- Searchable by employer name, city, state, ZIP, NAICS code
- CSV/Excel downloads available

### **3. Other Related Programs**
The DOL also provides similar data for:
- **H-2A** (temporary agricultural workers)
- **H-2B** (temporary non-agricultural workers)
- **PERM** (permanent labor certification)

## **Important Notes for Your Project:**

1. **Data Volume:** The DOL LCA database has 6+ million records spanning multiple years
2. **Filtering Strategy:** You'll want to filter by:
   - **Decision Date** (last 2-3 years for active companies)
   - **Case Status** (Certified cases)
   - **Frequency** (number of applications per company)

3. **Data Quality:** 
   - Contains company FEIN (Federal Employer Identification Number)
   - Worksite addresses
   - Job titles and SOC codes
   - Wage information
   - Certification dates

4. **Complementary to Your SEC Data:** This gives you a different angle - companies that have **proven history** of visa sponsorship, not just funding status.

The DOL LCA data is particularly valuable because every H-1B petition **must** have a certified LCA first, so this represents actual sponsorship activity, not just potential.
