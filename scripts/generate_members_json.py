#!/usr/bin/env python3
"""Generate JSON file for the member tables in `about/members.md`.

This script reads the markdown source, converts it to HTML, and then
scrapes the three tables (identified by their IDs) to produce a single
`members.json` file in the `about/` directory with a status field added
to each entry.

Usage:
    python3 scripts/generate_members_json.py

Dependencies:
    pip install markdown beautifulsoup4
"""
import json
import os
import sys

from bs4 import BeautifulSoup
import markdown


def table_to_json(table):
    """Convert a BeautifulSoup `<table>` element to a list of dicts."""
    # header row
    header_cells = table.find('tr').find_all('th')
    headers = [th.get_text(strip=True).lower() for th in header_cells]

    rows = []
    for tr in table.find_all('tr')[1:]:
        tds = tr.find_all('td')
        if not tds:
            continue
        entry = {}
        for key, td in zip(headers, tds):
            if key == 'name':
                # Name is always a string
                entry[key] = td.get_text(strip=True)
            else:
                # Affiliations and contributions: always store as a list
                ul = td.find('ul')
                if ul:
                    items = [li.get_text(strip=True) for li in ul.find_all('li')]
                    # filter out empty strings
                    items = [i for i in items if i]
                    entry[key] = items
                else:
                    text = td.get_text(strip=True)
                    if text:
                        entry[key] = [text]
                    else:
                        entry[key] = []
        rows.append(entry)
    return rows


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    md_path = os.path.join(repo_root, 'about', 'members.md')
    if not os.path.isfile(md_path):
        print(f"could not find {md_path}", file=sys.stderr)
        sys.exit(1)

    with open(md_path, 'r') as f:
        md = f.read()

    # convert markdown to HTML so we can take advantage of .. tags
    html = markdown.markdown(md, extensions=['tables'])
    soup = BeautifulSoup(html, 'html.parser')

    # JSON now lives in the top-level about directory rather than a
    # subfolder.  Historically we wrote to `about/members/` but the
    # file has been moved up one level.
    outdir = os.path.join(repo_root, 'about')
    os.makedirs(outdir, exist_ok=True)

    mapping = {
        'full-member-table': 'full',
        'provisional-member-table': 'provisional',
        'emeritus-member-table': 'emeritus',
    }

    all_data = []
    for table_id, status in mapping.items():
        table = soup.find('table', id=table_id)
        if table is None:
            print(f"warning: table with id '{table_id}' not found", file=sys.stderr)
            continue

        data = table_to_json(table)
        # Add status to each entry
        for entry in data:
            entry['status'] = status
        all_data.extend(data)

    outpath = os.path.join(outdir, 'members.json')
    with open(outpath, 'w') as outf:
        json.dump(all_data, outf, indent=2, ensure_ascii=False)
    print(f"wrote {outpath} ({len(all_data)} records)")


if __name__ == '__main__':
    main()
