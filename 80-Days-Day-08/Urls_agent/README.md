## How to run this script

This script takes a list of company names and creates a CSV with their websites.

---

## 1. What you need to edit

- **In `agent.py`** (near the bottom) find:

```python
company_names = []
```

- Replace it with one of these options:

- **Use `data_websites.csv` (recommended)**:

```python
import pandas as pd

df = pd.read_csv("data_websites.csv")
company_names = df["company_name"].dropna().tolist()  # or .iloc[:50] for a small test
```

- **Or: simple manual test list**:

```python
company_names = [
    "Google LLC",
    "Microsoft Corporation",
]
```

Nothing else in the code needs to be changed for normal use.

---

## 2. Environment variables (`.env`)

This zip **already contains a `.env` file** in the project root (same folder as `agent.py`).

- Open `.env` and **replace the values with your own keys**:

```bash
you=YOUR_YOU_DOT_COM_API_KEY
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

These are required for:
- **`you`**: You.com search (used to fetch web results).
- **`GEMINI_API_KEY`**: Gemini model (used to pick the website).


---

## 3. Install and run

This zip **already contains a virtual environment** (`myenv`).

From this folder in a terminal:

```bash
source myenv/bin/activate  # Windows: myenv\Scripts\activate
python agent.py
```

Make sure you have already edited `.env` with your own keys (section 2).

If the bundled env ever breaks, you can create a new one:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install langgraph pydantic pandas requests python-dotenv google-genai youdotcom
python agent.py
```

You will see progress logs in the terminal while it runs.

---

## 4. Input and output

- **Input**:
  - The `company_names` list you set in `agent.py`.
  - Typically sourced from `data_websites.csv` → column `company_name`.

- **Output**:
  - A file called **`Websites_data.csv`** in this folder.
  - Each row has:
    - `company_name`
    - `website` (chosen official website or blank if not confident)
    - `reasoning`
    - `alternative_url` (optional backup URL)

You only need to:
- Set `company_names` in `agent.py`.
- Put your keys in `.env`.
- Run `python agent.py` and use `Websites_data.csv` as the result.

