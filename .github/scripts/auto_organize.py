import os
import re
import shutil
from pathlib import Path

IGNORE_DIRS = {'.git', '.github', '.obsidian', '.trash', 'ToolBox'}

def parse_md(content):
    match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n?(.*)$', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2), True
    return "", content, False

def get_prop(yaml_text, key):
    match = re.search(rf'^{re.escape(key)}:\s*(.*)$', yaml_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def set_prop(yaml_text, key, value):
    val_str = f" {value}" if value != "" else ""
    pattern = rf'^{re.escape(key)}:.*$'
    if re.search(pattern, yaml_text, re.MULTILINE):
        return re.sub(pattern, f"{key}:{val_str}", yaml_text, count=1, flags=re.MULTILINE)
    else:
        sep = "\n" if yaml_text and not yaml_text.endswith("\n") else ""
        return f"{yaml_text}{sep}{key}:{val_str}"

def build_md(yaml_text, body):
    yaml_clean = yaml_text.strip("\r\n")
    return f"---\n{yaml_clean}\n---\n{body}"

def is_ignored(path_obj):
    return any(part in IGNORE_DIRS for part in path_obj.parts)

def has_waypoint_tag(body):
    return ("%% Waypoint %%" in body) or ("%% Begin Waypoint %%" in body)

def find_dest_folder(target_name, all_dirs):
    # 1. フォルダ名の完全一致を最優先
    exact = [d for d in all_dirs if d.name == target_name]
    if exact:
        return sorted(exact, key=lambda d: (len(d.parts), len(str(d))))[0]

    # 2. キーワード（全角・半角スペース区切り）をすべて含むフォルダ名
    keywords = [k for k in re.split(r'[\s　]+', target_name) if k]
    if not keywords:
        return None

    name_matches = [d for d in all_dirs if all(kw in d.name for kw in keywords)]
    if name_matches:
        return sorted(name_matches, key=lambda d: (len(d.parts), len(str(d))))[0]

    # 3. パス全体にキーワードをすべて含むフォルダ
    path_matches = [d for d in all_dirs if all(kw in d.as_posix() for kw in keywords)]
    if path_matches:
        return sorted(path_matches, key=lambda d: (len(d.parts), len(str(d))))[0]

    return None

def main():
    root = Path(".")

    # ---------------------------------------------------------
    # 1. ✅️ で始まるフォルダの処理（フォルダノート作成＆✅️削除）
    # ---------------------------------------------------------
    for dirpath, dirnames, _ in os.walk(root, topdown=False):
        p_dir = Path(dirpath)
        if is_ignored(p_dir):
            continue
        for dname in dirnames:
            if dname.startswith("✅️") or dname.startswith("✅"):
                clean_name = re.sub(r'^✅️?\s*', '', dname)
                if not clean_name:
                    continue
                old_dir = p_dir / dname
                new_dir = p_dir / clean_name
                if not new_dir.exists():
                    old_dir.rename(new_dir)
                else:
                    new_dir = old_dir

                note_path = new_dir / f"{new_dir.name}.md"
                if not note_path.exists():
                    initial_content = "---\n意味: \nWaypoint: true\n---\n\n%% Waypoint %%\n"
                    note_path.write_text(initial_content, encoding="utf-8")

    # ---------------------------------------------------------
    # 2. 全MDの初期整備（既成フォルダノート救済 ＆ 「意味」補完）
    # ---------------------------------------------------------
    all_mds = [p for p in root.rglob("*.md") if not is_ignored(p)]
    for md_path in all_mds:
        content = md_path.read_text(encoding="utf-8")
        yaml_text, body, has_yaml = parse_md(content)
        orig_yaml = yaml_text

        if get_prop(yaml_text, "意味") is None:
            yaml_text = set_prop(yaml_text, "意味", "")

        if md_path.parent.name == md_path.stem:
            if get_prop(yaml_text, "Waypoint") is None:
                yaml_text = set_prop(yaml_text, "Waypoint", "true")

        if yaml_text != orig_yaml or not has_yaml:
            md_path.write_text(build_md(yaml_text, body), encoding="utf-8")

    # ---------------------------------------------------------
    # 3. Waypoint: false をトリガーに同名フォルダ作成＆移動
    # ---------------------------------------------------------
    all_mds = [p for p in root.rglob("*.md") if not is_ignored(p)]
    for md_path in all_mds:
        if not md_path.exists():
            continue
        content = md_path.read_text(encoding="utf-8")
        yaml_text, body, _ = parse_md(content)
        wp_val = get_prop(yaml_text, "Waypoint")

        if wp_val and wp_val.lower() == "false":
            if md_path.parent.name != md_path.stem:
                target_dir = md_path.parent / md_path.stem
                target_dir.mkdir(exist_ok=True)
                dest_md_path = target_dir / md_path.name
            else:
                dest_md_path = md_path

            yaml_text = set_prop(yaml_text, "Waypoint", "true")
            if not has_waypoint_tag(body):
                sep = "\n\n" if body and not body.endswith("\n\n") else ""
                body = f"{body}{sep}%% Waypoint %%\n"

            dest_md_path.write_text(build_md(yaml_text, body), encoding="utf-8")
            if dest_md_path != md_path:
                md_path.unlink()

    # ---------------------------------------------------------
    # 4. 「所在フォルダ」プロパティによる移動・新規フォルダ作成
    # ---------------------------------------------------------
    all_dirs = [d for d in root.rglob("*") if d.is_dir() and not is_ignored(d)]
    all_mds = [p for p in root.rglob("*.md") if not is_ignored(p)]

    for md_path in all_mds:
        if not md_path.exists():
            continue
        content = md_path.read_text(encoding="utf-8")
        yaml_text, body, _ = parse_md(content)
        raw_target = get_prop(yaml_text, "所在フォルダ")

        if not raw_target:
            continue

        target_name = raw_target.strip().strip('"').strip("'")
        if not target_name or target_name in ("【完了済み】", "【不定】"):
            continue

        wp_val = get_prop(yaml_text, "Waypoint")
        is_wp_true = bool(wp_val and wp_val.lower() == "true")
        dest_dir = find_dest_folder(target_name, all_dirs)

        if dest_dir:
            # 移動先が見つかった場合
            yaml_text = set_prop(yaml_text, "所在フォルダ", "【完了済み】")
            yaml_text = set_prop(yaml_text, "所在チェック", "false")
            md_path.write_text(build_md(yaml_text, body), encoding="utf-8")

            if is_wp_true and md_path.parent.name == md_path.stem:
                src_folder = md_path.parent
                final_dest = dest_dir / src_folder.name
                if not final_dest.exists() and src_folder != dest_dir and dest_dir not in src_folder.parents:
                    shutil.move(str(src_folder), str(final_dest))
            else:
                final_dest = dest_dir / md_path.name
                if not final_dest.exists() and md_path.parent != dest_dir:
                    shutil.move(str(md_path), str(final_dest))
        else:
            # 移動先が見つからない場合：1つ上の階層に新規フォルダ＆同名フォルダノート作成
            if is_wp_true and md_path.parent.name == md_path.stem:
                base_dir = md_path.parent.parent
            else:
                base_dir = md_path.parent

            new_folder = base_dir / target_name
            new_folder.mkdir(exist_ok=True)
            new_note = new_folder / f"{target_name}.md"
            if not new_note.exists():
                new_note.write_text("---\n意味: \nWaypoint: true\n---\n\n%% Waypoint %%\n", encoding="utf-8")

            yaml_text = set_prop(yaml_text, "所在フォルダ", "【完了済み】")
            yaml_text = set_prop(yaml_text, "所在チェック", "false")
            md_path.write_text(build_md(yaml_text, body), encoding="utf-8")

    # ---------------------------------------------------------
    # 5. anki: true かつ Waypoint: true で同階層に card: true を伝播
    # ---------------------------------------------------------
    all_mds = [p for p in root.rglob("*.md") if not is_ignored(p)]
    for md_path in all_mds:
        content = md_path.read_text(encoding="utf-8")
        yaml_text, _, _ = parse_md(content)
        anki_val = get_prop(yaml_text, "anki")
        wp_val = get_prop(yaml_text, "Waypoint")

        if anki_val and anki_val.lower() == "true" and wp_val and wp_val.lower() == "true":
            parent_folder = md_path.parent
            for sibling in parent_folder.glob("*.md"):
                if sibling == md_path:
                    continue
                sib_content = sibling.read_text(encoding="utf-8")
                sib_yaml, sib_body, _ = parse_md(sib_content)
                if get_prop(sib_yaml, "card") != "true":
                    sib_yaml = set_prop(sib_yaml, "card", "true")
                    sibling.write_text(build_md(sib_yaml, sib_body), encoding="utf-8")

if __name__ == "__main__":
    main()
