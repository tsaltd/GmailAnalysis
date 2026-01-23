# GmailAnalysis — Implementation Roadmap (ETL First)
**Date:** 2026-01-23  
**Scope:** Begin implementation work starting with the data flow + ETL pipeline, using the *GmailAnalysis-Design* repo as the design reference.

---

## 0) Working assumptions
- **Design repo is authoritative** for diagrams, UI intent, and naming conventions: `GmailAnalysis-Design/docs/turnover-manifest.md`.
- **Implementation repo** will contain runnable code + generated artifacts (ignored by git).
- **Input**: one spreadsheet export (CSV/XLSX) with columns:
  - `Date`, `From`, `Subject`, `Unique ID`
- **Output datasets** (CSV):
  1. `Sender.csv` — `sender_id`, `email_address`
  2. `Header.csv` — `header_id`, `from`, `subject`, `unique_id`, `sender_id`
  3. `Sender_Header_Counts.csv` — `sender_id`, `email_address`, `header_count`
  4. `Message_Classification.csv` — `email_address`, `from`, `subject`, `unique_id`, `category`

---

## 1) Data flow: canonical ETL stages
### Stage A — Ingest
**Goal:** Load raw records from CSV/XLSX into a normalized in-memory table.
- Standardize column names (case/whitespace tolerant).
- Trim whitespace, preserve original `From` string (do **not** lose display name).

### Stage B — Parse / Normalize
**Goal:** Extract a canonical email address and create stable IDs.
- `email_address`: lowercased, stripped; **no angle brackets** in output.
- Parsing rules:
  - Prefer an address found inside `<...>` if present.
  - Else, find the first RFC-like email substring.
  - Else, blank ⇒ record flagged as `parse_failed`.
- `sender_id`: stable surrogate key (recommended):
  - `sender_id = sha1(email_address)[:12]` (or full sha1 if you prefer)
- `header_id`: stable surrogate key:
  - `header_id = sha1(unique_id)[:12]` if unique_id is trustworthy
  - else `sha1(date + from + subject)[:12]`

### Stage C — Relate
**Goal:** Build relational linkage.
- Map `email_address -> sender_id`
- Add `sender_id` to each message row (Header).

### Stage D — Aggregate
**Goal:** Compute per-sender counts.
- `Sender_Header_Counts.csv` produced from `Header.csv` group-by `sender_id`.

### Stage E — Classify (rule-first, model-later)
**Goal:** Categorize messages. Start deterministic; add LLM later as an optional tool.
Categories (example mapping to your existing scheme):
1. Spam / Phishing / Blacklist
2. Job related (not personal)
3. Job related other
4. Undetermined
5. Personal / Whitelist

**v0 classifier rules** (fast + transparent):
- Maintain local lists in `data/lists/`:
  - `whitelist_domains.txt`, `whitelist_emails.txt`
  - `blacklist_domains.txt`, `blacklist_emails.txt`
  - `job_keywords.txt` (subject + from text)
- Apply in this order:
  1) Blacklist exact email/domain ⇒ Category 1  
  2) Whitelist exact email/domain ⇒ Category 5  
  3) Job keyword hit (subject/from) ⇒ Category 2 or 3 (split with secondary keywords)  
  4) Else ⇒ Category 4  

---

## 2) Implementation repo: recommended tree
```
GmailAnalysis/
  docs/
    implementation-roadmap.md
    etl-spec.md
  src/
    gmailanalysis/
      __init__.py
      cli.py
      io_loaders.py
      parsing.py
      transforms.py
      aggregates.py
      classify_rules.py
      exports.py
      validate.py
      utils_hash.py
  data/
    input/              # local input files (gitignored)
    output/             # generated CSVs (gitignored)
    lists/              # rule lists (tracked)
  tests/
    test_parsing.py
    test_transforms.py
  pyproject.toml
  README.md
  .gitignore
```

---

## 3) CLI commands (target UX)
### Single-shot run
```
python -m gmailanalysis.cli run --input data/input/raw.xlsx --out data/output
```

### Stage-only runs
```
python -m gmailanalysis.cli ingest --input ...
python -m gmailanalysis.cli normalize --out ...
python -m gmailanalysis.cli aggregate --out ...
python -m gmailanalysis.cli classify --out ...
```

---

## 4) Acceptance criteria for ETL v0
- Produces all 4 output CSVs with required columns.
- No angle brackets in `email_address`.
- Deterministic IDs: rerunning on same input yields identical IDs.
- Basic validation:
  - `unique_id` is non-empty in Header (or logged if missing)
  - `sender_id` non-empty when email parsed
  - counts match the number of Header rows

---

## 5) Git hygiene
Add to `.gitignore`:
- `data/input/`
- `data/output/`
- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `*.log`

---

## 6) Next three implementation moves
1) Implement **parsing + ID** utilities + unit tests (highest risk/impact).
2) Implement **end-to-end run** producing Sender/Header/Counts.
3) Add **rule lists + classification** and output Message_Classification.

---

## 7) “Design repo as reference” workflow
- Keep a lightweight pointer file in implementation repo:
  - `docs/design-reference.md` containing:
    - the design repo URL
    - the canonical manifest path: `GmailAnalysis-Design/docs/turnover-manifest.md`
    - any naming decisions you must mirror

