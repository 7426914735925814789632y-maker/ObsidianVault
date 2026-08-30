<%*
// ベースとなるフォルダのパス（すでに存在している前提です）
const basePath = "山口晃央/FOS［山口晃央］/(ⅶ)_🍃-⑧/🎵│音楽/🎧│🎵アーティスト/🗯️│🎧️ラッパー/👥：🎤〔MOROHA〕";

// 曲名リスト
const songs = [
    "二文銭", "奮い立つCDショップにて", "涙", "行くぞ", "俺のがヤバイ",
    "イケタライクヲコエテイク", "Brother", "恩学", "YouTubeを御覧の皆様へ",
    "あなたから渡詩", "バトル鉛筆", "革命", "ハダ色の日々", "YES MUSIC, YES LIFE.",
    "今、偽善者の先頭で", "げこくのジョー", "勝ち負けじゃないと思える所まで俺は勝ちにこだわるよ",
    "黙闘", "三文銭", "鳩尾から君へ", "RED", "それいけ!フライヤーマン", "宿命",
    "Apollo 11", "スペシャル", "VS", "tomorrow", "GOLD", "Salad bowl",
    "四文銭", "ストロンガー", "上京タワー", "遠郷タワー", "米", "拝啓、MC アフロ様",
    "スタミナ太郎", "夜に数えて", "いくつものいつもの", "うぬぼれ", "五文銭",
    "チャンプロード", "スコールアンドレスポンス", "俺が俺で俺だ", "エリザベス",
    "0G", "花向", "命の不始末", "ネクター", "主題歌", "六文銭", "バラ色の日々",
    "Memorii", "30/20", "COVID-19", "燦美歌", "あいしてる", "やめるなら今だ", "一文銭"
];

// Waypointプラグインの誤爆を防ぐため、文字列を結合して定義します
const waypointText = "%%" + " Waypoint " + "%%";

// 各曲についてフォルダとファイルを作成
for (let song of songs) {
    // 前後の空白や見えない文字を削除
    song = song.trim();
    if (!song) continue;
    
    const folderName = `⏯️：♪「${song}」`;
    const fileName = `⏯️：♪「${song}」.md`;
    const folderPath = `${basePath}/${folderName}`;
    const filePath = `${folderPath}/${fileName}`;
    
    try {
        // フォルダの存在確認・作成
        let folder = app.vault.getAbstractFileByPath(folderPath);
        if (!folder) {
            await app.vault.createFolder(folderPath);
        }
        
        // ファイルの存在確認・作成
        let file = app.vault.getAbstractFileByPath(filePath);
        if (!file) {
            await app.vault.create(filePath, waypointText);
        }
    } catch (error) {
        console.error(`「${song}」の作成中にエラーが発生しました:`, error);
        new Notice(`エラー: 「${song}」の作成に失敗しました。`);
    }
}

new Notice("MOROHAの全曲名フォルダとファイルの作成が完了しました。");
%>