<%*
// 藤子・F・不二雄 SF短編集 全12巻（111作品）の定義データ
const sfData = [
  {
    vol: "01│🅐「第一巻＿ミノタウロスの皿」",
    works: ["ミノタウロスの皿", "ヒョンヒョロ", "愛のぬけがら", "くせものカレンダー", "ブラック・デビル", "オバケ屋敷の管理者", "値ぶみカメラ", "同窓生", "クローン家族", "ドジ美ちゃん"]
  },
  {
    vol: "02│🅐「第二巻＿絶滅の島」",
    works: ["絶滅の島", "定年退食", "休日のガンマン", "ミリバール", "あいつのタイムマシン", "カイケツ小池さん", "ボノム＝底ぬけさん＝", "ある日……", "劇画・オバQ"]
  },
  {
    vol: "03│🅐「第三巻＿ノスタル爺」",
    works: ["ノスタル爺", "コロリ前夜", "間間間男", "黄昏売込み兵", "権敷無丈", "ミニチュア製造カメラ", "大きな願い", "ポスタリザ", "どことなくなんとなく", "未来ドロボウ"]
  },
  {
    vol: "04│🅐「第四巻＿カンビュセスの籤」",
    works: ["カンビュセスの籤", "一千年後の再会", "自分会議", "我が子スーパーマン", "箱舟はいっぱい", "アン子 大いに怒る", "やすらぎの館", "ポストの中の明日", "ショッキングEG"]
  },
  {
    vol: "05│🅐「第五巻＿ウルトラ・スーパー・デラックスマン」",
    works: ["ウルトラ・スーパー・デラックスマン", "オバケでおっとでる", "無力感", "分岐点", "サンプルAとB", "知られざる一日", "ふたり前", "神さまごっこ", "並平家の一番長い日"]
  },
  {
    vol: "06│🅐「第六巻＿パラレル同窓会」",
    works: ["パラレル同窓会", "クレオパトラだぞ", "やさしい悪魔", "征地球論", "マイシェルター", "四畳半SL旅行", "幸運児", "あのバカは荒野をめざす", "旅人くのいち"]
  },
  {
    vol: "07│🅐「第七巻＿夢カメラ」",
    works: ["夢カメラ", "懐古の客", "三千年後の絵日記", "メフィスト惨歌", "影男", "マイロボット", "有名人販売株式会社", "みえないウーマン", "あしたの思い出"]
  },
  {
    vol: "08│🅐「第八巻＿異人たちからの館」",
    works: ["異人たちからの館", "タイムカメラ", "分身", "千年喜劇", "地球人", "流血鬼", "誰もいなくなった", "未来の思い出"]
  },
  {
    vol: "09│🅐「第九巻＿ポストの中の明日」",
    works: ["ポストの中の明日", "赤毛のアン子", "ひとりぼっちの宇宙戦争", "ウルトラまわる", "ボクのロボット", "ぼくの悪党", "あいつを殺しちゃイヤ！", "さよなら・スパイダー", "ユメミルキカイ", "神さまのロボット"]
  },
  {
    vol: "10│🅐「第十巻＿イヤなイヤなイヤな奴」",
    works: ["イヤなイヤなイヤな奴", "カンビュセスの籤（少年版）", "山寺の和尚さん", "ベソとタケシ", "タイムマシンで作る生活", "俺と俺と俺", "流血鬼（少年版）", "恐竜さん", "あのバカは荒野をめざす（少年版）"]
  },
  {
    vol: "11│🅐「第十一巻＿宇宙船製造法」",
    works: ["宇宙船製造法", "さらば深き海よ", "じじぬき", "アン子 大いに怒る（少年版）", "みえないウーマン（少年版）", "恋人製造法", "創世日記", "四畳半SL旅行（少年版）", "マイロボット（少年版）"]
  },
  {
    vol: "12│🅐「第十二巻＿創世日記」",
    works: ["創世日記（完全版）", "巨大ロボットの秋", "世界名作童話", "宇宙人報告書", "老年期", "四畳半の超人", "大怪獣のあしあと", "ノスタル爺（少年版）"]
  }
];

// ルートパス
const rootPath = "山口晃央/FOS［山口晃央］/(ⅷ)_🕳-⑥/│漫画家/👤：💬〔藤子・F・不二夫〕/🛸│💬SF短編集/🅐│🛸異色SF短編";

// Templaterの誤認を防ぐため % 記号をエスケープ生成
const percent = String.fromCharCode(37);
const wpContent = `${percent}${percent} Waypoint ${percent}${percent}\n`;

for (const book of sfData) {
  // ① 巻フォルダのパスとMOCファイルパス
  const volFolderPath = `${rootPath}/${book.vol}`;
  const volMocFilePath = `${volFolderPath}/${book.vol}.md`;

  if (!this.app.vault.getAbstractFileByPath(volFolderPath)) {
    await this.app.vault.createFolder(volFolderPath);
  }
  if (!this.app.vault.getAbstractFileByPath(volMocFilePath)) {
    await this.app.vault.create(volMocFilePath, wpContent);
  }

  // ② 各作品ごとのフォルダ・ファイル生成
  for (const title of book.works) {
    const workName = `📖：「${title}」`;
    const workFolderPath = `${volFolderPath}/${workName}`;
    const workFilePath = `${workFolderPath}/${workName}.md`;

    if (!this.app.vault.getAbstractFileByPath(workFolderPath)) {
      await this.app.vault.createFolder(workFolderPath);
    }
    if (!this.app.vault.getAbstractFileByPath(workFilePath)) {
      await this.app.vault.create(workFilePath, wpContent);
    }
  }
}

new Notice("藤子・F・不二雄 SF短編集（全12巻・111作品）の生成が完了しました！");
-%>