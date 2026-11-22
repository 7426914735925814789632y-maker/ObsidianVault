#!/usr/bin/env python3
"""Generate an Obsidian UZU play log Markdown file from JSON payload."""

from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

JST = timezone(timedelta(hours=9))
DEFAULT_TARGET_DIR = os.environ.get(
    "UZU_TARGET_DIR",
    "Mainストレージ/山口晃央/FOS［山口晃央］/(ⅷⅰ)_👑-⑦/│マーダーミステリー/│UZU履歴",
)
FILE_PATTERN = re.compile(r"^(\d{4})：(.+)\.md$")
X_STATUS_PATTERN = re.compile(r"https?://(?:x|twitter)\.com/([^/]+)/status/(\d+)")
INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]')
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
BOT_USER_AGENT = "Twitterbot/1.0"


class OGPParser(HTMLParser):
    """HTML parser extracting Open Graph, Twitter Card, <title>, and favicon."""

    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.icons: list[str] = []
        self.in_title = False
        self.title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_lower = tag.lower()
        if tag_lower == "title":
            self.in_title = True
            return

        attr_map = {k.lower(): (v or "") for k, v in attrs}
        if tag_lower == "meta":
            key = attr_map.get("property") or attr_map.get("name") or ""
            content = attr_map.get("content") or ""
            if key and content and key.lower() not in self.meta:
                self.meta[key.lower()] = html.unescape(content.strip())
        elif tag_lower == "link":
            rel = attr_map.get("rel", "").lower()
            href = attr_map.get("href", "").strip()
            if href and ("icon" in rel):
                self.icons.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def page_title(self) -> str:
        return html.unescape("".join(self.title_parts).strip())


