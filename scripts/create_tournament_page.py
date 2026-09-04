#!/usr/bin/env python3
"""Create ACF tournament pages from the reusable Markdown templates.

Edit the uncommented entries in ``TOURNAMENTS`` below, then run this script
without arguments to create every configured tournament. Each entry needs a
year, date, head editor(s), HSQB forums URL, and a mirror-forum readiness flag.
Use ``--dry-run`` to preview changes; existing pages are never overwritten.
Positional ``TOURNAMENT YEAR`` pairs can optionally override configured years
for one run.
"""

import argparse
import re
from datetime import date
from pathlib import Path

# Add or uncomment tournament entries here. Commented entries are not created.
TOURNAMENTS = {
    # "fall": {
    #     "year": 2026,
    #     "date": "October 17, 2026",
    #     "head_editors": "Noah Chin",
    #     "forums_url": "https://hsquizbowl.org/forums/viewtopic.php?t=30232",
    #     "mirror_forums_ready": False,
    # },
    # "winter": {
    #     "year": 2026,
    #     "date": "November 14, 2026",
    #     "head_editors": "Ben Chapman",
    #     "forums_url": "https://hsquizbowl.org/forums/viewtopic.php?t=30250",
    #     "mirror_forums_ready": False,
    # },
    # "regionals": {
    #     "year": 2027,
    #     "date": "January 30, 2027",
    #     "head_editors": "Shahar Schwartz",
    #     "forums_url": "https://hsquizbowl.org/forums/viewtopic.php?t=30344",
    #     "mirror_forums_ready": False,
    # },
    "nationals": {
        "year": 2027,
        "date": "Date TBA, 2027",
        "head_editors": "Eve Fleisig",
        "forums_url": "https://hsquizbowl.org/forums/viewtopic.php?t=30235",
        "mirror_forums_ready": False,
    },
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "combinations",
        nargs="*",
        metavar="TOURNAMENT YEAR",
        help="One or more tournament/year pairs, for example: fall 2026 winter 2026",
    )
    parser.add_argument("--last-updated", default=date.today().strftime("%B %-d, %Y"))
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print paths without writing",
    )
    return parser.parse_args()


def requested_tournaments(combinations):
    if not combinations:
        return [
            (tournament, details["year"]) for tournament, details in TOURNAMENTS.items()
        ]
    if len(combinations) % 2:
        raise ValueError(
            "Tournament arguments must be supplied in TOURNAMENT YEAR pairs"
        )

    requested = []
    for index in range(0, len(combinations), 2):
        tournament = combinations[index]
        if tournament not in TOURNAMENTS:
            raise ValueError(f"Unknown tournament: {tournament}")
        try:
            year = int(combinations[index + 1])
        except ValueError as error:
            raise ValueError(f"Invalid year: {combinations[index + 1]}") from error
        requested.append((tournament, year))
    return requested


def replace_metadata(
    template,
    year,
    previous_year_offset,
    tournament_date,
    last_updated,
    head_editors,
    forums_url,
    mirror_forums_ready,
):
    forum_number = re.search(r"[?&]t=(\d+)", forums_url)
    if forum_number is None:
        raise ValueError(f"Forums URL does not contain a topic number: {forums_url}")

    rendered = (
        template.replace("__YEAR__", str(year))
        .replace("__PREVIOUS_YEAR__", str(year + previous_year_offset))
        .replace("__DATE__", tournament_date)
        .replace("__LAST_UPDATED__", last_updated)
        .replace("__HEAD_EDITORS__", head_editors)
        .replace("__ANNOUNCEMENT_FORUMS_NUMBER__", forum_number.group(1))
    )
    if not mirror_forums_ready:
        rendered = re.sub(
            r"\[(__SITE__)\]\(https://hsquizbowl\.org/forums/viewtopic\.php\?t=__MIRROR_FORUMS_NUMBER_\d+__\)",
            r"\1",
            rendered,
        )
    return rendered


def update_index(index_path, year, display_name):
    contents = index_path.read_text()
    link = f"**[{year} {display_name}]({year})**"
    marker = "\n## Past Tournaments\n"
    if marker not in contents:
        raise ValueError(f"Could not find the archive marker in {index_path}")

    before_past, after_past = contents.split(marker, 1)
    current_pattern = re.compile(
        rf"^\*\*\[\d+ {re.escape(display_name)}\]\(\d+\)\*\*\n?",
        re.MULTILINE,
    )
    current_match = current_pattern.search(before_past)
    if current_match is not None:
        old_link = current_match.group(0).strip()
        if old_link == link:
            return contents
        before_past = (
            before_past[: current_match.start()] + before_past[current_match.end() :]
        )
    else:
        old_link = None

    if link in before_past:
        return contents
    before_past = before_past.rstrip() + f"\n\n{link}\n"

    if old_link is not None:
        past_link = re.sub(r"^\*\*|\*\*$", "", old_link)
        if past_link not in after_past:
            archive_marker = (
                f"Announcements and information about previous iterations of "
                f"{display_name} are archived below:\n\n"
            )
            if archive_marker not in after_past:
                raise ValueError(
                    f"Could not find the past-tournament list in {index_path}"
                )
            after_past = after_past.replace(
                archive_marker, f"{archive_marker}* {past_link}\n", 1
            )

    return before_past + marker + after_past


