import re

with open('/Users/ignite/College/IDP/IDP-REPORT/source/AuxFiles/ProjectBib.bib', 'r', encoding='utf-8') as f:
    content = f.read()

entries = []
current_entry = {}
for line in content.split('\n'):
    line = line.strip()
    if line.startswith('@'):
        if current_entry:
            entries.append(current_entry)
        current_entry = {'raw': line + '\n'}
        match = re.search(r'@.*\{(.*),', line)
        if match:
            current_entry['id'] = match.group(1)
    elif current_entry:
        current_entry['raw'] += line + '\n'
        if line.startswith('year'):
            match = re.search(r'year\s*=\s*\{(\d+)\}', line)
            if match:
                current_entry['year'] = int(match.group(1))
        if line.startswith('author'):
            match = re.search(r'author\s*=\s*\{(.*?)\}', line)
            if match:
                current_entry['author'] = match.group(1)
        if line.startswith('title'):
            match = re.search(r'title\s*=\s*\{(.*?)\}', line)
            if match:
                current_entry['title'] = match.group(1)

if current_entry:
    entries.append(current_entry)

for e in entries:
    # parse first author family name
    author = e.get('author', '')
    author = author.replace('{', '').replace('}', '')
    first_author = author.split(' and ')[0].strip()
    family_name = first_author.split(',')[0].strip()
    e['sort_name'] = family_name.lower()
    e['sort_title'] = e.get('title', '').lower()
    e['sort_year'] = e.get('year', 0)

# ydnt sort: year descending, name ascending, title ascending
entries.sort(key=lambda x: (-x['sort_year'], x['sort_name'], x['sort_title']))

to_remove = [3, 6, 15, 16, 18, 20, 21, 24, 26, 29, 30, 32, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 51]
keep_titles = [
    "modification of chitosan-coated magnetic material for enhanced adsorption performance",
    "fluoride removal using ce/al/fe tri-metal oxide modified diatomaceous earth",
    "fluoride adsorption using thermally activated kaolin clay and limestone",
    "pei–gtmac functionalized biomass adsorbents for enhanced anion removal",
    "gtmac quaternization of chitosan in ionic liquid for improved adsorption",
    "fluoride removal from water using activated alumina",
    "insight into biosorptive uptake of fluoride by chemically activated biochar: experimental modeling and parametric optimization",
    "synthesis and investigation of gtmac modified biomass adsorbents for anionic pollutant removal",
    "a sustainable approach for fluoride treatment using coconut fiber cellulose as an adsorbent"
]

final_entries = []
for i, e in enumerate(entries):
    idx = i + 1
    t = e['sort_title'].replace('--', '–')  # normalize dashes
    is_keep_title = any(kt in t for kt in keep_titles) or any(t in kt for kt in keep_titles)
    
    if idx in to_remove and not is_keep_title:
        # print(f"Removing [{idx}]: {e.get('title')}")
        pass
    else:
        final_entries.append(e)

with open('/Users/ignite/College/IDP/IDP-REPORT/source/AuxFiles/ProjectBib.bib', 'w', encoding='utf-8') as f:
    for e in final_entries:
        f.write(e['raw'].strip() + '\n\n')

print(f"Total entries kept: {len(final_entries)}")
