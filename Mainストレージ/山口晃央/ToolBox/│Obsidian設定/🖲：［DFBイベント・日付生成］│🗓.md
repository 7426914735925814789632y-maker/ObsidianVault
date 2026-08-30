<%*
// 【Waypoint暴走対策】このテンプレートファイル自体への出力を完全にブロック
tp.config.target_file.content = tp.config.active_file ? app.workspace.getActiveFile().unsafeRawContent : "";

// 1. アクティブなファイルからコンテキスト（年・月・ベースパス）を自動抽出
const activeFile = app.workspace.getActiveFile();
let basePath = "";
let year = "2016";
let month = "05";

if (activeFile) {
    const pathRegex = new RegExp("(.+?/〔(\\d{4})年〕/〔(\\d{1,2})月〕)");
    const match = activeFile.path.match(pathRegex);
    if (match) {
        basePath = match[1];
        year = match[2];
        month = match[3].padStart(2, '0');
    }
}

// 2. コンテキストが自動取得できない場合のフォールバック（手動入力＋無限自動計算）
if (!basePath) {
    year = await tp.system.prompt("年を入力してください (例: 2022)", year);
    if (!year) return;
    const monthInput = await tp.system.prompt("月を入力してください (例: 12)", parseInt(month).toString());
    if (!monthInput) return;
    month = monthInput.padStart(2, '0');
    
    const yearNum = parseInt(year);
    const age = yearNum - 2000;
    
    let startAge = 0;
    if (age > 0) {
        startAge = Math.floor((age - 1) / 5) * 5;
    }
    const endAge = startAge + 5;
    
    const startStr = String(startAge).padStart(2, '0');
    const endStr = String(endAge).padStart(2, '0');
    const ageFolder = "│" + startStr + "歳~" + endStr + "歳";
    
    basePath = "山口晃央/Past：山口晃央の過去/DFB/" + ageFolder + "/〔" + year + "年〕/〔" + parseInt(month) + "月〕";
}

new Notice("⏳ タイムライン連続生成を開始: 〔" + year + "年〕〔" + parseInt(month) + "月〕");

// 3. 量産用ループインタフェース（スプリント入力仕様）
while (true) {
    const dayInput = await tp.system.prompt("【" + year + "年" + month + "月】「日」を入力（例: 02 / 空欄またはキャンセルで終了）", "");
    if (!dayInput) {
        new Notice("🏁 タイムラインの生成を終了しました。");
        break;
    }
    const day = dayInput.padStart(2, '0');
    const fullDate = year + "-" + month + "-" + day;
    
    const eventInput = await tp.system.prompt("【" + fullDate + "】イベント名を入力（空欄でこの日をスキップ）", "");
    if (!eventInput) continue;
    
    const dateFolderPath = basePath + "/" + fullDate;
    const dateFilePath = dateFolderPath + "/" + fullDate + ".md";
    const eventFilePath = dateFolderPath + "/🗓：「" + eventInput + "」.md";
    
    try {
        if (!await app.vault.adapter.exists(dateFolderPath)) {
            await app.vault.createFolder(dateFolderPath);
        }
        
        if (!await app.vault.adapter.exists(dateFilePath)) {
            const waypointText = "%%" + " Waypoint " + "%%";
            await app.vault.create(dateFilePath, waypointText);
        }
        
        if (!await app.vault.adapter.exists(eventFilePath)) {
            const content = "# 🗓：「" + eventInput + "」\n\n- 日付: " + fullDate + "\n- タイムライン: [[" + fullDate + "]]\n\n---";
            await app.vault.create(eventFilePath, content);
        }
        
        new Notice("✅ 作成: " + fullDate + " / 🗓：「" + eventInput + "」");
    } catch (error) {
        new Notice("❌ エラー: " + error.message);
        console.error(error);
    }
}
%>