Gmail Analysis
A Python-based tool for analyzing and exporting Gmail message headers.
Overview
This project provides utilities to export and analyze Gmail message headers, allowing you to gain insights into your email patterns, metadata, and header information.
Files
•	gmail_headers_export.py - Export Gmail message headers to a structured format
•	gmail_headers_analysis.py - Analyze exported Gmail headers for insights and patterns
•	credentials.json - Google API OAuth 2.0 credentials (required)
•	token.json - Stored authentication token (auto-generated)
Prerequisites
•	Python 3.7 or higher
•	Google Cloud Project with Gmail API enabled
•	OAuth 2.0 credentials from Google Cloud Console
Setup
1.	Install dependencies:
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
2.	Configure Google API:
o	Go to Google Cloud Console
o	Create a new project or select an existing one
o	Enable the Gmail API
o	Create OAuth 2.0 credentials (Desktop application)
o	Download the credentials and save as credentials.json in the project root
3.	First Run:
o	Run either script for the first time
o	A browser window will open for authentication
o	Grant the necessary permissions
o	The token.json file will be created automatically
Usage
Export Gmail Headers
python gmail_headers_export.py
Analyze Gmail Headers
python gmail_headers_analysis.py
Exports
Exported data will be saved in the exports/ directory.
Security Note
•	Never commit credentials.json or token.json to version control
•	These files contain sensitive authentication information
•	Ensure they are listed in your .gitignore file
License
This project is provided as-is for personal use.
