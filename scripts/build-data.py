"""Build a static index from yt-dlp flat-playlist JSON (Japanese titles)."""
import json
import pathlib
import re
import sys
import unicodedata

root = pathlib.Path(__file__).resolve().parents[1]
sources = json.loads((root / 'scripts/playlists.json').read_text())
rows = {}
others = []
excluded = []
for source in sources:
    playlist = json.loads((pathlib.Path(sys.argv[1]) / (source['id'] + '.json')).read_text())
    name = unicodedata.normalize('NFKC', playlist['title'])
    if '応用情報' not in name:
        others.append(source)
        continue
    year = int(re.search(r'令和\s*(\d+)', name)[1])
    season = '秋' if '秋' in name else '春'
    key = f'{year}-{season}'
    row = rows.setdefault(key, {'year': year + 2018, 'label': f'令和{year}年{season}', 'season': season, 'morning': {}, 'afternoon': {}, 'playlists': [], 'summaries': []})
    row['playlists'].append(source)
    for video in playlist['entries']:
        title = unicodedata.normalize('NFKC', video['title'])
        url = f"https://www.youtube.com/watch?v={video['id']}&list={source['id']}"
        if '解答速報' in title:
            row['summaries'].append({'title': video['title'], 'url': url})
            continue
        if '応用情報' not in title:
            excluded.append({'id': video['id'], 'title': video['title'], 'reason': '試験問題の解説ではない動画'})
            continue
        exam = 'afternoon' if '午後' in title or '午後' in name else 'morning'
        match = re.search(r'問\s*(\d+)(?:\s*[〜~～\-]\s*(?:問)?\s*(\d+))?', title)
        if not match:
            match = re.search(r'午後\s*(\d+)', title)
        if not match:
            excluded.append({'id': video['id'], 'title': video['title'], 'reason': '問題番号を特定できない動画'})
            continue
        first = int(match[1]); last = int(match[2] or first) if len(match.groups()) > 1 else first
        for number in range(first, last + 1):
            item = {'id': video['id'], 'title': video['title'], 'url': url, 'grouped': first != last}
            previous = row[exam].get(str(number))
            if previous is None or (previous['grouped'] and not item['grouped']):
                row[exam][str(number)] = item
data = {'updated': '2026-10-15', 'rows': sorted(rows.values(), key=lambda row: (row['year'], row['season'] == '秋'), reverse=True), 'otherPlaylists': others}
(root / 'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
(root / 'scripts/excluded.json').write_text(json.dumps(excluded, ensure_ascii=False, indent=2) + '\n')
print('Indexed', sum(len(row[exam]) for row in data['rows'] for exam in ('morning', 'afternoon')), 'cells')
