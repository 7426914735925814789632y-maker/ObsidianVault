---
意味: スプシやGAS等のACLプラグインが聞かないリンクを一括ACL生成する。
---


```cardlink
url: https://share.gemini.google/b4zSx450EDx5
title: "‎Gemini - direct access to Google AI"
description: "Created with Gemini"
host: share.gemini.google
favicon: https://www.gstatic.com/lamda/images/gemini_sparkle_4g_512_lt_f94943af3be039176192d.png
image: https://www.gstatic.com/lamda/images/gemini_aurora_thumbnail_4g_e74822ff0ca4259beb718.png
```


## 概要・トリガー
* **呼び出しワード:** `@ACL` / `@CardLink` / `ACL化` / `カードリンク`
* **対象:** Google Spreadsheet (`docs.google.com/spreadsheets/`) / Google Apps Script (`script.google.com/`)
* **動作:** 対象URLやファイル内容（シート構成・主要カラム・連携処理）を読み取り、固定アイコン付きの `cardlink` ブロックを生成する。

## AIが陥りやすい罠・必須の制約事項（仕様の勘所）


「リンクは全部”〇〇”で囲め」
1. **チャットUIの自動リンク化によるYAML破壊の回避＝**
   * コードブロック内であっても生の `https://` を出力すると、ブラウザ／UI側のコピー機構が `[URL](URL)` というMarkdownリンク記法へ自動変換してしまい、Obsidian側でYAMLパースエラーが起きる。
   * **対策:** `url`・`favicon`・`image` の値は必ずダブルクォーテーションで囲み、コロンをUnicodeエスケープした `"https\u003a//..."` 形式で出力する（ObsidianのYAMLパーサー `js-yaml` は正常にデコードして読み込む）。

「コピペの時”””cardlinkみたいなやつ消えがち」
1. **3連バッククォート吸収によるコピー漏れ防止＝**
   * ` ```cardlink ` を通常の3連バッククォートで囲むと、右上のコピーボタンを押した際に外枠が剥がれ、中身（`url:` 〜 `image:`）しかクリップボードに入らない。
   * **対策:** 外側を必ず**4連バッククォート（````）**で囲み、開始行の ` ```cardlink ` と終了行の ` ``` ` を含めた全行が一発でコピーされる構造にする。

「アイコンは取得できないから自前で」
1. **ログイン必須サービスのOGP取得失敗への固定アイコン対応＝**
   * Google系サービスは認証壁があるため、Auto Card Link標準の自動OGP取得が失敗する。
   * **対策:** 以下の固定メタデータを直接埋め込む。
     * **Spreadsheet:** `favicon: "https\u003a//ssl.gstatic.com/docs/spreadsheets/favicon3.ico"` / `image: "https\u003a//www.gstatic.com/images/branding/product/2x/sheets_2020q4_48dp.png"`
     * **GAS:** `favicon: "https\u003a//ssl.gstatic.com/script/apps_script_1x_24dp.png"` / `image: "https\u003a//www.gstatic.com/images/branding/product/2x/apps_script_48dp.png"`

4. **YAML構文エラーの厳禁事項**
   * **クォート衝突:** `title` と `description` 内にダブルクォーテーション（`"`）を含めない（`'` または「」に置換）。
   * **複数行の禁止:** `description` 内で改行すると描画が崩れるため、必ず1行にまとめる。
   * **URL末尾の正規化:** スプレッドシートのURL末尾に付く `?` や `#gid=...` は削り、`/edit` で統一する。