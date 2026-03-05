# Reorders contributions by year and places year(s) at the front of each contribution item instead of at the end.
import re

def expand_year(year_str):
    if '-' not in year_str:
        return year_str
    parts = year_str.split('-')
    if len(parts) != 2:
        return year_str
    start, end = parts
    start = int(start)
    if len(end) == 2 and end.isdigit():
        end_num = int(end)
        if end_num < start % 100:
            end = str((start // 100) * 100 + end_num)
        else:
            end = str(start // 100 * 100 + end_num)
    return f"{start}-{end}"

def process_li(text):
    text = text.strip()
    # check if already starts with year
    if re.match(r'\d{4}', text):
        return text
    # find ", year" at end
    match = re.search(r', (\d{4}(?:-\d{2,4})?(?:-Present|-present)?)$', text)
    if match:
        year = match.group(1)
        year = expand_year(year)
        rest = text[:match.start()].strip()
        return f"{year}, {rest}"
    return text

def parse_sort_key(text):
    if not text.strip():
        return 9999
    match = re.match(r'(\d{4})(?:-(\d{2,4}))?(?:-Present|-present)?', text)
    if match:
        start = int(match.group(1))
        return start
    else:
        return 9999

# read file
with open('/Users/ap/Documents/AP/APMISC/quizbowl/acf/acf-quizbowl.github.io/about/members.md', 'r') as f:
    content = f.read()

# find all <tr> blocks
tr_pattern = r'(<tr>\n    <td>.*?</td>\n    <td>\n        <ul>\n(?:            <li>.*?</li>\n)+        </ul>\n    </td>\n    <td>\n        <ul>\n(?:            <li>.*?</li>\n)+        </ul>\n    </td>\n</tr>)'

def replace_tr(match):
    tr_block = match.group(1)
    # split into parts
    parts = re.split(r'(<td>\n        <ul>\n(?:            <li>.*?</li>\n)+        </ul>\n    </td>)', tr_block)
    # parts[0] is before first td, parts[1] affiliations td, parts[2] between, parts[3] contributions td, parts[4] after
    affiliations_td = parts[1]
    contributions_td = parts[3]
    # process contributions_td
    li_pattern = r'<li>(.*?)</li>'
    lis = re.findall(li_pattern, contributions_td)
    processed_lis = [process_li(li) for li in lis]
    processed_lis.sort(key=parse_sort_key)
    ul_content = '\n'.join(f'            <li>{li}</li>' for li in processed_lis)
    new_contributions_td = f'<td>\n        <ul>\n{ul_content}\n        </ul>\n    </td>'
    new_tr = parts[0] + affiliations_td + parts[2] + new_contributions_td + parts[4]
    return new_tr

new_content = re.sub(tr_pattern, replace_tr, content, flags=re.DOTALL)

# write back
with open('/Users/ap/Documents/AP/APMISC/quizbowl/acf/acf-quizbowl.github.io/about/members.md', 'w') as f:
    f.write(new_content)

print("Done")