
import argparse
import json
import os
import shutil
import re
from datetime import datetime, timezone


from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def extract_canonical_email(from_str: str) -> str:
    """
    Deterministically extract a canonical email address from a Gmail From header.

    Rules:
    - Prefer an address inside <...>
    - Otherwise use the first email-like pattern
    - Lowercase the result
    - Return empty string if none found
    """
    if not from_str:
        return ""

    s = " ".join(str(from_str).split()).strip()

    # Prefer angle brackets
    m = re.search(r"<\s*([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\s*>", s, re.IGNORECASE)
    if m and m.group(1):
        return m.group(1).lower()

    # Fallback: first email anywhere
    m = re.search(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", s, re.IGNORECASE)
    if m and m.group(1):
        return m.group(1).lower()

    return ""


def get_gmail_service():
    """Authenticate and build the Gmail API service."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError(
                    "credentials.json not found. Download it from Google Cloud Console "
                    "for an OAuth 2.0 Desktop Client and place it next to this script."
                )
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def fetch_headers(service, query: str, max_messages: int):
    """
    Fetch messages from Gmail matching the query.
    Returns a list of JSON-ready dicts with:
    Date, From, Canonical Email, Subject, Unique ID
    """
    user_id = "me"
    results = []
    fetched = 0
    page_token = None

    while True:
        if fetched >= max_messages:
            break

        list_kwargs = {
            "userId": user_id,
            "q": query,
            "maxResults": min(500, max_messages - fetched),
        }
        if page_token:
            list_kwargs["pageToken"] = page_token

        resp = service.users().messages().list(**list_kwargs).execute()
        messages = resp.get("messages", [])
        if not messages:
            break

        for m in messages:
            if fetched >= max_messages:
                break

            msg = service.users().messages().get(
                userId=user_id,
                id=m["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()

            headers = msg.get("payload", {}).get("headers", [])
            header_map = {h.get("name"): h.get("value") for h in headers}

            from_raw = header_map.get("From", "")
            subject = header_map.get("Subject", "")

            # Prefer header Date; fall back to internalDate (ms since epoch)
            date_str = header_map.get("Date")
            if not date_str:
                internal_ms = msg.get("internalDate")
                if internal_ms is not None:
                    try:
                        dt = datetime.fromtimestamp(int(internal_ms) / 1000.0, tz=timezone.utc)
                        date_str = dt.isoformat()
                    except Exception:
                        date_str = ""
                else:
                    date_str = ""

            record = {
                "Date": date_str,
                "From": from_raw,
                "Canonical Email": extract_canonical_email(from_raw),
                "Subject": subject,
                "Unique ID": msg.get("id"),
            }
            results.append(record)
            fetched += 1

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return results


def save_json(records, output_dir: str | None = None) -> str:
    """Save records to a timestamped JSON file and return its path."""
    if output_dir is None:
        output_dir = "."
    os.makedirs(output_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gmail_headers_{ts}.json"
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    return path


def main():
    parser = argparse.ArgumentParser(
        description="Export Gmail headers to JSON with canonical email."
    )
    parser.add_argument(
        "--query",
        type=str,
        default="newer_than:7d",
        help="Gmail search query (same syntax as Gmail search box).",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=500,
        help="Maximum number of messages to fetch.",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=".",
        help="Output directory for the JSON file.",
    )
    args = parser.parse_args()

    service = get_gmail_service()
    records = fetch_headers(service, query=args.query, max_messages=args.max)

    print(f"Fetched {len(records)} messages.")
    if not records:
        print("No messages matched the query.")
        return

    # QA: count missing canonical emails
    missing = sum(1 for r in records if not r.get("Canonical Email"))
    print(f"QA: Missing canonical email for {missing} records.")

# 1) Save timestamped JSON (history)
    timestamped_path = save_json(records, output_dir="exports")
    print(f"Saved JSON to: {timestamped_path}")

# 2) Also update the stable file for analysis
    latest_path = os.path.join("exports", "gmail_headers.json")
    shutil.copyfile(timestamped_path, latest_path)
    print(f"Updated latest export: {latest_path}")


if __name__ == "__main__":
    main()
