#!/usr/bin/env python

import json
import subprocess
from collections import namedtuple
from pathlib import Path

from lxml import html

DEST = Path("~/workspace/www.obeythetestinggoat.com/content/book").expanduser()

CHAPTERS = [
    c.replace(".asciidoc", ".html")
    for c in json.loads(Path("atlas.json").read_text())["files"]
]
for tweak_chap in ["praise.html", "part1.html", "part2.html", "part3.html"]:
    CHAPTERS[CHAPTERS.index(tweak_chap)] = tweak_chap.replace(".", ".forbook.")
CHAPTERS.remove("cover.html")
CHAPTERS.remove("titlepage.html")
CHAPTERS.remove("copyright.html")
CHAPTERS.remove("toc.html")
CHAPTERS.remove("ix.html")
CHAPTERS.remove("author_bio.html")
CHAPTERS.remove("colo.html")

ChapterInfo = namedtuple("ChapterInfo", "href_id chapter_title subheaders xrefs")


def make_chapters():
    for chapter in CHAPTERS:
        subprocess.check_call(["make", chapter], stdout=subprocess.PIPE)


def parse_chapters():
    for chapter in CHAPTERS:
        raw_html = Path(chapter).read_text()
        yield chapter, html.fromstring(raw_html)


def get_anchor_targets(parsed_html):
    ignores = {"header", "content", "footnotes", "footer", "footer-text"}
    all_ids = [a.get("id") for a in parsed_html.cssselect("*[id]")]
    return [i for i in all_ids if not i.startswith("_") and i not in ignores]


def get_chapter_info():
    chapter_info = {}
    appendix_numbers = list("ABCDEFGHIJKL")
    chapter_numbers = list(range(1, 100))
    part_numbers = list(range(1, 10))

    for chapter, parsed_html in parse_chapters():
        print("getting info from", chapter)

        if not parsed_html.cssselect("h2"):
            header = parsed_html.cssselect("h1")[0]
        else:
            header = parsed_html.cssselect("h2")[0]
        href_id = header.get("id")
        if href_id is None:
            href_id = parsed_html.cssselect("body")[0].get("id")
        subheaders = [h.get("id") for h in parsed_html.cssselect("h3")]

        chapter_title = header.text_content()
        chapter_title = chapter_title.replace("Appendix A: ", "")

        if chapter.startswith("chapter_"):
            chapter_no = chapter_numbers.pop(0)
            chapter_title = f"Chapter {chapter_no}: {chapter_title}"

        if chapter.startswith("appendix_"):
            appendix_no = appendix_numbers.pop(0)
            chapter_title = f"Appendix {appendix_no}: {chapter_title}"

        if chapter.startswith("part"):
            part_no = part_numbers.pop(0)
            chapter_title = f"Part {part_no}: {chapter_title}"

        if chapter.startswith("epilogue"):
            chapter_title = f"Epilogue: {chapter_title}"

        xrefs = get_anchor_targets(parsed_html)
        chapter_info[chapter] = ChapterInfo(href_id, chapter_title, subheaders, xrefs)

    return chapter_info


def fix_xrefs(contents, chapter, chapter_info):
    parsed = html.fromstring(contents)
    links = parsed.cssselect(r"a[href^=\#]")
    for link in links:
        for other_chap in CHAPTERS:
            if other_chap == chapter:
                continue
            chapter_id = chapter_info[other_chap].href_id
            href = link.get("href")
            targets = ["#" + x for x in chapter_info[other_chap].xrefs]
            if href == "#" + chapter_id:
                link.set("href", f"/book/{other_chap}")
            elif href in targets:
                link.set("href", f"/book/{other_chap}{href}")

    return html.tostring(parsed)


def fix_title(contents, chapter, chapter_info):
    parsed = html.fromstring(contents)
    titles = parsed.cssselect("h2")
    if titles and titles[0].text.startswith("Appendix A"):
        title = titles[0]
        title.text = chapter_info[chapter].chapter_title
    return html.tostring(parsed)


def copy_chapters_across_with_fixes(chapter_info, fixed_toc):
    comments_html = Path("disqus_comments.html").read_text()
    buy_book_div = html.fromstring(Path("buy_the_book_banner.html").read_text())
    analytics_div = html.fromstring(Path("analytics.html").read_text())
    load_toc_script = Path("load_toc.js").read_text()

    for chapter in CHAPTERS:
        old_contents = Path(chapter).read_text()
        new_contents = fix_xrefs(old_contents, chapter, chapter_info)
        new_contents = fix_title(new_contents, chapter, chapter_info)
        parsed = html.fromstring(new_contents)
        body = parsed.cssselect("body")[0]
        if parsed.cssselect("#header"):
            head = parsed.cssselect("head")[0]
            head.append(
                html.fragment_fromstring("<script>" + load_toc_script + "</script>")
            )
            body.set("class", "article toc2 toc-left")
        body.insert(0, buy_book_div)
        body.append(
            html.fromstring(
                comments_html.replace("CHAPTER_NAME", chapter.split(".")[0])
            )
        )
        body.append(analytics_div)
        fixed_contents = html.tostring(parsed)

        with open(DEST / chapter, "w") as f:
            f.write(fixed_contents.decode("utf8"))
        with open(DEST / "toc.html", "w") as f:
            f.write(html.tostring(fixed_toc).decode("utf8"))


def extract_toc_from_book():
    subprocess.check_call(["make", "book.html"], stdout=subprocess.PIPE)
    parsed = html.fromstring(Path("book.html").read_text())
    return parsed.cssselect("#toc")[0]


def fix_toc(toc, chapter_info):
    href_mappings = {}
    for chapter in CHAPTERS:
        chap = chapter_info[chapter]
        if chap.href_id:
            href_mappings["#" + chap.href_id] = f"/book/{chapter}"
        for subheader in chap.subheaders:
            href_mappings["#" + subheader] = f"/book/{chapter}#{subheader}"

    def fix_link(href):
        if href in href_mappings:
            return href_mappings[href]
        else:
            return href

    toc.rewrite_links(fix_link)
    toc.set("class", "toc2")
    return toc


def print_toc_md(chapter_info):
    for chapter in CHAPTERS:
        title = chapter_info[chapter].chapter_title
        print(f"* [{title}](/book/{chapter})")


def rsync_images():
    subprocess.run(
        ["rsync", "-a", "-v", "images/", DEST / "images/"],
        check=True,
    )


def main():
    make_chapters()
    toc = extract_toc_from_book()
    chapter_info = get_chapter_info()
    fixed_toc = fix_toc(toc, chapter_info)
    copy_chapters_across_with_fixes(chapter_info, fixed_toc)
    rsync_images()
    print_toc_md(chapter_info)


if __name__ == "__main__":
    main()
