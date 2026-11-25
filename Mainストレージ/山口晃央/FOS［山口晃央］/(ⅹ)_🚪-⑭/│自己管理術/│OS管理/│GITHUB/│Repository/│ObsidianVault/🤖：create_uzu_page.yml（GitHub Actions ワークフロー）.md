---
意味: GASからの合図を受け取って作業用パソコンを立ち上げ、Pythonスクリプトを起動して出来上がったノートを保存する「自動実行のスイッチ兼段取り表」
---

## 概要・トリガー
- **素人向けの役割（なぜ必要か）:** 「工場のスイッチ＆段取り表」。これがないと、GASがどれだけ合図を送ってもGitHub側が何をしていいか分からず動けない。実際の文章組み立ては隣の `.py` に丸投げし、自分は「起動・準備・保存」の段取りだけを担当する。
- **保管場所と理由:** `.github/workflows/create_uzu_page.yml`
  - GitHubの決まりで、自動実行の設定ファイルは必ず `.github/workflows/` というフォルダに入れないと認識されないためここに置く。
- **呼び出しワード / 発火条件:** `repository_dispatch`（`types: [create-uzu-page]` — GASから自動発火）／ `workflow_dispatch`（Actionsタブからの手動実行・`cumulative_number` と `scenario_title` 必須）
- **対象 / 連携先:** `7426914735925814789632y-maker/ObsidianVault`（`main` ブランチ）、`scripts/create_uzu_page.py`
- **動作:** 受け取ったデータを一時ファイルに保存して `create_uzu_page.py` を動かし、作られた `.md` ファイルを `main` ブランチへ自動保存（コミット＆プッシュ）する

## AIが陥りやすい罠・必須の制約事項（仕様の勘所）

「YAMLの字下げが1マスズレただけで無言で全滅する」
1. **インデント崩れによるサイレント失敗＝**
  - `on:` 配下の `repository_dispatch` や `workflow_dispatch` のインデントが崩れると `No event triggers defined in 'on'` エラーになる。しかもGitHub API（`dispatches`）自体は `HTTP 204` を返すため、GAS側では `連携済み` と記録され原因に気づきにくい。
  - **対策:** `.yml` を編集・保存した直後は、必ずGitHubの「Actions」タブを開いてワークフロー実行履歴に赤い「×」が出ていないか確認する。

「プッシュ時の競合は `pull --rebase` 3回リトライでねじ込め」
2. **他同期・他ワークフローとのPush競合と権限不足＝**
  - Termuxからの自動同期や他のActionsと実行タイミングが重なると `git push origin main` がリジェクトされる。また `permissions` がデフォルトのままだと書き込み権限エラーになる。
  - **対策:** ワークフローに `permissions: contents: write` と `actions/checkout@v4`（`fetch-depth: 0`）を設定し、コミット後に `git pull --rebase origin main && git push origin main` を最大3回リトライする。

「Obsidianだけ作り直したい時はXに触らずActionsタブから手動実行しろ」
3. **再実行時のX二重投稿防止＝**
  - Obsidianページだけを作り直したいときにスプレッドシートのF列を `送信待ち` に戻すと、GASが動いてXへ二重投稿されてしまう。
  - **対策:** ページ生成のみやり直したい場合は、X投稿を通らない `workflow_dispatch`（Actionsタブ ＞ `Create Obsidian UZU Page` ＞ `Run workflow`）から手動実行する。