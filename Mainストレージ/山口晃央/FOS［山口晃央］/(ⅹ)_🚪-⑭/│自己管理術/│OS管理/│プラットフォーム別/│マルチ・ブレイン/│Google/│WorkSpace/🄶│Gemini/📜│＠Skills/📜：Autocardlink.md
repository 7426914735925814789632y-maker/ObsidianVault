---
意味: 提示されたURLやWorkspaceファイルのメタデータをもとに、Obsidian・汎用Markdownエディタ・GitHubの全環境で崩れず表示される「1行HTMLリンクカード」を出力するスキル。
---

<table style="width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #555555; background-color: rgba(128, 128, 128, 0.12); border-radius: 14px; overflow: hidden; margin: 6px 0;"><tr><td style="border: none; padding: 10px 12px; vertical-align: middle; line-height: 1.35;"><a href="https://share.gemini.google/b4zSx450EDx5" style="font-weight: 600; font-size: 0.9em; text-decoration: none;">Gemini - direct access to Google AI</a><br><span style="font-size: 0.78em; opacity: 0.8;">Created with Gemini</span><br><span style="font-size: 0.7em; opacity: 0.65;">🌐 share.gemini.google</span></td><td align="center" valign="middle" width="120" style="border: none; padding: 8px 12px 8px 0; text-align: center; vertical-align: middle;"><img src="https://www.gstatic.com/lamda/images/gemini_aurora_thumbnail_4g_e74822ff0ca4259beb718.png" width="105" style="width: 105px; height: auto; border-radius: 8px; display: block; margin: 0 auto;"></td></tr></table>


## 概要・トリガー
- **呼び出しワード / 発火条件:** `@ACL`、`@CardLink`、`ACL化`、`CardLink化`、`Auto Card Link`、`カードリンクを作成`
- **対象 / 連携先:** Webページ全般、Google スプレッドシート、Google Apps Script（GAS）
- **動作:** URLや対象ファイルからタイトル・80文字程度の要約・ドメイン名・OGP画像（未取得時はGoogleファビコンAPI）を抽出し、Markdown本文にそのまま貼れる改行なし1行の `<table>` タグで出力する。

## AIが陥りやすい罠・必須の制約事項（仕様の勘所）

「HTMLタグの中に1つでも改行を入れるな、必ず1行で出せ」
1. **Markdownパーサーによる自動 `<br>` 挿入とレイアウト崩壊＝**
  - 見やすさのためにHTMLタグ内に改行を入れると、Obsidian等のパーサーが改行を `<br>` に変換し、カードが縦長に間延びしたり字下げが発生したりする。
  - **対策:** `<table ...>` から `</table>` までを完全に改行なしの1行で出力し、かつ上下のMarkdown本文と干渉しないよう前後に1行ずつ空行を入れる。

「外側を `<div>` で囲むな、`<table>` 単体で組め」
2. **余計なマージン・二重枠線の発生＝**
  - `<div>` の内側に `<table>` を配置すると、エディタやテーマによっては外枠と内枠が二重になったり不要な余白が生まれたりする。
  - **対策:** ラッパー用の `<div>` は使わず、`<table>` タグ単体でカード全体の枠線・背景・角丸を構成する。

「GitHubは `style="..."` を全部消すから、HTML属性の `width` を必ず残せ」
3. **GitHub上でのインラインCSS無効化による崩れ＝**
  - GitHubのMarkdownレンダラーはセキュリティ上 `style="..."` 属性をすべて削除するため、CSSだけで幅や配置を指定すると画像が巨大化したり横並びが崩れたりする。
  - **対策:** `<table>` 構造をベースにし、右セルの `width="120"`・`align="center"`・`valign="middle"`、および画像タグの `width="105"` といった素のHTML属性を必ず残す。

「Obsidian専用のCSS変数（`var(--...)`）は使わず、どのテーマでも動く固定値を使え」
4. **環境依存の色指定による視認性低下＝**
  - `--background-modifier-border` などのObsidian固有変数は他エディタやGitHubで無効になる。
  - **対策:** 枠線は `#555555`、背景色は半透明の `rgba(128, 128, 128, 0.12)`、文字の濃淡は `opacity` を指定し、ライト・ダーク両テーマおよび全環境で自然に馴染ませる。

「OGP画像が取れないときはGoogleファビコンAPIに逃がし、特殊文字はエスケープしろ」
5. **画像リンク切れとHTML構文破損＝**
  - サムネイルが存在しないページや、タイトル・概要に `<` `>` `&` を含むページをそのまま埋め込むと表示が壊れる。
  - **対策:** `og:image` や公式ロゴが取れない場合は `https://www.google.com/s2/favicons?domain={ドメイン名}&sz=128` を使い、テキスト内の特殊文字は適切にHTMLエスケープする。
