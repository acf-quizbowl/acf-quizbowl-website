#!/usr/bin/env python3
"""Sort the member tables in about/members.md by surname and add letter markers.

This script processes each <table class="table-ruled member-list" ...> in
about/members.md. It sorts the <tr> rows inside the <tbody> by the surname
(found in the first <td> in each row) and inserts HTML comments of the form
<!-- X --> before the first row of any group whose surname begins with the
letter X. The file is modified in place.

Usage:
    ./scripts/sort_members.py
"""

import re
from pathlib import Path

MEMBERS_PATH = Path(__file__).parent.parent / "about" / "members.md"


def extract_rows(tbody_text: str) -> list[str]:
    """Return a list of <tr>...</tr> blocks from the tbody text."""
    # simple regex capturing each row including its content
    row_regex = re.compile(r"(<tr>.*?</tr>)", re.DOTALL)
    return row_regex.findall(tbody_text)


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


def sort_and_annotate(rows: list[str]) -> str:
    """Sort rows by surname and return annotated tbody content."""
    # pair with surname initial
    keyed = sorted(rows, key=lambda r: surname_from_row(r))
    output_lines = []
    last_initial = None
    for row in keyed:
        surname = surname_from_row(row)
        initial = surname[:1] if surname else ""
        if initial != last_initial:
            # insert comment marker
            output_lines.append(f"<!-- {initial} -->")
            last_initial = initial
        output_lines.append(row)
    # join with newline
    return "\n".join(output_lines)


def process_file(path: Path) -> None:
    text = path.read_text()
    # regex to match a table and capture tbody content
    table_regex = re.compile(
        r"(<table[^>]*class=\"table-ruled member-list\"[^>]*>.*?<tbody>)(.*?)(</tbody>)(.*?</table>)",
        re.DOTALL,
    )

    def replacer(match):
        prefix = match.group(1)
        tbody = match.group(2)
        suffix = match.group(3)
        tail = match.group(4)
        rows = extract_rows(tbody)
        if not rows:
            return match.group(0)
        new_tbody = sort_and_annotate(rows)
        # ensure indentation consistent with original (4 spaces)
        indented = "\n".join("    " + line for line in new_tbody.splitlines())
        return prefix + "\n" + indented + "\n" + suffix + tail

    new_text = table_regex.sub(replacer, text)
    path.write_text(new_text)


if __name__ == "__main__":
    process_file(MEMBERS_PATH)
    print(f"Updated {MEMBERS_PATH}")
