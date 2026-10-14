'use strict';
const tabs = [...document.querySelectorAll('[role="tab"]')];
const table = document.querySelector('#questions');
let data;
function element(tag, text, className) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (className) el.className = className;
  return el;
}
function render(exam, updateUrl = true) {
  const label = exam === 'afternoon' ? '午後' : '午前';
  tabs.forEach(tab => {
    const active = tab.dataset.exam === exam;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
  });
  document.querySelector('#panel').setAttribute('aria-labelledby', `tab-${exam}`);
  const count = exam === 'afternoon' ? 11 : 80;
  const head = element('thead');
  const heading = element('tr');
  const first = element('th', '試験回'); first.scope = 'col'; heading.append(first);
  for (let n = 1; n <= count; n++) { const th = element('th', `問${n}`); th.scope = 'col'; heading.append(th); }
  head.append(heading);
  const body = element('tbody');
  for (const row of data.rows) {
    const tr = element('tr');
    const th = element('th', row.label); th.scope = 'row';
    th.append(element('small', `${row.year}年${row.season}期`));
    if (exam === 'morning') for (const summary of row.summaries) {
      const a = element('a', '解答速報 ↗'); a.href = summary.url; a.title = summary.title; th.append(a);
    }
    tr.append(th);
    for (let n = 1; n <= count; n++) {
      const td = element('td');
      const video = row[exam][n];
      if (video) {
        const a = element('a', undefined, video.grouped ? 'grouped' : '');
        a.href = video.url;
        a.setAttribute('aria-label', `${row.label} ${label} 問${n}：${video.title}${video.grouped ? '（まとめ動画）' : ''}`);
        a.title = `${video.title}${video.grouped ? '（まとめ動画）' : ''}`;
        const icon = element('span', '▶'); icon.setAttribute('aria-hidden', 'true'); a.append(icon); td.append(a);
      } else { const empty = element('span', '—', 'empty'); empty.setAttribute('aria-label', '対応動画なし'); td.append(empty); }
      tr.append(td);
    }
    body.append(tr);
  }
  table.replaceChildren(head, body);
  document.querySelector('#table-description').textContent = `${label}試験 · ${data.rows.length}回分 · 問1〜${count}`;
  document.querySelector('.table-scroll').scrollLeft = 0;
  if (updateUrl) { const url = new URL(location.href); url.searchParams.set('exam', exam); history.replaceState(null, '', url); }
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => { if (data) render(tab.dataset.exam); });
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') next = tabs[1 - index];
    if (event.key === 'Home') next = tabs[0];
    if (event.key === 'End') next = tabs[1];
    if (next && data) { event.preventDefault(); next.focus(); render(next.dataset.exam); }
  });
});
function requestedExam() { return new URLSearchParams(location.search).get('exam') === 'afternoon' ? 'afternoon' : 'morning'; }
fetch('data.json').then(response => { if (!response.ok) throw new Error('データを取得できませんでした'); return response.json(); }).then(json => {
  data = json; render(requestedExam(), false);
  document.querySelector('#updated').textContent = data.updated;
  for (const playlist of data.otherPlaylists) { const a = element('a', `${playlist.title} ↗`); a.href = playlist.url; document.querySelector('#other-links').append(a); }
}).catch(() => { document.querySelector('#table-description').textContent = '一覧を読み込めませんでした。ページを再読み込みしてください。'; });
window.addEventListener('popstate', () => { if (data) render(requestedExam(), false); });
