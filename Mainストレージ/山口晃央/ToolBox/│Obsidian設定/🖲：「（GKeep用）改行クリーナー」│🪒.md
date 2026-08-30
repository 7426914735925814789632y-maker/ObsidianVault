<%*
// 選択されているテキストを取得
let selectedText = tp.file.selection();

if (selectedText) {
    // 連続する改行を1つにまとめる
    let cleanedText = selectedText.replace(/\r\n/g, "\n")
                                  .replace(/\n{2,}/g, "\n")
                                  .trim();
    // 選択範囲を置換
    tR += cleanedText;
} else {
    // 何も選択されていない場合は通常のクリップボード出力をフォールバックとして動作
    let text = await tp.system.clipboard();
    tR += text.replace(/\r\n/g, "\n").replace(/\n{2,}/g, "\n").trim();
}
-%>