<%*
const view = app.workspace.getActiveViewOfType(tp.obsidian.MarkdownView);
if (!view) return;

const editor = view.editor;
const fullText = editor.getValue();

// 1行書き・複数行書きの両方に対応したコードブロック判定用の正規表現
const codeBlockRegex = /```([^\r\n`]*)\r?\n?([\s\S]*?)```/g;

const allMatches = [...fullText.matchAll(codeBlockRegex)];

// cardlinkを除外した変換対象を取得
const validMatches = allMatches.filter(match => {
  const lang = (match[1] || "").trim().toLowerCase();
  return !lang.startsWith("cardlink");
});

if (validMatches.length === 0) {
  new Notice("対象となるコードブロックが見つかりませんでした。");
  return;
}

// 1件ずつタイトルを設定
const titles = [];
for (let i = 0; i < validMatches.length; i++) {
  const match = validMatches[i];
  // 1行タイプと複数行タイプから純粋なコンテンツ文面を抽出
  const rawContent = match[2] ? match[2] : match[1];
  const content = rawContent.trim();

  // プレビュー用に文頭の1行を取得（50文字制限）
  const firstLine = content.split(/\r?\n/)[0] || "メモ内容";
  const preview = firstLine.length > 50 ? firstLine.substring(0, 50) + "..." : firstLine;

  const promptMessage = `[${i + 1}/${validMatches.length}件目]\nプレビュー: ${preview}\n\nタイトルを入力してください:`;
  const inputTitle = await tp.system.prompt(promptMessage, firstLine);

  if (inputTitle === null) {
    new Notice("処理をキャンセルしました。");
    return;
  }

  titles.push(inputTitle.trim());
}

let validIndex = 0;

// テキストの一括置換
const updatedText = fullText.replace(codeBlockRegex, (match, lang, codeContent) => {
  const trimmedLang = (lang || "").trim().toLowerCase();

  // cardlink はそのまま残す
  if (trimmedLang.startsWith("cardlink")) {
    return match;
  }

  const currentTitle = titles[validIndex] || "";
  validIndex++;

  // コンテンツ部分を取り出し、コールアウトの引用行（> ）にする
  const content = (codeContent ? codeContent : lang).trim();
  const body = content
    .split(/\r?\n/)
    .map(line => `> ${line}`)
    .join('\n');

  // ★変更点：前後に強制改行を入れて次の一文の巻き込みを遮断する
  return `\n> [!info] ${currentTitle}\n${body}\n`;
});

// 挿入した改行によって連続しすぎた空行（3つ以上）をきれいな2空行に整理
const cleanedText = updatedText.replace(/\n{3,}/g, '\n\n');

editor.setValue(cleanedText);
new Notice(`${validIndex} 件のメモをコールアウトに変換しました。`);
-%>