import os
import re
import shutil
from pathlib import Path

# 処理対象から除外するフォルダ名
IGNORE_DIRS = {'.git', '.github', '.obsidian', '.trash', 'ToolBox'}

def parse_md(content):
    """YAMLフロントマターと本文を安全に分離する"""
    match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n?(.*)$', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2), True
    return "", content, False

def get_prop(yaml_text, key):
    """YAMLテキストから指定キーの値を取得する"""
    match = re.search(rf'^{re.escape(key)}:\s*(.*)$', yaml_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def set_prop(yaml_text, key, value):
    """YAMLテキストの指定キーを更新、なければ末尾に追加する"""
    val_str = f" {value}" if value != "" else ""
    pattern = rf'^{re.escape(key)}:.*$'
    if re.search(pattern, yaml_text, re.MULTILINE):
        return re.sub(pattern, f"{key}:{val_str}", yaml_text, count=1, flags=re.MULTILINE)
    else:
        sep = "\n" if yaml_text and not yaml_text.endswith("\n") else ""
        return f"{yaml_text}{sep}{key}:{val_str}"

def del_prop(yaml_text, key):
    """YAMLテキストから指定キーを削除する"""
    lines = yaml_text.splitlines()
    new_lines = [line for line in lines if not re.match(rf'^{re.escape(key)}:', line)]
    return "\n".join(new_lines)

def build_md(yaml_text, body):
    """YAMLと本文を結合する"""
    yaml_clean = yaml_text.strip("\r\n")
    return f"---\n{yaml_clean}\n---\n{body}"

def is_ignored(path_obj):
    return any(part in IGNORE_DIRS for part in path_obj.parts)

def main():
    root = Path(".")

    # ---------------------------------------------------------
    # ステップ1: ✅️ で始まるフォルダの処理（フォルダノート作成＆✅️削除）
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
                    new_dir = old_dir  # 同名フォルダが既にある場合はリネーム保留

                note_path = new_dir / f"{new_dir.name}.md"
                if not note_path.exists():
                    initial_content = "---\n意味: \nWaypoint: true\n---\n\n%% Waypoint %%\n"
                    note_path.write_text(initial_content, encoding="utf-8")

    # ---------------------------------------------------------
    # ステップ2: 全MDの初期整備（既成フォルダノート救済 ＆ 「意味」補完）
    # ---------------------------------------------------------
    all_mds = [p for p in root.rglob("*.md") if not is_ignored(p)]
    for md_path in all_mds:
        content = md_path.read_text(encoding="utf-8")
        yaml_text, body, has_yaml = parse_md(content)
        orig_yaml, orig_body = yaml_text, body

        # 全ファイルに「意味: 」プロパティがなければ追加
        if get_prop(yaml_text, "意味") is None:
            yaml_text = set_prop(yaml_text, "意味", "")

        # 親フォルダ名とファイル名が完全一致 ＝ 既成フォルダノートに Waypoint: true を付与
        if md_path.parent.name == md_path.stem:
            if get_prop(yaml_text, "Waypoint") is None:
                yaml_text = set_prop(yaml_text, "Waypoint", "true")

        if yaml_text != orig_yaml or not has_yaml:
            md_path.write_text(build_md(yaml_text, body), encoding="utf-8")

    # ---------------------------------------------------------
    # ステップ3: Waypoint: false をトリガーに同名フォルダ作成＆移動
    # ---------------------------------------------------------
    all_mds = [p for p in root.rglob("*.md") if not is_ignored(p)]
    for md_path in all_mds:
        if not md_path.exists():
            continue
        content = md_path.read_text(encoding="utf-8")
        yaml_text, body, _ = parse_md(content)
        wp_val = get_prop(yaml_text, "Waypoint")

        if wp_val and wp_val.lower() == "false":
            target_dir = md_path.parent / md_path.stem
            target_dir.mkdir(exist_ok=True)
            new_md_path = target_dir / md_path.name

            yaml_text = set_prop(yaml_text, "Waypoint", "true")
            if "%% Waypoint %%" not in body:
                sep = "\n\n" if body and not body.endswith("\n\n") else ""
                body = f"{body}{sep}%% Waypoint %%\n"

            new_md_path.write_text(build_md(yaml_text, body), encoding="utf-8")
            if new_md_path != md_path:
                md_path.unlink()

    # ---------------------------------------------------------
    # ステップ4: 「親フォルダ: ○○」をトリガーにフォルダまたは単体移動
    # ---------------------------------------------------------
    all_dirs = [d for d in root.rglob("*") if d.is_dir() and not is_ignored(d)]
    all_mds = [p for p in root.rglob("*.md") if not is_ignored(p)]

    for md_path in all_mds:
        if not md_path.exists():
            continue
        content = md_path.read_text(encoding="utf-8")
        yaml_text, body, _ = parse_md(content)
        parent_target = get_prop(yaml_text, "親フォルダ")

        if parent_target:
            # 「○○」を含むフォルダを検索（完全一致優先、次に階層が浅い順）
            exact_matches = [d for d in all_dirs if d.name == parent_target]
            partial_matches = [d for d in all_dirs if parent_target in d.name]
            candidates = exact_matches if exact_matches else partial_matches

            if candidates:
                dest_dir = sorted(candidates, key=lambda d: (len(d.parts), len(str(d))))[0]
                yaml_text = del_prop(yaml_text, "親フォルダ")
                md_path.write_text(build_md(yaml_text, body), encoding="utf-8")

                wp_val = get_prop(yaml_text, "Waypoint")
                if wp_val and wp_val.lower() == "true" and md_path.parent.name == md_path.stem:
                    # フォルダごと移動
                    src_folder = md_path.parent
                    final_dest = dest_dir / src_folder.name
                    if not final_dest.exists() and src_folder != dest_dir and dest_dir not in src_folder.parents:
                        shutil.move(str(src_folder), str(final_dest))
                else:
                    # 当該mdのみ移動
                    final_dest = dest_dir / md_path.name
                    if not final_dest.exists() and md_path.parent != dest_dir:
                        shutil.move(str(md_path), str(final_dest))

    # ---------------------------------------------------------
    # ステップ5: anki: true かつ Waypoint: true で同階層に card: true を伝播
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
                    continue  # フォルダノート自身は除外
                sib_content = sibling.read_text(encoding="utf-8")
                sib_yaml, sib_body, _ = parse_md(sib_content)
                if get_prop(sib_yaml, "card") != "true":
                    sib_yaml = set_prop(sib_yaml, "card", "true")
                    sibling.write_text(build_md(sib_yaml, sib_body), encoding="utf-8")

if __name__ == "__main__":
    main()
