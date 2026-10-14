# 応用情報技術者試験 過去問動画一覧

石田宏実の情報処理技術者試験講座の公開再生リストから作成した非公式リンク集。
午前・午後のタブ、試験回の行、問題番号の列でYouTube動画を探せます。

- 個別解説を優先。まとめ動画のみがある問題は、その動画の先頭へリンク。
- 問題番号を特定できない解答速報は、試験回の下に別リンクとして掲載。
- 対応動画のないセルにはリンクを付けません。
- 試験と関係のない動画は除外。その他の再生リストはページ下部に掲載。
- ビルド不要。HTML / CSS / JavaScript / JSONのみで動作します。

## ローカル表示

```sh
python3 -m http.server 8000
```

## データ更新

`scripts/playlists.json` の各URLを以下の形式で取得し、任意のディレクトリへ `<再生リストID>.json` として保存します。

```sh
yt-dlp --flat-playlist --dump-single-json --extractor-args 'youtube:lang=ja' '再生リストURL'
python3 scripts/build-data.py /path/to/playlist-json-directory
```

生成後はタイトル、問題番号、除外された動画 (`scripts/excluded.json`) を確認してください。
YouTubeの動画は埋め込み・複製せず、公開ページへのリンクのみ掲載しています。

## 公開

GitHub Pagesの `main` ブランチ `/` から配信します。