def http_get_text(
    url: str, timeout: int = 12, user_agent: str = USER_AGENT
) -> tuple[str, str]:
    """Fetch URL body and final URL; return ('', url) on failure."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            final_url = resp.geturl() or url
            raw_bytes = resp.read(768 * 1024)
            charset = resp.headers.get_content_charset() or "utf-8"
            return raw_bytes.decode(charset, errors="replace"), final_url
    except (urllib.error.URLError, TimeoutError, ValueError):
        return "", url


def fetch_ogp(url: str, timeout: int = 12) -> dict[str, str]:
    """Fetch OGP/Twitter metadata and favicon for Auto Card Link."""
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc
    result = {
        "url": url,
        "title": "",
        "description": "",
        "host": host,
        "image": "",
        "favicon": "",
    }
    if not url:
        return result

    ua = BOT_USER_AGENT if "uzu-app.com" in host else USER_AGENT
    body, final_url = http_get_text(url, timeout=timeout, user_agent=ua)
    if not body:
        return result

    parser = OGPParser()
    parser.feed(body)

    result["title"] = (
        parser.meta.get("og:title")
        or parser.meta.get("twitter:title")
        or parser.page_title
    )
    result["description"] = (
        parser.meta.get("og:description")
        or parser.meta.get("twitter:description")
        or parser.meta.get("description")
        or ""
    )
    raw_image = (
        parser.meta.get("og:image")
        or parser.meta.get("twitter:image")
        or ""
    )
    if raw_image:
        result["image"] = urllib.parse.urljoin(final_url, raw_image)

    if parser.icons:
        result["favicon"] = urllib.parse.urljoin(final_url, parser.icons[0])

    return result


def fetch_x_metadata(x_post_url: str) -> dict[str, str]:
    """Fetch X post metadata via fxtwitter / oembed as fallback."""
    info = {
        "title": "",
        "description": "",
        "image": "",
        "favicon": "https://abs.twimg.com/favicons/twitter.3.ico",
    }
    match = X_STATUS_PATTERN.search(x_post_url)
    if match:
        user, status_id = match.group(1), match.group(2)
        fx_body, _ = http_get_text(
            f"https://api.fxtwitter.com/{user}/status/{status_id}", timeout=10
        )
        if fx_body:
            try:
                data = json.loads(fx_body)
                tweet = data.get("tweet") or {}
                author = tweet.get("author") or {}
                name = author.get("name") or ""
                screen = author.get("screen_name") or user
                if name:
                    info["title"] = f"{name} (@{screen}) on X"
                if tweet.get("text"):
                    info["description"] = tweet["text"]
                media = tweet.get("media") or {}
                photos = media.get("photos") or []
                if photos and isinstance(photos[0], dict):
                    info["image"] = photos[0].get("url") or ""
                if info["description"]:
                    return info
            except json.JSONDecodeError:
                pass

    oembed_url = (
        "https://publish.twitter.com/oembed?omit_script=true&url="
        + urllib.parse.quote(x_post_url, safe="")
    )
    oe_body, _ = http_get_text(oembed_url, timeout=10)
    if oe_body:
        try:
            oe = json.loads(oe_body)
            author_name = oe.get("author_name") or ""
            author_url = oe.get("author_url") or ""
            handle = author_url.rstrip("/").split("/")[-1] if author_url else ""
            if author_name and handle and not info["title"]:
                info["title"] = f"{author_name} (@{handle}) on X"
            raw_html = oe.get("html") or ""
            p_match = re.search(r"<p[^>]*>(.*?)</p>", raw_html, re.S)
            if p_match and not info["description"]:
                plain = re.sub(r"<[^>]+>", " ", p_match.group(1))
                info["description"] = html.unescape(re.sub(r"\s+", " ", plain).strip())
        except json.JSONDecodeError:
            pass

    return info


def escape_cardlink_str(value: str) -> str:
    """Normalize multiline strings and escape double quotes for cardlink."""
    single_line = re.sub(r"\s+", " ", value).strip()
    return single_line.replace('"', '\\"')


def format_cardlink(data: dict[str, str]) -> str:
    """Render an Obsidian Auto Card Link code block."""
    lines = ["```cardlink", f"url: {data['url']}"]
    if data.get("title"):
        lines.append(f'title: "{escape_cardlink_str(data["title"])}"')
    if data.get("description"):
        lines.append(f'description: "{escape_cardlink_str(data["description"])}"')
    if data.get("host"):
        lines.append(f"host: {data['host']}")
    if data.get("favicon"):
        lines.append(f"favicon: {data['favicon']}")
    if data.get("image"):
        lines.append(f"image: {data['image']}")
    lines.append("```")
    return "\n".join(lines)


def find_entries(target_dir: Path) -> list[tuple[int, str]]:
    """Return sorted list of (number, stem) for existing UZU notes."""
    if not target_dir.exists():
        return []

    entries: list[tuple[int, str]] = []
    for path in target_dir.iterdir():
        if not path.is_file():
            continue
        match = FILE_PATTERN.match(path.name)
        if match:
            entries.append((int(match.group(1)), path.stem))
    entries.sort(key=lambda item: item[0])
    return entries


def resolve_number_and_prev(
    entries: list[tuple[int, str]],
    explicit_num: str,
    explicit_prev: str,
) -> tuple[str, str]:
    """Use sheet-provided cumulative_number and find previous note stem."""
    if explicit_num.isdigit():
        num_int = int(explicit_num)
    else:
        max_num = entries[-1][0] if entries else 0
        num_int = max_num + 1

    prev_stem = explicit_prev
    if not prev_stem and entries:
        prior = [stem for n, stem in entries if n < num_int]
        if prior:
            prev_stem = prior[-1]

    return f"{num_int:04d}", prev_stem


def sanitize_title(title: str) -> str:
    """Remove characters disallowed in filenames across OSes."""
    cleaned = INVALID_FILENAME_CHARS.sub(" ", title).strip()
    return re.sub(r"\s+", " ", cleaned)


def format_memo_lines(memo: str) -> str:
    """Normalize memo lines; keep existing bullets or prefix with ・."""
    raw_lines = [line.rstrip() for line in memo.strip().splitlines()]
    formatted: list[str] = []
    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if (
            line.startswith("・")
            or line.startswith("- ")
            or line.startswith("* ")
            or line.startswith("\t")
            or line.startswith("  ")
            or stripped.startswith("→")
        ):
            formatted.append(line)
        else:
            formatted.append(f"・{stripped}")
    return "\n".join(formatted)


def build_markdown(payload: dict[str, object], target_dir: Path) -> tuple[Path, str]:
    """Build target Path and full Markdown content from payload."""
    scenario_title = sanitize_title(str(payload.get("scenario_title") or "").strip())
    if not scenario_title:
        raise ValueError("scenario_title is required")

    play_date = str(payload.get("play_date") or "").strip()
    if not play_date:
        play_date = datetime.now(JST).strftime("%Y-%m-%d")

    synopsis = str(payload.get("synopsis") or "").strip()
    memo = str(payload.get("memo") or "").strip()
    uzu_url = str(payload.get("uzu_url") or "").strip()
    x_post_url = str(payload.get("x_post_url") or "").strip()
    x_post_text = str(payload.get("x_post_text") or "").strip()
    x_image_url = str(payload.get("x_image_url") or "").strip()
    x_author_title = str(
        payload.get("x_author_title") or "ひあ (@hia_fosch) on X"
    ).strip()
    gemini_url = str(payload.get("gemini_url") or "").strip()

    entries = find_entries(target_dir)
    next_num, prev_title = resolve_number_and_prev(
        entries,
        str(payload.get("cumulative_number") or "").strip(),
        str(payload.get("prev_title") or "").strip(),
    )

    filename = f"{next_num}：「{scenario_title}」.md"
    output_path = target_dir / filename

    synopsis_line = re.sub(r"\s+", " ", synopsis)
    sections: list[str] = [
        "---",
        f"意味: {synopsis_line}",
        f"開始日: {play_date}",
        "---",
        f"日付：[[{play_date}]]",
    ]
    if prev_title:
        sections.append(f"前回：[[{prev_title}]]")

    sections.append("#### 【メモ】")
    if memo:
        sections.append(format_memo_lines(memo))

    sections.extend(["", "", "---", ""])

    uzu_ogp: dict[str, str] = {}
    if uzu_url:
        uzu_ogp = fetch_ogp(uzu_url)
        if not uzu_ogp.get("title") or uzu_ogp.get("title") in ("ウズ", "UZU"):
            uzu_ogp["title"] = f"『{scenario_title}』"
        if not uzu_ogp.get("image") and x_image_url:
            uzu_ogp["image"] = x_image_url
        if not uzu_ogp.get("favicon"):
            uzu_ogp["favicon"] = "https://www.uzu-app.com/favicon.ico"
        sections.append(format_cardlink(uzu_ogp))
        sections.extend(["", "", ""])

    if x_post_url:
        sections.append("!" + "[](" + x_post_url + ")")
        sections.append("")

        need_x_fetch = not x_post_text or not x_image_url
        fetched_x = fetch_x_metadata(x_post_url) if need_x_fetch else {}
        x_card = {
            "url": x_post_url,
            "title": fetched_x.get("title") or x_author_title,
            "description": x_post_text or fetched_x.get("description") or "",
            "host": "x.com",
            "favicon": "https://abs.twimg.com/favicons/twitter.3.ico",
            "image": x_image_url or fetched_x.get("image") or uzu_ogp.get("image", ""),
        }
        sections.append(format_cardlink(x_card))

    if gemini_url:
        gemini_ogp = fetch_ogp(gemini_url)
        if not gemini_ogp.get("title"):
            gemini_ogp["title"] = f"{scenario_title} - Gemini 戦略ログ"
        sections.append("")
        sections.append(format_cardlink(gemini_ogp))

    content = "\n".join(sections).rstrip() + "\n"
    return output_path, content


def load_payload() -> dict[str, object]:
    """Load JSON payload from PAYLOAD_JSON env var or stdin."""
    raw = os.environ.get("PAYLOAD_JSON", "").strip()
    if not raw and not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("No JSON payload provided via PAYLOAD_JSON or stdin")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Payload must be a JSON object")
    return data


def main() -> int:
    payload = load_payload()
    repo_root = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
    rel_dir = str(payload.get("target_dir") or DEFAULT_TARGET_DIR).strip("/")
    target_dir = repo_root / rel_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path, content = build_markdown(payload, target_dir)
    overwrite = str(payload.get("overwrite", "")).lower() in ("1", "true", "yes")
    if output_path.exists() and not overwrite:
        print(f"File already exists, skipping: {output_path}")
        return 0

    output_path.write_text(content, encoding="utf-8")
    print(f"Created Obsidian note: {output_path}")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"created_file={output_path.relative_to(repo_root)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
