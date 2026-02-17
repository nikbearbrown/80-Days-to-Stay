# WEBSITE_EXTRACTION_PROMPT = """Extract official website for: {company_name}

# RULES:
# 1. URLs must exist in search results
# 2. Never generate URLs

# MATCHING:

# Direct Match:
# - Domain = company name (ignore spaces/hyphens)
# - Domain = acronym shown in results

# Fuzzy Match (STRICT - all must be true):
# - Names similar (removing suffixes/spaces)
# - Business type matches (same industry)
# - Geographic location compatible (if location-specific)
# - Company scale similar (both startups OR both enterprises)

# Relationships (needs EXPLICIT phrase):
# - "acquired by X" / "subsidiary of X" → X's root domain
# - "company behind X" / "maker of X" → X's site
# - "formerly X" / "rebranded to X" → current name

# DO NOT infer relationships from:
# - "Holdings" in name
# - Listing properties/portfolios
# - Similar names alone
# - Industry overlap

# URL CLEANING:
# Strip these paths: /news/, /press/, /blog/, /team/, /property/, /article/
# Extract root domain only 

# EXCLUDE:
# linkedin, facebook, twitter, instagram, crunchbase, bloomberg, pitchbook, zoominfo, dnb, glassdoor, indeed, wikipedia

# CRITICAL REASONING RULES:
# ✓ Use: "explicitly states", "directly matches", "confirmed by"
# ✗ Avoid: "suggests", "indicates", "likely", "presumed", "aligns with"

# Multiple signals required (2+):
# - Appears multiple times
# - Has official pages (/about, /contact, /company)
# - Self-describes as company
# - Description matches business
# - Do not try to overguess, you have to have highly confident and provide enough evidence for reasoning

# SEARCH RESULTS:
# {search_results}
# """


WEBSITE_EXTRACTION_PROMPT = """Extract official website for: {company_name}

ABSOLUTE RULES:
1. URLs MUST exist in search results
2. NEVER generate URLs
3. NULL if ANY doubt

VALIDATION - Step 1:
Company name (or variation: no INC/LLC, acronym, no spaces) MUST appear.
Not found → NULL

MATCHING - Step 2:

A) Direct Match ONLY:
✓ Domain = exact company name (ignore spaces/hyphens/INC/LLC)
✓ Domain = acronym EXPLICITLY shown in results

B) Fuzzy Match FORBIDDEN unless ALL true:
✓ Business descriptions EXPLICITLY identical
✓ Locations EXPLICITLY compatible
✓ Scale EXPLICITLY similar
✗ Missing even ONE → NULL

C) Explicit Relationships ONLY:
✓ Text MUST say: "acquired by X", "X acquired Y", "subsidiary of X"
✓ Extract X's root domain (remove /news/, /press/, /blog/)
✗ No relationship text → NULL

ABSOLUTE PROHIBITIONS:

✗ ZERO character substitutions allowed
  Examples of FORBIDDEN matches:
  - Company ≠ Cumpany (o≠u)
  - ANY letter change = NULL

✗ ZERO number/word conversions
  - 1 ≠ One
  - 2 ≠ Two
  - Unless EXPLICIT text shows both

✗ ZERO Holdings assumptions
  - "X Holdings" does NOT own "X Brand"
  - Needs text like: "X Holdings owns Y" or "X Holdings operates Y"

✗ ZERO property/portfolio inferences
✗ ZERO similar name assumptions

EXCLUDE:
linkedin, facebook, twitter, instagram, crunchbase, bloomberg, pitchbook, zoominfo, dnb, glassdoor, indeed, wikipedia

VALIDATE (need 2+ signals):
- Multiple appearances
- Has /about, /contact, /company
- Self-describes as company
- Business matches

REASONING MUST include:
1. Which rule (A/B/C) applied
2. Exact matching evidence
3. Multiple validation signals
4. High confident decisions should be made, else better to leave null 
5. If you still believe but are not 100 percent sure, you have a alternate url attribute. 

FORBIDDEN REASONING WORDS:
"suggests", "likely", "variation", "resembles", "similar to", "allowing for"

REQUIRED REASONING WORDS:
"explicitly states", "directly matches", "confirmed by"

WHEN IN DOUBT → NULL
Better 100 false negatives than 1 false positive

SEARCH RESULTS:
{search_results}
"""
