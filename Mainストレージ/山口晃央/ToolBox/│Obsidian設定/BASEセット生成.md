<%*
// 1. 全ファイルの取得と、親フォルダの検索キーワード入力
const allFiles = app.vault.getAllLoadedFiles();
const folderQuery = await tp.system.prompt("親フォルダの検索キーワードを入力してください（例：人物、プロジェクト、立川、概念）:");
if (!folderQuery) return;

// キーワードを含むフォルダを抽出
const targetFolders = allFiles.filter(f => f.children !== undefined && f.name.includes(folderQuery));

let parentFolderPath = "";
if (targetFolders.length === 0) {
    new Notice(`❌ 「${folderQuery}」を含むフォルダが見つかりませんでした。`);
    return;
} else if (targetFolders.length === 1) {
    parentFolderPath = targetFolders[0].path;
} else {
    // 複数候補がある場合はサジェスターで選択
    const folderPaths = targetFolders.map(f => f.path);
    const selectedPath = await tp.system.suggester(folderPaths, folderPaths);
    if (!selectedPath) return;
    parentFolderPath = selectedPath;
}

// 2. DFBフォルダのフルパスを自動取得
const dfbFolder = allFiles.find(f => f.children !== undefined && f.name === "DFB");
if (!dfbFolder) {
    new Notice("❌ 「DFB」フォルダがVault内に見つかりませんでした。");
    return;
}
const dfbPath = dfbFolder.path;

// 3. 作成する項目（ファイル・フォルダ）名の入力プロンプト
const parentFolderName = parentFolderPath.split("/").pop();
const baseName = await tp.system.prompt(`📁 親フォルダ: ${parentFolderName}\n作成するフォルダ・ファイル名（例：田中太郎、手品演出案、SKK＝「昭和記念公園」）:`);
if (!baseName) return;

// 4. 命名規則とパスの定義
const newFolderPath = `${parentFolderPath}/${baseName}`;
const mdFilePath = `${newFolderPath}/${baseName}.md`;
const baseFilePath = `${newFolderPath}/☷│${baseName}.BASE`;

// file.hasLink() に渡すための「拡張子なしのフルパス」
const mdLinkPath = `${newFolderPath}/${baseName}`;

// 5. フォルダの作成（存在しない場合のみ）
if (!await app.vault.adapter.exists(newFolderPath)) {
    await app.vault.createFolder(newFolderPath);
}

// 6. .md ファイルの中身
const mdContent = `# ${baseName}\n\n`;

// 7. .BASE ファイルの中身（YAML構造を動的生成）
const baseContent = `views:
  - type: table
    name: 表
    filters:
      and:
        - file.hasLink("${mdLinkPath}")
        - file.inFolder("${dfbPath}")
`;

// 8. ファイルの生成
if (!await app.vault.adapter.exists(mdFilePath)) {
    await app.vault.create(mdFilePath, mdContent);
}
if (!await app.vault.adapter.exists(baseFilePath)) {
    await app.vault.create(baseFilePath, baseContent);
}

// 9. 生成したメインの .md ファイルを自動で開く
const targetFile = app.vault.getAbstractFileByPath(mdFilePath);
if (targetFile) {
    await app.workspace.getLeaf().openFile(targetFile);
}
-%>