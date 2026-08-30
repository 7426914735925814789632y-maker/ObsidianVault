<%*
// ==============================================================================
// 1. 設定領域（2026年8月1日 〜 2030年12月31日 ※今月7月は除外）
// ==============================================================================
const startDate = new Date(2026, 7, 1);   // 2026年8月1日 (JSの月カウントでは 7 = 8月)
const endDate = new Date(2030, 11, 31);  // 2030年12月31日
const baseRoot = "山口晃央/Past：山口晃央の過去/DFB/│25歳~30歳";

// 特殊記号（%）のパースエラーを防ぐためのエスケープ済みWaypoint
const waypointStr = "\x25\x25 Waypoint \x25\x25";

// ==============================================================================
// 2. 既設スキップ ＆ 安全注入ロジック
// ==============================================================================
let current = new Date(startDate);
let updatedCount = 0;
let skippedCount = 0;
let createdCount = 0;

new Notice("2026年8月〜2030年12月までのフッター本番一斉注入を開始します...");

while (current <= endDate) {
    const year = current.getFullYear();
    const month = current.getMonth() + 1;
    
    const yyyy = year;
    const mm = String(month).padStart(2, '0');
    const dd = String(current.getDate()).padStart(2, '0');
    const dateStr = yyyy + "-" + mm + "-" + dd;

    const yearFolder = "〔" + year + "年〕";
    const monthFolder = "〔" + month + "月〕";
    
    // 対象パスの組み立て
    const dirPath = baseRoot + "/" + yearFolder + "/" + monthFolder + "/" + dateStr;
    const mdPath = dirPath + "/" + dateStr + ".md";

    // 注入する指定フッターの構造
    const footerContent = "### ────────■\n" +
"#### 【ファイルLog】\n" +
"![](☷│" + dateStr + ".base)\n" +
"#### 【DailyData】\n" +
waypointStr + "\n\n" +
"#### 【出力用追加テキスト】\n" +
"##### ○本日出力ファイル";

    // 該当日のフォルダが存在する場合のみ処理（ノイズ作成防止の安全策）
    if (await app.vault.adapter.exists(dirPath)) {
        
        if (await app.vault.adapter.exists(mdPath)) {
            // すでにデイリーノートが存在する場合、一度中身を読み込む
            let existingContent = await app.vault.adapter.read(mdPath);

            // ★ガード条件：すでにフッターが入力されている場合は「完全に無視（スキップ）」
            if (existingContent.includes("### ────────■")) {
                skippedCount++;
            } else {
                // フッターがない場合のみ、既存ログを保護しながら末尾に結合
                let newContent = existingContent.trim() + "\n\n" + footerContent;
                await app.vault.adapter.write(mdPath, newContent);
                updatedCount++;
            }
        } else {
            // 万が一フォルダだけあってファイルがない場合は、タイトル付きで新規作成
            const newFileContent = "# " + dateStr + "\n\n" + footerContent;
            await app.vault.adapter.write(mdPath, newFileContent);
            createdCount++;
        }
    }

    // 次の日へ
    current.setDate(current.getDate() + 1);
}

new Notice("本番処理がすべて完了しました！\n" +
"・フッター未設定ノートへの注入: " + updatedCount + "件\n" +
"・すでにフッターあり（スキップ無視）: " + skippedCount + "件\n" +
"・空フォルダへの新規生成: " + createdCount + "件");
-%>