#!/usr/bin/env python

import os
from lxml import html
import subprocess

CHAPTERS = [
    "praise.harry.html",
    "preface.html",
    "pre-requisite-installations.html",
    "video_plug.html",
    "acknowledgments.html",

    "part1.harry.html",
    "chapter_01.html",
    "chapter_02_unittest.html",
    "chapter_unit_test_first_view.html",
    "chapter_philosophy_and_refactoring.html",
    "chapter_post_and_database.html",
    "chapter_explicit_waits_1.html",

    "part2.harry.html",
    "chapter_working_incrementally.html",
    "chapter_prettification.html",
    "chapter_manual_deployment.html",
    "chapter_automate_deployment_with_fabric.html",
    "chapter_database_layer_validation.html",
    "chapter_simple_form.html",
    "chapter_advanced_forms.html",
    "chapter_javascript.html",

    "part3.harry.html",
    "chapter_deploying_validation.html",
    "chapter_spiking_custom_auth.html",
    "chapter_mocking.html",
    "chapter_fixtures_and_debugging_staging.html",
    "chapter_outside_in.html",
    "chapter_purist_unit_tests.html",
    "chapter_CI.html",
    "chapter_page_pattern.html",
    "epilogue.html",

    "appendix_I_PythonAnywhere.html",
    "appendix_II_Django_Class-Based_Views.html",
    "appendix_III_provisioning_with_ansible.html",
    "appendix_IV_testing_migrations.html",
    "appendix_V_bdd_tools.html",
    "appendix_VI_rest_api.html",
    "appendix_VII_DjangoRestFramework.html",
    "appendix_IX_cheat_sheet.html",
    "appendix_X_what_to_do_next.html",

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
        'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'IX', 'X'
    ]
    chapter_numbers = list(range(1, 100))
    part_numbers = list(range(1, 10))

    for chapter, parsed_html in parse_chapters():
        print('getting info from', chapter)

        if not parsed_html.cssselect('h2'):
            header = parsed_html.cssselect('h1')[0]
        else:
            header = parsed_html.cssselect('h2')[0]
        href_id = header.get('id')
        if href_id is None:
            href_id = parsed_html.cssselect('body')[0].get('id')
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


        chapter_info[chapter] = href_id, chapter_title, subheaders

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
    comments_div = html.fromstring(open('disqus_comments.html').read())
    buy_book_div = html.fromstring(open('buy_the_book_banner.html').read())
    analytics_div = html.fromstring(open('analytics.html').read())
    load_toc_script = open('load_toc.js').read()

    for chapter in CHAPTERS:
        new_contents = fix_xrefs(chapter, chapter_info)
        parsed = html.fromstring(new_contents)
        body = parsed.cssselect('body')[0]
        if parsed.cssselect('#header'):
            head = parsed.cssselect('head')[0]
            head.append(html.fragment_fromstring('<script>' + load_toc_script + '</script>'))
            body.set('class', 'article toc2 toc-left')
        body.insert(0, buy_book_div)
        body.append(comments_div)
        body.append(analytics_div)
        fixed_contents = html.tostring(parsed)

        target = os.path.join('/home/harry/workspace/www.obeythetestinggoat.com/content/book', chapter)
        with open(target, 'w') as f:
            f.write(fixed_contents.decode('utf8'))
        toc = '/home/harry/workspace/www.obeythetestinggoat.com/content/book/toc.html'
        with open(toc, 'w') as f:
            f.write(html.tostring(fixed_toc).decode('utf8'))


def extract_toc_from_book():
    subprocess.check_call(['make', 'book.html'], stdout=subprocess.PIPE)
    parsed = html.fromstring(open('book.html').read())
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
