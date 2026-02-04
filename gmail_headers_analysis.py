import argparse
import json
import os
from collections import defaultdict
from datetime import datetime


def load_records(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze(records, min_count: int = 1, max_count: int | None = None):
    """
    Build:
    - counts_by_email: {email: count}
    - messages_with_counts: list of {Count, Email, From, Subject}
    """
    # First pass: count per canonical email
    counts = defaultdict(int)
    for r in records:
        email = (r.get("Canonical Email") or "").strip().lower()
        if not email:
            continue
        counts[email] += 1

    # Optional range filter
    def in_range(c: int) -> bool:
        if c < min_count:
            return False
        if max_count is not None and c > max_count:
            return False
        return True

    # Build ranking list
    ranking = [
        {"Email": email, "Count": cnt}
        for email, cnt in counts.items()
        if in_range(cnt)
    ]
    ranking.sort(key=lambda x: x["Count"], reverse=True)

    # Build message-level rows with the sender's total count
    messages_with_counts = []
    for r in records:
        email = (r.get("Canonical Email") or "").strip().lower()
        if not email:
            continue
        cnt = counts[email]
        if not in_range(cnt):
            continue
        messages_with_counts.append({
            "Count": cnt,
            "Email": email,
            "From": r.get("From", ""),
            "Subject": r.get("Subject", ""),
        })

    return ranking, messages_with_counts


def save_csv_ranking(ranking, outdir: str, label: str = "") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{label}" if label else ""
    filename = f"sender_ranking{suffix}_{ts}.csv"
    path = os.path.join(outdir, filename)
    os.makedirs(outdir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("Count,Email\n")
        for row in ranking:
            f.write(f"{row['Count']},{row['Email']}\n")
    return path


def save_csv_messages(messages, outdir: str, label: str = "") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{label}" if label else ""
    filename = f"messages_with_counts{suffix}_{ts}.csv"
    path = os.path.join(outdir, filename)
    os.makedirs(outdir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("Count,Email,From,Subject\n")
        for row in messages:
            # Escape double quotes and wrap fields that may contain commas
            def esc(s: str) -> str:
                s = s.replace('"', '""')
                if "," in s or '"' in s or "\n" in s:
                    return f'"{s}"'
                return s
            f.write(
                f"{row['Count']},"
                f"{esc(row['Email'])},"
                f"{esc(row['From'])},"
                f"{esc(row['Subject'])}\n"
            )
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Gmail header JSON and produce ranking/report CSVs."
    )
    
    parser.add_argument(
    "--json-file",
    type=str,
    default=os.path.join("exports", "gmail_headers.json"),
    help="Path to gmail_headers JSON export (default: exports/gmail_headers.json)",
)

    parser.add_argument(
        "--min-count",
        type=int,
        default=1,
        help="Minimum message count per sender to include.",
    )
    parser.add_argument(
        "--max-count",
        type=int,
        default=None,
        help="Maximum message count per sender to include (optional).",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=".",
        help="Output directory for CSV files.",
    )
    parser.add_argument(
        "--label",
        type=str,
        default="",
        help="Optional label to include in output filenames (e.g. 'inbox14d').",
    )
    args = parser.parse_args()

    records = load_records(args.json_file)
    print(f"Loaded {len(records)} records from {args.json_file}")

    ranking, messages = analyze(records, min_count=args.min_count, max_count=args.max_count)
    print(f"Unique senders in range: {len(ranking)}")
    print(f"Messages in range: {len(messages)}")

    rank_path = save_csv_ranking(ranking, args.outdir, args.label)
    msg_path = save_csv_messages(messages, args.outdir, args.label)

    print(f"Sender ranking CSV: {rank_path}")
    print(f"Messages with counts CSV: {msg_path}")


if __name__ == "__main__":
    main()
