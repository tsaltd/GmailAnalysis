from __future__ import annotations

import argparse
from gmailanalysis.io_loaders import load_messages


def main() -> None:
    p = argparse.ArgumentParser(prog="gmailanalysis")
    sub = p.add_subparsers(dest="cmd", required=True)

    ingest = sub.add_parser("ingest", help="Stage A: load raw messages")
    ingest.add_argument("--input", required=True, help="Path to .csv or .xlsx")
    ingest.add_argument("--sheet", default=None, help="XLSX sheet name (optional)")

    args = p.parse_args()

    if args.cmd == "ingest":
        rows = load_messages(args.input, sheet_name=args.sheet)
        print(f"Loaded {len(rows)} rows from {args.input}")
        if rows:
            r = rows[0]
            print("Sample row:")
            print(f"  Date: {r.date}")
            print(f"  From: {r.from_raw}")
            print(f"  Subject: {r.subject}")
            print(f"  Unique ID: {r.unique_id}")


if __name__ == "__main__":
    main()
