import csv
import json
import os

INPUT_JSON = os.path.join("exports", "gmail_headers.json")
OUTPUT_CSV = os.path.join("reports", "gmail_headers.csv")

FIELDS = ["Date", "From", "Canonical Email", "Subject", "Unique ID"]


def main():
    if not os.path.exists(INPUT_JSON):
        raise FileNotFoundError(f"Missing input JSON: {INPUT_JSON}")

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        records = json.load(f)
d
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for r in records:
            writer.writerow({k: r.get(k, "") for k in FIELDS})

    print(f"Wrote CSV: {OUTPUT_CSV} ({len(records)} rows)")


if __name__ == "__main__":
    main()
