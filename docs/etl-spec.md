# GmailAnalysis — ETL Spec (v0)
**Date:** 2026-01-23

## Inputs
### Supported
- `.csv` with headers
- `.xlsx` with a single sheet OR a sheet name passed via CLI

### Required columns (case-insensitive)
- `Date`
- `From`
- `Subject`
- `Unique ID`

## Normalized internal record
| Field | Type | Notes |
|---|---|---|
| date | string | Keep raw string; optionally parse to datetime later |
| from_raw | string | Original sender field from export |
| subject | string | Raw subject |
| unique_id | string | Stable message id from export |
| email_address | string | Canonical parsed email (lowercased) |
| sender_id | string | Hash(email_address) |
| header_id | string | Hash(unique_id) |
| parse_failed | bool | True when no email extracted |

## Parsing rules (email)
1. If `from_raw` contains `<...>` and inside matches an email pattern, use it.
2. Else find first email-like substring.
3. Else `email_address = ""` and `parse_failed = True`.

Email regex (good enough for v0):
- `(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}`

## ID strategy
- `sender_id = sha1(email_address).hexdigest()[:12]`
- `header_id = sha1(unique_id).hexdigest()[:12]`

If `unique_id` missing:
- `header_id = sha1(date + '|' + from_raw + '|' + subject).hexdigest()[:12]`  
and log a warning.

## Outputs
### Sender.csv
- `sender_id`
- `email_address`
**Dedup:** one row per email_address

### Header.csv
- `header_id`
- `from`
- `subject`
- `unique_id`
- `sender_id`
**Row count:** equals input message count

### Sender_Header_Counts.csv
- `sender_id`
- `email_address`
- `header_count`

### Message_Classification.csv
- `email_address`
- `from`
- `subject`
- `unique_id`
- `category`

## Validation checks (fail-fast where possible)
- Required columns exist
- No duplicate `unique_id` (warn if duplicates; keep first or keep all with suffix—decide once)
- All output CSVs written successfully
- If `parse_failed` rate > configurable threshold (default 5%), emit warning and sample offenders

