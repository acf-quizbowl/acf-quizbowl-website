#!/usr/bin/env python3
"""Sync members data from Google Sheets to JSON, Excel, and update Markdown.

This script reads member data from a Google Sheets spreadsheet, converts it
to the JSON format used by the site, generates an Excel spreadsheet, and then
updates the Markdown file using the same logic as update_members.py.

Usage:
    python3 scripts/sync_from_sheets.py [sheet_id] [--credentials credentials_file]

The spreadsheet should have columns: Name, Email, Status, Affiliations, Contributions, Skills, Last Activity
Affiliations and Contributions should be newline-separated in their cells.

Dependencies:
    pip install gspread google-auth openpyxl
"""

import json
import sys
import argparse
from pathlib import Path
from re import split

import gspread
from google.oauth2.service_account import Credentials

from update_members import update_members_md, update_members_excel

status_order = ["full", "provisional", "emeritus", "former", "nonmember"]
order_priority = {status: i for i, status in enumerate(status_order)}


def get_indices_dict(main_array, search_array):
    """
    Finds first index of each string in the search_array within the main_array
    and returns them in a dictionary.
    """

    first_indices = {}
    for item in search_array:
        try:
            # Use the index() method to find the first occurrence
            index = main_array.index(item)
            first_indices[item] = index
        except ValueError:
            # Handle cases where the item is not found in the haystack list
            first_indices[item] = None  # or -1 or some other indicator
    return first_indices


def main():
    parser = argparse.ArgumentParser(description="Sync members data from Google Sheets")
    parser.add_argument(
        "sheet_id",
        nargs="?",
        default="1Byrc19gXCmOYJajB5O-bUYJg-E8GuM6VrYcvkcnbW8Y",  # ACF Master list
        help="Google Sheets spreadsheet ID (default: example ID)",
    )
    parser.add_argument(
        "--credentials",
        default=str(Path(__file__).parent / "script-credentials.json"),
        help="Path to service account credentials JSON file (default: scripts/script-credentials.json)",
    )
    args = parser.parse_args()

    sheet_id = args.sheet_id
    credentials_file = args.credentials

    # Check if credentials file exists
    if not Path(credentials_file).exists():
        print(f"Credentials file not found: {credentials_file}", file=sys.stderr)
        sys.exit(1)

    # Authenticate with Google Sheets
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]
    client = gspread.service_account(filename=credentials_file, scopes=SCOPES)
    spreadsheet = client.open_by_key(sheet_id)

    # Open the spreadsheet
    sheet = spreadsheet.get_worksheet_by_id(1362804576)  # Assume first sheet

    # Get all values
    data = sheet.get_all_values()

    if not data:
        print("No data in spreadsheet", file=sys.stderr)
        sys.exit(1)

    # Assume first row is headers
    headers = data[0]
    required_headers = [
        "Full Name",
        "First Name",
        "Last Name",
        "Email",
        "Status",
        "Affiliations",
        "Contributions",
        "Skills",
        "Last Activity",
    ]
    headers_set = set(headers)
    required_headers_set = set(required_headers)
    if not required_headers_set.issubset(headers_set):
        print(
            f"Missing required headers: {list(required_headers_set - headers_set)}",
            file=sys.stderr,
        )
        sys.exit(1)

    headers_dict = get_indices_dict(headers, required_headers)
    print(headers_dict)

    # Parse rows
    members = []
    for row in data[1:]:
        if not row[headers_dict["Full Name"]].strip():  # Skip empty name rows
            continue
        name = row[headers_dict["Full Name"]].strip()
        email = row[headers_dict["Email"]].strip()  # Not used in JSON
        status = row[headers_dict["Status"]].strip()
        affiliations = [
            a.strip()
            for a in split(r"\n|; ", row[headers_dict["Affiliations"]])
            if a.strip()
        ]
        contributions = [
            c.strip()
            for c in split(r"\n|; ", row[headers_dict["Contributions"]])
            if c.strip()
        ]
        skills = row[headers_dict["Skills"]].strip()  # Not used
        last_activity = row[headers_dict["Last Activity"]].strip()  # Not used

        member = {
            "name": name,
            "email": email,
            "affiliations": affiliations,
            "contributions": contributions,
            "status": status,
            "skills": skills,
            "last_activity": last_activity,
        }
        members.append(member)

    members = sorted(members, key=lambda x: order_priority[x["status"]])

    # Write to JSON
    repo_root = Path(__file__).parent.parent
    json_path = repo_root / "about" / "members.json"
    with open(json_path, "w") as f:
        json.dump(members, f, indent=2, ensure_ascii=False)
    print(f"Wrote {json_path} ({len(members)} records)")

    # Create Excel
    excel_path = repo_root / "about" / "members.xlsx"
    update_members_excel(members, excel_path)

    # Update Markdown
    update_members_md()


if __name__ == "__main__":
    main()
