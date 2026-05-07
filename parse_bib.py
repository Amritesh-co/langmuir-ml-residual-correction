import re

with open('/Users/ignite/College/IDP/docs/PROJECT_REFERENCES.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

bib_entries = []
for line in lines:
    if line.startswith('> '):
        line = line[2:].strip()
        match = re.match(r'^(.*?)\s*\((.*?)\)\.\s*\*\*(.*?)\*\*(?:\s*\*([^*]+)\*)?', line)
        if match:
            author = match.group(1).strip()
            year = match.group(2).strip()
            title = match.group(3).strip()
            journal = match.group(4).strip() if match.group(4) else "Unknown Journal"
            
            if "World Health Organization" in author:
                author = "{World Health Organization}"
            
            title = title.rstrip('.')
            
            bib_id = author.split(',')[0].split(' ')[0]
            bib_id = re.sub(r'[^A-Za-z0-9]', '', bib_id) + year
            if not bib_id: bib_id = "Unknown" + year
            
            try:
                y_int = int(re.search(r'\d{4}', year).group())
            except:
                y_int = 0
                
            bib_entries.append({
                'id': bib_id,
                'author': author,
                'year_int': y_int,
                'year': year,
                'title': title,
                'journal': journal
            })

import os
with open('/Users/ignite/College/IDP/IDP-REPORT/source/AuxFiles/ProjectBib.bib', 'r', encoding='utf-8') as f:
    existing_bib = f.read()

existing_entries = []
current_entry = {}
for line in existing_bib.split('\n'):
    line = line.strip()
    if line.startswith('@'):
        if current_entry:
            existing_entries.append(current_entry)
        current_entry = {'raw': line + '\n'}
        match = re.search(r'@.*\{(.*),', line)
        if match:
            current_entry['id'] = match.group(1)
    elif current_entry:
        current_entry['raw'] += line + '\n'
        if line.startswith('year'):
            match = re.search(r'year\s*=\s*\{(\d+)\}', line)
            if match:
                current_entry['year_int'] = int(match.group(1))

if current_entry:
    existing_entries.append(current_entry)

titles_seen = set()
merged_entries = []

for e in existing_entries:
    title_match = re.search(r'title\s*=\s*\{(.*?)\}', e['raw'])
    title = title_match.group(1).lower().replace(' ', '') if title_match else ""
    if title not in titles_seen:
        titles_seen.add(title)
        merged_entries.append({
            'year_int': e.get('year_int', 0),
            'raw': e['raw']
        })

bib_ids = set([e.get('id') for e in existing_entries])

for e in bib_entries:
    title_key = e['title'].lower().replace(' ', '')
    if title_key not in titles_seen:
        titles_seen.add(title_key)
        
        b_id = e['id']
        counter = 1
        while b_id in bib_ids:
            b_id = f"{e['id']}{counter}"
            counter += 1
        bib_ids.add(b_id)
        
        raw = f"@article{{{b_id},\n\tauthor  = {{{e['author']}}},\n\ttitle   = {{{e['title']}}},\n\tjournal = {{{e['journal']}}},\n\tyear    = {{{e['year']}}}\n}}\n\n"
        merged_entries.append({
            'year_int': e['year_int'],
            'raw': raw
        })

merged_entries.sort(key=lambda x: x['year_int'], reverse=True)

with open('/Users/ignite/College/IDP/IDP-REPORT/source/AuxFiles/ProjectBib.bib', 'w', encoding='utf-8') as f:
    for e in merged_entries:
        f.write(e['raw'].strip() + '\n\n')

print(f"Total merged entries: {len(merged_entries)}")
