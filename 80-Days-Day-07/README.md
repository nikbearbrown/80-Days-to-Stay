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


I'll search for the major ATS systems currently used by companies.Based on the latest research, here are the **major ATS systems** you should focus on:

## **Top 5 ATS Systems (Fortune 500 - 2025 Data)**

### **1. Workday** - 39.3% market share
- **The #1 ATS** among Fortune 500 companies by far
- Enterprise-level, all-in-one HR platform
- Known for lengthy applications requiring unique account creation
- Resume parser often needs manual correction (15-20 min per application)
- Used by major retailers, banks, healthcare companies

### **2. SuccessFactors (SAP)** - 13.2% market share
- Second most popular among Fortune 500
- Part of SAP's HR suite
- Enterprise-focused

### **3. Taleo (Oracle)** - Declining but still significant
- Was previously tied with Workday (~22% in 2019)
- One of the oldest, most established systems
- Known for lengthy multi-page applications
- Heavy use of "knockout questions" (wrong answer = auto-rejection)
- Used by large banks, retail, manufacturing

### **4. iCIMS** - ~7-8% market share
- Enduring presence in enterprise
- Growing steadily

### **5. Greenhouse** - Growing rapidly
- **The one you mentioned!** 
- Modern, tech-focused ATS
- Very popular with startups and tech companies
- **Publicly accessible JSON feeds** (as you discovered!)
- Easy to detect via URL pattern: `greenhouse.io/[company-name]`
- Clean, fast application process
- Started at 0.4% of Fortune 500 in 2019, now growing

## **Other Major Modern ATS Systems**

### **Lever** 
- Greenhouse's main competitor
- Modern recruiting platform with CRM features
- Popular with tech and high-growth companies
- Fast, user-friendly

### **SmartRecruiters**
- Growing among mid-size to large companies
- Modern interface

### **Jobvite**
- Social recruiting features

### **BambooHR**
- Popular with SMBs
- Seamless transition from candidate to employee

### **Others Worth Noting:**
- **Workable** - Mid-market favorite
- **JazzHR** - Small business focus
- **Eightfold** - AI-powered, skills-based matching
- **PhenomPeople** - AI chatbots and personalization

## **Key Stats:**
- **97.8%** of Fortune 500 companies use a detectable ATS
- **Combined dominance**: Workday + SuccessFactors = 52.4% of Fortune 500
- Among **12,820+ companies** (broader market), distribution is much more varied

## **For Your "80 Days to Stay" Project:**

Since you're building detection for the top systems, I'd focus on:

1. **Greenhouse** ✓ (you've already got this working!)
2. **Workday** 
3. **Lever**
4. **Taleo**
5. **iCIMS**

These five will likely cover the majority of companies that international students would target. Your assumption is correct - if it's not one of the top 5-10, they're probably reviewing manually or using a proprietary system.

The Greenhouse approach you described (trying `company-name.greenhouse.io`) works well. Similar patterns exist for other systems:
- **Lever**: `jobs.lever.co/[company-name]`
- **Workday**: More complex, usually `[company].wd1.myworkdayjobs.com` or similar
