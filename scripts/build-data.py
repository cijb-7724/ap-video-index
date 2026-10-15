"""Rebuild the index from the audited playlist + channel video catalog."""
import json
import pathlib
import re
import unicodedata

root = pathlib.Path(__file__).resolve().parents[1]
catalog = json.loads((root / 'scripts/source-videos.json').read_text())
sources = json.loads((root / 'scripts/playlists.json').read_text())
rows = {}
for year in range(4, 8):
    for season in ('春', '秋'):
        rows[(year, season)] = {'year': year + 2018, 'label': f'令和{year}年{season}', 'season': season, 'morning': {}, 'afternoon': {}, 'summaries': []}
excluded = []
for video in catalog:
    title = unicodedata.normalize('NFKC', video['title'])
    playlist_title = unicodedata.normalize('NFKC', video['playlistTitle'])
    match = re.search(r'令和\s*(\d+)\s*年?\s*(春|秋)', title)
    if not match:
        match = re.search(r'令和\s*(\d+)\s*年?\s*(春|秋)', playlist_title)
    if not match or (int(match[1]), match[2]) not in rows:
        continue
    if '応用情報' not in title or any(term in title for term in ('短編映画', '実写', '再現して', '実写化')):
        excluded.append({'id': video['id'], 'title': video['title']})
        continue
    row = rows[(int(match[1]), match[2])]
    url = f"https://www.youtube.com/watch?v={video['id']}"
    if video['playlist']:
        url += '&list=' + video['playlist']
    exam = 'afternoon' if '午後' in title or '午後' in playlist_title else 'morning'
    question = re.search(r'問\s*(\d+)(?:\s*[〜~～\-]\s*(?:問)?\s*(\d+))?', title)
    if not question:
        question = re.search(r'午後\s*(\d+)', title)
    if not question:
        if '解答速報' in title and not any(v['id'] == video['id'] for v in row['summaries']):
            row['summaries'].append({'id': video['id'], 'title': video['title'], 'url': url})
        continue
    first = int(question[1])
    last = int(question[2] or first) if len(question.groups()) > 1 else first
    limit = 11 if exam == 'afternoon' else 80
    if not 1 <= first <= last <= limit:
        raise ValueError(video)
    priority = 0 if first != last else 1 if '解答速報' in title else 2
    for number in range(first, last + 1):
        previous = row[exam].get(str(number))
        if previous is None or priority > previous['priority']:
            row[exam][str(number)] = {'id': video['id'], 'title': video['title'], 'url': url, 'grouped': first != last, 'priority': priority}
data = {'updated': '2026-10-15', 'rows': sorted(rows.values(), key=lambda row: (row['year'], row['season'] == '秋'), reverse=True), 'otherPlaylists': [s for s in sources if '応用情報' not in s['title']]}
(root / 'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
(root / 'scripts/excluded.json').write_text(json.dumps(excluded, ensure_ascii=False, indent=2) + '\n')
for row in data['rows']:
    print(row['label'], '午前', len(row['morning']), '/ 80', '午後', len(row['afternoon']), '/ 11')
