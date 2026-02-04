⚠️ DEPRECATED

This repository contains pre-beta experiments.
Active development continues in a new repository.

Design & planning:
https://github.com/tsaltd/GmailAnalysis-Design


# Gmail Analysis

A Python-based tool for analyzing and exporting Gmail message headers.

## Overview

This project provides utilities to export and analyze Gmail message headers, allowing you to gain insights into your email patterns, metadata, and header information.

## Files

- **gmail_headers_export.py** - Export Gmail message headers to a structured format
- **gmail_headers_analysis.py** - Analyze exported Gmail headers for insights and patterns
- **credentials.json** - Google API OAuth 2.0 credentials (required)
- **token.json** - Stored authentication token (auto-generated)

## Prerequisites

- Python 3.7 or higher
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials from Google Cloud Console

## Setup

1. **Install dependencies:**
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Configure Google API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials and save as `credentials.json` in the project root

3. **First Run:**
   - Run either script for the first time
   - A browser window will open for authentication
   - Grant the necessary permissions
   - The `token.json` file will be created automatically

## Usage

### Export Gmail Headers
```bash
python gmail_headers_export.py
```

### Analyze Gmail Headers
```bash
python gmail_headers_analysis.py
```

## Exports

Exported data will be saved in the `exports/` directory.

## Security Note

- Never commit `credentials.json` or `token.json` to version control
- These files contain sensitive authentication information
- Ensure they are listed in your `.gitignore` file

## License

This project is provided as-is for personal use.
