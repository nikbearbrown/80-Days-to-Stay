# Webpage Content Extractor

Extract text content from scraped HTML files. Two versions: **clean** (preserves contact info, removes media noise) and **raw** (minimal processing).

## Folder structure
- Create a folder named `websites` and copy all scrapped website folders in that folder before running any scripts

## Scripts

### `webpage_processor_clean.py` - Smart Cleaning (Recommended)
- **Preserves**: Emails, phones, URLs, addresses, names, dates
- **Removes**: Image/video URLs, technical timestamps, file sizes
- **Use for**: Job leads, networking, business intelligence

### `webpage_processor_raw.py` - Minimal Processing
- **Preserves**: Everything
- **Removes**: Only HTML tags (`<script>`, `<style>`)
- **Use for**: Complete data archiving

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run clean version 
cd Scripts
python webpage_processor_clean.py

# Run raw version (complete data)
python webpage_processor_raw.py
```

## Project Structure

```
project-root/
├── Scripts/
│   ├── webpage_processor_clean.py
│   └── webpage_processor_raw.py
├── websites/              # Input: scraped HTML files
│   ├── company1.com/
│   │   ├── page1.html
│   │   └── page2.html
│   └── company2.com/
│       └── about.html
```

## Output

Both scripts generate:
- **`.md` files** - Same name as HTML, extracted text only
- **`{folder_name}_all_content.txt`** - Aggregated content per website folder

**Example output:**
```
websites/
└── company1.com/
    ├── page1.html          (original)
    ├── page1.md            (extracted text)
    ├── page2.html
    ├── page2.md
    └── company1.com_all_content.txt  (all pages combined)
```

## What Gets Extracted

| Data Type | Clean Version | Raw Version |
|-----------|--------------|-------------|
| Text content | ✅ | ✅ |
| Emails | ✅ | ✅ |
| Phone numbers | ✅ | ✅ |
| URLs (LinkedIn, company sites) | ✅ | ✅ |
| Addresses | ✅ | ✅ |
| Names & titles | ✅ | ✅ |
| Dates (human-readable) | ✅ | ✅ |
| Image URLs | ❌ | ✅ |
| Video URLs | ❌ | ✅ |
| Technical timestamps | ❌ | ✅ |
| File sizes | ❌ | ✅ |

## Configuration

**Change thread count** (default: 4):
```python
# In either script, modify:
processor = WebpageProcessor(
    base_path=str(websites_path),
    max_workers=8  # Change here
)
```

**Process different folder**:
```python
# Modify main() function:
websites_path = base_dir / "custom_folder"
```

## Performance

- **Clean**: ~280-350 files/min (4 threads)
- **Raw**: ~300-400 files/min (4 threads)
- **Output size**: Clean is ~25% smaller than raw

## Requirements

- Python 3.7+
- BeautifulSoup4 (see `requirements.txt`)
