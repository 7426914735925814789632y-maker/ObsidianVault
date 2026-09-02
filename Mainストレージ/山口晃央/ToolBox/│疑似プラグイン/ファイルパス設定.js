module.exports = async (tp) => {
    try {
        const tFile = tp.config.target_file;
        if (!tFile || tFile.extension !== "md") return;

        // 現在のファイルの中身（ディスク上の物理テキスト）を読み込む
        let content = await app.vault.read(tFile);
        
        // 物理書き換え用のフラグ（目印）
        const startTag = "%% PHYSICAL_PATH_START %%";
        const endTag = "%% PHYSICAL_PATH_END %%";
        
        // 現在の実際の親フォルダパスを最も安全な方法で取得
        const currentActualPath = tp.file.folder(true); 
        
        // 置換用の正規表現パターン
        const regex = new RegExp(`${startTag}[\\s\\S]*?${endTag}`, "g");
        const newPathStr = `${startTag}\n${currentActualPath}\n${endTag}`;
        
        // ノート内にフラグが存在し、かつ書き込まれているパスが現在地と異なる場合のみ上書き
        if (content.match(regex) && !content.includes(newPathStr)) {
            const updatedContent = content.replace(regex, newPathStr);
            await app.vault.modify(tFile, updatedContent);
        }
    } catch (e) {
        // 万が一エラーが起きた場合は、Obsidianの画面右上にポップアップで通知する
        new Notice("ファイルパス設定スクリプトでエラーが発生しました: " + e.message);
    }
}