#!/usr/bin/env python3
"""Regenerate HTML member tables from JSON and clean/sort entries.

This tool complements the `generate_members_json.py` script by consuming the
resulting JSON file and rewriting the corresponding HTML tables in
`about/members.md`.  It performs the same operations that the previous
separate scripts did:

* clean contribution strings (move years to front, expand abbreviated ranges),
* sort contributions chronologically,
* sort rows by member surname and insert alphabetical HTML comments,
* update the markdown source in place.

Usage
-----
    python3 scripts/update_members.py

Dependencies
------------
None beyond the standard library (json, re, pathlib).

The script expects the JSON file to be named:

    about/members.json

If the directory or file is missing a warning is printed and the script
skips them.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

# constants
REPO_ROOT = Path(__file__).parent.parent
MEMBERS_MD = REPO_ROOT / "about" / "members.md"
JSON_DIR = REPO_ROOT / "about"

TABLE_FILES = {
    "full-member-table": "full",
    "provisional-member-table": "provisional",
    "emeritus-member-table": "emeritus",
}


# ---------------------------------------------------------------------------
# contribution-cleaning helpers (from scripts/clean_members.py)
# ---------------------------------------------------------------------------

def expand_year(year_str: str) -> str:
    if "-" not in year_str:
        return year_str
    parts = year_str.split("-")
    if len(parts) != 2:
        return year_str
    start, end = parts
    try:
        start_i = int(start)
    except ValueError:
        return year_str
    # handle two-digit end
    if len(end) == 2 and end.isdigit():
        end_num = int(end)
        if end_num < start_i % 100:
            end = str((start_i // 100) * 100 + end_num)
        else:
            end = str(start_i // 100 * 100 + end_num)
    return f"{start_i}-{end}"


def process_li(text: str) -> str:
    text = text.strip()
    # already starts with year?
    if re.match(r"\d{4}", text):
        return text
    # look for ", year" at end
    match = re.search(r", (\d{4}(?:-\d{2,4})?(?:-Present|-present)?)$", text)
    if match:
        year = match.group(1)
        year = expand_year(year)
        rest = text[: match.start()].strip()
        return f"{year}, {rest}"
    return text


def parse_sort_key(text: str) -> int:
    if not text.strip():
        return 9999
    match = re.match(r"(\d{4})(?:-(\d{2,4}))?(?:-Present|-present)?", text)
    if match:
        return int(match.group(1))
    else:
        return 9999


# ---------------------------------------------------------------------------
# sorting helpers (adapted from scripts/sort_members.py)
# ---------------------------------------------------------------------------

def surname_from_row(row: str) -> str:
    """Extract the surname (last word) from the first <td> in a row."""
    # find first <td>...</td>
    m = re.search(r"<td>(.*?)</td>", row, re.DOTALL)
    if not m:
        return ""
    name = m.group(1).strip()
    # take last space-separated token
    parts = name.split()
    return parts[-1].upper() if parts else ""


def sort_and_annotate(rows: List[str]) -> str:
    """Sort rows by surname and return annotated tbody content."""
    # pair with surname initial
    keyed = sorted(rows, key=lambda r: surname_from_row(r))
    output_lines: List[str] = []
    last_initial: str | None = None
    for row in keyed:
        initial = surname_from_row(row)[:1]
        if initial != last_initial:
            # insert comment marker
            output_lines.append(f"<!-- {initial} -->")
            last_initial = initial
        output_lines.append(row)
    # join with newline
    return "\n".join(output_lines)


# ---------------------------------------------------------------------------
# row generation
# ---------------------------------------------------------------------------

def make_row(entry: Dict[str, Any]) -> str:
    """Return a <tr> block for a member entry.

    The `entry` dictionary has keys 'name', 'affiliations', and 'contributions'.
    Both 'affiliations' and 'contributions' may be:
    - a list of strings (rendered as a <ul> with <li> items)
    - a single string (rendered as plain text in the <td>)
    - empty list/empty string/None (rendered as empty <td></td>)
    """
    name = entry.get("name", "")
    if isinstance(name, list):
        name = name[0] if name else ""
    name = name.strip("[]'\"")
    affs_raw = entry.get("affiliations", [])
    contribs_raw = entry.get("contributions", [])

    # Helper to build a cell from data that could be string, list, or empty
    def build_cell_content(raw_data, is_contrib: bool = False) -> str:
        """Build HTML for a cell (affiliation or contribution).

        Returns the inner HTML for a <td> element:
        - For a list with one item: the item as plaintext
        - For a list with multiple items: <ul>...</ul>
        - For empty: empty string
        """
        # Normalize to a list of strings
        if isinstance(raw_data, str):
            items = [raw_data] if raw_data.strip() else []
        elif isinstance(raw_data, list):
            items = [x for x in (raw_data or []) if x]
        else:
            items = []

        if not items:
            # Empty cell
            return ""

        # If single item, return indented plaintext
        if len(items) == 1:
            return f"        {items[0].strip()}"

        # Multiple items: render as <ul>
        if is_contrib:
            # Clean and sort contributions
            cleaned = [process_li(c) for c in items]
            cleaned.sort(key=parse_sort_key)
        else:
            # Affiliations: just strip whitespace
            cleaned = [c.strip() for c in items if c.strip()]

        if not cleaned:
            return ""

        li_lines = ["        <ul>"]
        for item in cleaned:
            li_lines.append(f"            <li>{item}</li>")
        li_lines.append("        </ul>")
        return "\n".join(li_lines)

    aff_content = build_cell_content(affs_raw, is_contrib=False)
    contrib_content = build_cell_content(contribs_raw, is_contrib=True)

    # Build affiliation cell
    if aff_content:
        aff_cell = f"    <td>\n{aff_content}\n    </td>\n"
    else:
        aff_cell = "    <td></td>\n"

    # Build contribution cell
    if contrib_content:
        contrib_cell = f"    <td>\n{contrib_content}\n    </td>\n"
    else:
        contrib_cell = "    <td></td>\n"

    row = (
        "<tr>\n"
        f"    <td>{name}</td>\n"
        + aff_cell
        + contrib_cell
        + "</tr>"
    )
    return row


# ---------------------------------------------------------------------------
# table replacement
# ---------------------------------------------------------------------------

def generate_tbody(entries: List[Dict[str, Any]]) -> str:
    rows = [make_row(e) for e in entries]
    annotated = sort_and_annotate(rows)
    # indent each line by 4 spaces, matching existing file style
    indented = "\n".join("    " + line for line in annotated.splitlines())
    return indented


def update_members_md():
    if not MEMBERS_MD.exists():
        print(f"{MEMBERS_MD} does not exist")
        return
    text = MEMBERS_MD.read_text()

    json_path = JSON_DIR / "members.json"
    if not json_path.exists():
        print(f"warning: {json_path} missing")
        return
    with open(json_path, 'r') as jf:
        all_entries = json.load(jf)
        if not isinstance(all_entries, list):
            print(f"warning: {json_path} does not contain a list")
            return

    for table_id, status in TABLE_FILES.items():
        entries = [e for e in all_entries if e.get('status') == status]
        # Remove status from entries for processing
        for e in entries:
            e.pop('status', None)

        new_body = generate_tbody(entries)

        # regex to replace tbody content
        pattern = re.compile(
            rf"(<table[^>]*id=\"{table_id}\"[^>]*>.*?<tbody>)(.*?)(</tbody>)(.*?</table>)",
            re.DOTALL,
        )

        def repl(m):
            prefix = m.group(1)
            suffix = m.group(3)
            tail = m.group(4)
            return f"{prefix}\n{new_body}\n{suffix}{tail}"

        text = pattern.sub(repl, text)
        print(f"replaced table {table_id} ({len(entries)} entries)")

    MEMBERS_MD.write_text(text)
    print(f"updated {MEMBERS_MD}")


if __name__ == '__main__':
    update_members_md()
