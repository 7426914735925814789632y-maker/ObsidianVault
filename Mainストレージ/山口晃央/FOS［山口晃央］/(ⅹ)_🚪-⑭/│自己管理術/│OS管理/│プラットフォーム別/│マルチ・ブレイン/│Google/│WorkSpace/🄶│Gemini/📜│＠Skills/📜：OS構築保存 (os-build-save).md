---
意味: Skills・GAS・スプレッドシート等の構築・改修内容を、ObsidianのBases対応プロパティ＋人間向け一言要約＋AI向け技術解説の統一フォーマットで出力するスキル。
---
<table style="width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #555555; background-color: rgba(128, 128, 128, 0.12); border-radius: 14px; overflow: hidden; margin: 6px 0;"><tr><td style="border: none; padding: 10px 12px; vertical-align: middle; line-height: 1.35;"><a href="https://share.gemini.google/b4zSx450EDx5" style="font-weight: 600; font-size: 0.9em; text-decoration: none;">Gemini - direct access to Google AI</a><br><span style="font-size: 0.78em; opacity: 0.8;">Created with Gemini</span><br><span style="font-size: 0.7em; opacity: 0.65;">🌐 share.gemini.google</span></td><td align="center" valign="middle" width="120" style="border: none; padding: 8px 12px 8px 0; text-align: center; vertical-align: middle;"><img src="https://www.gstatic.com/lamda/images/gemini_aurora_thumbnail_4g_e74822ff0ca4259beb718.png" width="105" style="width: 105px; height: auto; border-radius: 8px; display: block; margin: 0 auto;"></td></tr></table>


## 概要・トリガー
- **呼び出しワード / 発火条件:** `@OSセーブ`、`＠OSセーブ`、`OSセーブ`、`OS構築保存`、`@OS構築保存`、`＠OS構築保存`
- **対象 / 連携先:** Obsidian（構築ログ・システムドキュメント保管用ノート）
- **動作:** 直前の会話や指定されたシステム構築物から役割・トリガー・構造・ハマりポイントを抽出し、そのままObsidianへ貼り付けられるMarkdownドキュメントを生成する。

## AIが陥りやすい罠・必須の制約事項（仕様の勘所）

「小難しい技術用語の前に、まず人間が0.5秒でわかる一言サマリーを置け」
1. **技術解説の羅列による可読性低下＝**
  - AIが原因と対策だけを技術的に並べると、後から人間が見返したときに要点が頭に入ってこない。
  - **対策:** 「仕様の勘所」の各項目の直前に、必ず `「〇〇は△△しろ」` のような口語的・直感的なカギ括弧付きフレーズを添え、その下に技術的な原因と対策を箇条書きにする。

「冒頭の `意味:` プロパティは絶対に1行のまま崩すな」
2. **YAMLフロントマターの構文・参照エラー＝**
  - 冒頭の `---` で囲まれた `意味:` プロパティが複数行になったり欠落したりすると、ObsidianのBasesやDataviewで一覧表示・検索ができなくなる。
  - **対策:** `意味:` の値は改行を入れず1行の簡潔な説明に収め、前後の `---` 区切りを厳守する。

「雑談や試行錯誤の経緯は捨てて、『何をするか』と『どこでコケるか』だけ書け」
3. **ログの冗長化による保守性悪化＝**
  - 会話のやり取りをそのまままとめると長文化し、実践で参照したい仕様や制約が埋もれてしまう。
  - **対策:** 「概要・トリガー」と「仕様の勘所（問題・対策）」の2軸に絞って構造化し、関連URLを添える場合は最新の `autocardlink`（1行HTMLリンクカード）仕様を併用する。
