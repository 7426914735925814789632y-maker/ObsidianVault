<%*
// ==============================================================================
// 1. 設定領域（期間とルートパス）
// ==============================================================================
const startDate = new Date(2026, 0, 1);
const endDate = new Date(2026, 11, 31);
const baseRoot = "山口晃央/Past：山口晃央の過去/DFB";

// ==============================================================================
// 2. 変換・生成ロジック
// ==============================================================================
let current = new Date(startDate);
let count = 0;

new Notice("BASEファイルのフィルター条件を最適化中...");

while (current <= endDate) {
    const year = current.getFullYear();
    const month = current.getMonth() + 1;
    
    const yyyy = year;
    const mm = String(month).padStart(2, '0');
    const dd = String(current.getDate()).padStart(2, '0');
    const dateStr = `${yyyy}-${mm}-${dd}`; // 例: "2026-05-28"

    const yearFolder = `〔${year}年〕`;
    const monthFolder = `〔${month}月〕`;
    
    const dirPath = `${baseRoot}/${yearFolder}/${monthFolder}/${dateStr}`;
    const newBasePath = `${dirPath}/☷│${dateStr}.base`;

    // フィルター条件の右辺に、直接 dateStr ("2026-05-28") を埋め込む
    const baseContent = `views:
  - type: table
    name: 表
    filters:
      or:
        - |
          file.ctime.date() == "${dateStr}"
        - and:
            - '!file.inFolder("${baseRoot}")'
            - file.hasLink("${baseRoot}/${yearFolder}/${monthFolder}/${dateStr}/${dateStr}")`;

    // ファイルを上書き更新
    if (await app.vault.adapter.exists(newBasePath)) {
        await app.vault.adapter.write(newBasePath, baseContent);
        count++;
    }

    current.setDate(current.getDate() + 1);
}

new Notice(`最適化が完了しました！\n${count} 個の .base ファイルを修正しました。`);
-%>