def update_home_date(contents, slug, tournament_date):
    pattern = re.compile(
        rf'(<div class="tournament-card\b[^>]*>\s*<span class="date">)[^<]*'
        rf'(</span>(?:(?!<div class="tournament-card\b).)*?'
        rf'<h2><a href="/tournaments/{re.escape(slug)}/)',
        re.DOTALL,
    )
    updated, replacements = pattern.subn(
        rf"\g<1>{tournament_date}\g<2>", contents, count=1
    )
    if replacements == 0:
        raise ValueError(f"Could not find the {slug} date panel in _layouts/home.html")
    return updated


def placeholder_types(contents):
    placeholders = re.findall(r"__[A-Z][A-Z0-9_]*__", contents)
    return sorted(
        {re.sub(r"_\d+__", "_X__", placeholder) for placeholder in placeholders}
    )


def print_placeholders(placeholders):
    print("Placeholders to update:")
    if placeholders:
        for placeholder in placeholders:
            print(f"  {placeholder}")
    else:
        print("  (none)")


def get_clone_details(root, tournament, year, last_updated):
    tournament_details = {
        **TOURNAMENT_DEFAULTS[tournament],
        **TOURNAMENTS[tournament],
    }
    folder = tournament_details["folder"]
    display_name = tournament_details["display_name"]
    slug = tournament_details["slug"]
    template_path = root / "tournaments" / folder / f"{slug}_template.md"
    season_start_year = year + tournament_details["season_start_offset"]
    season = f"{season_start_year}-{str(season_start_year + 1)[-2:]}"
    destination_dir = root / "tournaments" / folder / season
    destination_path = destination_dir / f"{year}-{slug}.md"
    index_path = root / "tournaments" / folder / f"{slug}.md"

    if not template_path.is_file():
        raise FileNotFoundError(f"Template not found: {template_path}")
    if destination_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing tournament: {destination_path}"
        )

    rendered = replace_metadata(
        template_path.read_text(),
        year,
        tournament_details["previous_year_offset"],
        tournament_details["date"],
        last_updated,
        tournament_details["head_editors"],
        tournament_details["forums_url"],
        tournament_details["mirror_forums_ready"],
    )
    updated_index = update_index(index_path, year, display_name)
    return (
        destination_dir,
        destination_path,
        index_path,
        rendered,
        updated_index,
        slug,
        tournament_details["date"],
        placeholder_types(rendered),
    )


TOURNAMENT_DEFAULTS = {
    "fall": {
        "folder": "1_fall",
        "display_name": "ACF Fall",
        "slug": "fall",
        "season_start_offset": 0,
        "previous_year_offset": -1,
    },
    "winter": {
        "folder": "2_winter",
        "display_name": "ACF Winter",
        "slug": "winter",
        "season_start_offset": 0,
        "previous_year_offset": -1,
    },
    "regionals": {
        "folder": "3_regionals",
        "display_name": "ACF Regionals",
        "slug": "regionals",
        "season_start_offset": -1,
        "previous_year_offset": -2,
    },
    "nationals": {
        "folder": "4_nationals",
        "display_name": "ACF Nationals",
        "slug": "nationals",
        "season_start_offset": -1,
        "previous_year_offset": -2,
    },
}


def main():
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    clones = [
        get_clone_details(root, tournament, year, args.last_updated)
        for tournament, year in requested_tournaments(args.combinations)
    ]
    home_path = root / "_layouts" / "home.html"
    home_contents = home_path.read_text()
    updated_home = home_contents
    for clone in clones:
        updated_home = update_home_date(updated_home, clone[5], clone[6])

    if args.dry_run:
        for _, destination_path, index_path, _, _, _, _, placeholders in clones:
            print(f"Would create {destination_path}")
            print(f"Would update {index_path}")
            print_placeholders(placeholders)
        if updated_home != home_contents:
            print(f"Would update {home_path}")
        return

    for (
        destination_dir,
        destination_path,
        index_path,
        rendered,
        updated_index,
        _,
        _,
        placeholders,
    ) in clones:
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(rendered)
        index_path.write_text(updated_index)
        print(f"Created {destination_path}")
        print(f"Updated {index_path}")
        print_placeholders(placeholders)
    if updated_home != home_contents:
        home_path.write_text(updated_home)
        print(f"Updated {home_path}")


if __name__ == "__main__":
    main()
