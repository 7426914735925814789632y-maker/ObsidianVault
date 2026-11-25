---
意味: Skills・スプシ・GAS・Templater等の構築・改修内容を、直感的な要約付きドキュメント形式でObsidian保存用に出力するスキル。
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
- **呼び出しワード:** `OS構築保存` / `@OS構築保存` / `Obsidianに記録` / `構築ログをまとめて`（およびSkills・GAS・スプシ・Templater等の新規作成・改修完了時）
- **対象:** Gemini Skills、Googleスプレッドシート、GAS、Obsidian Templaterコード、GitHub Actions等のシステム構築物
- **動作:** 構築した仕組みの役割・トリガー・構造と、実装時に判明したハマりポイント（原因と対策）を統一フォーマットで出力する。

## AIが陥りやすい罠・必須の制約事項（仕様の勘所）

「技術用語だけ並べると後から読むときダルい」
1. **人間向けの直感的な一言サマリーの必須化＝**
  - AI向けの厳密な技術解説だけを箇条書きにすると、後から見返した際に要点を掴むのに時間がかかる。
  - **対策:** 各制約項目の直前に必ず `「〇〇は××しろ」` のような口語的・直感的なカギ括弧フレーズを配置し、0.5秒で勘所が頭に入る構造にする。

「YAMLプロパティが壊れるとBasesやDataviewで死ぬ」
2. **冒頭プロパティ（意味）の1行厳守＝**
  - `---` で囲まれた `意味:` プロパティ内に改行やコロン・クォーテーションの不整合が混入すると、Obsidian側でメタデータとして認識されなくなる。
  - **対策:** タイトル行（`📜：対象名`）の直下に `---` で囲んだ `意味: 〜` を1行で完結させて配置する。

「雑談や経緯はノイズになる」
3. **構築ログの純度維持（役割と罠の2軸限定）＝**
  - 会話中の試行錯誤や余談まで盛り込むとドキュメントが肥大化し、再利用性が落ちる。
  - **対策:** 「何をする仕組みか（概要・トリガー）」と「どこでコケるか・どう防ぐか（仕様の勘所）」の2点のみに絞って記述する。