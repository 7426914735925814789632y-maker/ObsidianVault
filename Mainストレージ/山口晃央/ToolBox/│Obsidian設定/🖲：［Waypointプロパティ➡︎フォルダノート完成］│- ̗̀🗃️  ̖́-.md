<%*
const IGNORE_DIRS = [".obsidian", ".trash", "ToolBox", ".github"];
const WP_TAG = "\u0025\u0025 Waypoint \u0025\u0025";
const WP_BEGIN = "\u0025\u0025 Begin Waypoint \u0025\u0025";

function isIgnored(path) {
  return path.split("/").some(part => IGNORE_DIRS.indexOf(part) !== -1);
}

let folderizedCount = 0;
const allFiles = app.vault.getMarkdownFiles();

for (let i = 0; i < allFiles.length; i++) {
  const file = allFiles[i];
  if (isIgnored(file.path)) continue;

  const cache = app.metadataCache.getFileCache(file);
  const fm = cache && cache.frontmatter ? cache.frontmatter : null;
  if (!fm) continue;

  // プロパティが存在し、かつ値が false または null（空欄 [-]）の場合のみ実行
  if (fm["Waypoint"] === false || fm["Waypoint"] === "false" || fm["Waypoint"] === null) {
    // 1. 親フォルダが未作成の場合のみ作成・移動（重複フォルダ防止）
    if (file.parent.name !== file.basename) {
      const newFolderPath = file.parent.path === "/" ? file.basename : file.parent.path + "/" + file.basename;
      if (!app.vault.getAbstractFileByPath(newFolderPath)) {
        await app.vault.createFolder(newFolderPath);
      }
      const newFilePath = newFolderPath + "/" + file.name;
      if (!app.vault.getAbstractFileByPath(newFilePath)) {
        await app.fileManager.renameFile(file, newFilePath);
        folderizedCount++;
      }
    }

    // 2. フォルダ移動完了後にプロパティを true に更新
    await app.fileManager.processFrontMatter(file, function(fmUpdate) {
      fmUpdate["Waypoint"] = true;
    });

    const content = await app.vault.read(file);
    if (content.indexOf(WP_TAG) === -1 && content.indexOf(WP_BEGIN) === -1) {
      const sep = content.endsWith("\n") ? "\n" : "\n\n";
      await app.vault.modify(file, content + sep + WP_TAG + "\n");
    }
  }
}

new Notice("フォルダノート完成：" + folderizedCount + "件処理しました");
%>
