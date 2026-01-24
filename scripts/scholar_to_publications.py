#!/usr/bin/env python3
"""
从 Google Scholar 抓取出版物列表，生成 _includes/generated_publications.html
用于 Publications 页面自动展示。

依赖: pip install scholarly

用法（在项目根目录）:
  python scripts/scholar_to_publications.py

或指定 Scholar 用户 ID:
  python scripts/scholar_to_publications.py --user o3Q56qsAAAAJ

说明:
- 若被 Google 限流，可尝试使用代理，见 scholarly 文档。
- 生成的文件会覆盖 _includes/generated_publications.html；失败时不会覆盖原文件。
"""

import argparse
import html
import os
import re
import sys

# 需在项目根目录运行
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT = os.path.join(ROOT, "_includes", "generated_publications.html")

# 需要在作者字符串中加粗的名称模式（按优先级）
BOLD_PATTERNS = ["Xuanlong Yu", "X. Yu", "X Yu"]


def bold_author(authors_str: str) -> str:
    """在作者字符串中把本人加粗。"""
    out = html.escape(authors_str)
    for p in BOLD_PATTERNS:
        newout = re.sub(re.escape(p), f"<strong>{html.escape(p)}</strong>", out, count=1)
        if newout != out:
            return newout
    return out


def main():
    parser = argparse.ArgumentParser(description="从 Google Scholar 生成 publications 列表")
    parser.add_argument("--user", default="o3Q56qsAAAAJ", help="Google Scholar 用户 ID")
    args = parser.parse_args()

    try:
        from scholarly import scholarly
    except ImportError:
        print("请先安装: pip install scholarly", file=sys.stderr)
        sys.exit(1)

    try:
        author = scholarly.search_author_id(args.user)
        author = scholarly.fill(
            author,
            sections=["publications"],
            sortby="year",
            publication_limit=0,
        )
    except Exception as e:
        print(f"获取 Scholar 数据失败: {e}", file=sys.stderr)
        print("未修改 _includes/generated_publications.html", file=sys.stderr)
        sys.exit(1)

    pubs = author.get("publications") or []
    rows = []

    for p in pubs:
        bib = p.get("bib") or {}
        title = bib.get("title") or "(无标题)"
        title = html.escape(title)

        auth = bib.get("author")
        if isinstance(auth, list):
            authors_str = ", ".join(auth)
        else:
            authors_str = auth or ""
        authors_html = bold_author(authors_str)

        venue = bib.get("venue") or ""
        year = bib.get("pub_year") or bib.get("year") or ""
        venue_year = ", ".join(filter(None, [venue, str(year)]))
        venue_year = html.escape(venue_year)

        url = p.get("pub_url") or p.get("eprint_url") or ""
        if url:
            url = html.escape(url)
            link_part = f' [<a href="{url}">链接</a>]'
        else:
            link_part = ""

        rows.append((title, link_part, authors_html, venue_year))

    # 按年份倒序（已按 year 排序时，fill 可能按 citedby，这里再排一次更稳）
    def year_key(r):
        v = r[3]
        m = re.search(r"20\d{2}", v)
        return int(m.group(0)) if m else 0

    rows.sort(key=year_key, reverse=True)

    blocks = []
    for title, link_part, authors_html, venue_year in rows:
        blocks.append(
            f"<p><strong>{title}</strong>{link_part}<br>\n"
            f"{authors_html}<br>\n"
            f"<em>{venue_year}</em></p>\n"
        )
    blocks.append("<p>*equal contribution</p>\n")

    html_content = "\n".join(blocks)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"已生成 {len(rows)} 条出版物 -> {OUTPUT}")


if __name__ == "__main__":
    main()
