#!/usr/bin/env python

import os
from lxml import html
import subprocess

CHAPTERS = [
    "praise.html",
    "preface.html",
    "pre-requisite-installations.html",
    "video_plug.html",
    "acknowledgments.html",

    "part1.harry.html",
    "chapter_01.html",
    "chapter_02.html",
    "chapter_03.html",
    "chapter_04.html",
    "chapter_05.html",
    "chapter_06.html",

    "part2.harry.html",
    "chapter_07.html",
    "chapter_08.html",
    "chapter_09.html",
    "chapter_10.html",
    "chapter_11.html",
    "chapter_12.html",
    "chapter_14.html",
    # NB - 14 is intentionally before 13.
    "chapter_13.html",

    "part3.harry.html",
    "chapter_15.html",
    "chapter_16.html",
    "chapter_17.html",
    "chapter_18.html",
    "chapter_19.html",
    "chapter_20.html",
    "chapter_21.html",
    "chapter_22.html",
    "epilogue.html",

    "appendix_I_PythonAnywhere.html",
    "appendix_II_Django_Class-Based_Views.html",
    "appendix_III_provisioning_with_ansible.html",
    "appendix_IV_testing_migrations.html",
    "appendix_bdd_tools.html",
    "appendix_V_what_to_do_next.html",
    "appendix_VI_cheat_sheet.html",

    "bibliography.html",
]



def make_chapters():
    for chapter in CHAPTERS:
        subprocess.check_call(['make', chapter], stdout=subprocess.PIPE)


def parse_chapters():
    for chapter in CHAPTERS:
        raw_html = open(chapter).read()
        yield chapter, html.fromstring(raw_html)


def get_chapter_info():
    chapter_info = {}
    appendix_numbers = [
        'I', 'II', 'III', 'IV', 'V', 'VI', 'VII'
    ]
    chapter_numbers = list(range(1, 100))
    part_numbers = list(range(1, 10))
    for chapter, parsed_html in parse_chapters():
        print('getting info from', chapter)
        if not parsed_html.cssselect('h2'):
            header = parsed_html.cssselect('h1')[0]
        else:
            header = parsed_html.cssselect('h2')[0]
        subheaders = [h.get('id') for h in parsed_html.cssselect('h3')]

        chapter_title = header.text_content()
        chapter_title = chapter_title.replace('Appendix A: ', '')

        if chapter.startswith('chapter_'):
            chapter_no = chapter_numbers.pop(0)
            chapter_title = 'Chapter {}: {}'.format(chapter_no, chapter_title)

        if chapter.startswith('appendix_'):
            appendix_no = appendix_numbers.pop(0)
            chapter_title = 'Appendix {}: {}'.format(appendix_no, chapter_title)

        if chapter.startswith('part'):
            part_no = part_numbers.pop(0)
            chapter_title = 'Part {}: {}'.format(part_no, chapter_title)

        if chapter.startswith('epilogue'):
            chapter_title = 'Epilogue: {}'.format(chapter_title)


        chapter_info[chapter] = header.get('id'), chapter_title, subheaders

    return chapter_info


def fix_xrefs(chapter, chapter_info):
    contents = open(chapter).read()
    for other_chap in CHAPTERS:
        html_id, chapter_title, subheaders = chapter_info[other_chap]
        old_tag = 'href="#{}"'.format(html_id)
        new_tag = 'href="/book/{}"'.format(other_chap)
        if old_tag in contents:
            contents = contents.replace(old_tag, new_tag)
    return contents


def copy_chapters_across_fixing_xrefs(chapter_info, fixed_toc):
    for chapter in CHAPTERS:
        new_contents = fix_xrefs(chapter, chapter_info)
        parsed = html.fromstring(new_contents)
        if parsed.cssselect('#header'):
            header = parsed.cssselect('#header')[0]
            header.append(fixed_toc)
            body = parsed.cssselect('body')[0]
            body.set('class', 'article toc2 toc-left')
        fixed_contents = html.tostring(parsed)

        target = os.path.join('/home/harry/workspace/www.obeythetestinggoat.com/content/book', chapter)
        with open(target, 'w') as f:
            f.write(fixed_contents.decode('utf8'))


def extract_toc_from_book():
    subprocess.check_call(['make', 'book.harry.html'], stdout=subprocess.PIPE)
    parsed = html.fromstring(open('book.harry.html').read())
    return parsed.cssselect('#toc')[0]



def fix_toc(toc, chapter_info):
    href_mappings = {}
    for chapter in CHAPTERS:
        html_id, chapter_title, subheaders = chapter_info[chapter]
        if html_id:
            href_mappings['#' + html_id] = '/book/{}'.format(chapter)
        for subheader in subheaders:
            href_mappings['#' + subheader] = '/book/{}#{}'.format(chapter, subheader)

    def fix_link(href):
        if href in href_mappings:
            return href_mappings[href]
        else:
            return href

    toc.rewrite_links(fix_link)
    toc.set('class', 'toc2')
    return toc


def print_toc_md(chapter_info):
    for chapter in CHAPTERS:
        html_id, chapter_title, subheaders = chapter_info[chapter]
        print('* [{title}](/book/{link})'.format(title=chapter_title, link=chapter))


def main():
    make_chapters()
    toc = extract_toc_from_book()
    chapter_info = get_chapter_info()
    fixed_toc = fix_toc(toc, chapter_info)
    copy_chapters_across_fixing_xrefs(chapter_info, fixed_toc)
    print_toc_md(chapter_info)


if __name__ == '__main__':
    main()
