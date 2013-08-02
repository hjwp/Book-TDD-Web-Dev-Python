#!/usr/bin/env python3
from lxml import html
from textwrap import dedent
import unittest

from book_parser import (
    CodeListing,
    Command,
    Output,
    get_commands,
    parse_listing,
)
from examples import (
    CODE_LISTING_WITH_CAPTION,
    CODE_LISTING_WITH_CAPTION_AND_GIT_COMMIT_REF,
    COMMAND_LISTING_WITH_CAPTION,
    COMMANDS_WITH_VIRTUALENV,
)


class CodeListingTest(unittest.TestCase):

    def test_stringify(self):
        c = CodeListing(filename='a.py', contents='abc\ndef')
        assert 'abc' in str(c)
        assert 'a.py' in str(c)


class ParseCodeListingTest(unittest.TestCase):

    def test_recognises_code_listings(self):
        code_html = CODE_LISTING_WITH_CAPTION.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        self.assertEqual(len(listings), 1)
        listing = listings[0]
        self.assertEqual(type(listing), CodeListing)
        self.assertEqual(listing.filename, 'functional_tests.py')
        self.assertEqual(
            listing.contents,
            dedent(
                """
                from selenium import webdriver

                browser = webdriver.Firefox()
                browser.get('http://localhost:8000')

                assert 'Django' in browser.title
                """
            ).strip()
        )
        self.assertFalse('\r' in listing.contents)
        self.assertEqual(listing.commit_ref, None)


    def test_recognises_git_commit_refs(self):
        code_html = CODE_LISTING_WITH_CAPTION_AND_GIT_COMMIT_REF.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        self.assertEqual(len(listings), 1)
        listing = listings[0]
        self.assertEqual(type(listing), CodeListing)
        self.assertEqual(listing.filename, 'functional_tests/tests.py')
        self.assertEqual(listing.commit_ref, 'ch07l001')
        self.assertEqual(listing.type, 'code listing with git ref')


    def test_recognises_server_commands(self):
        code_html = COMMAND_LISTING_WITH_CAPTION.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        print(listings)
        self.assertEqual(len(listings), 4)
        listing = listings[0]
        self.assertEqual(listing.type, 'server command')
        self.assertEqual(listing, 'sudo apt-get install git')


    def test_recognises_virtualenv_commands(self):
        code_html = COMMANDS_WITH_VIRTUALENV.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        print(listings)
        self.assertEqual(len(listings), 3)
        virtualenv_command = listings[1]
        self.assertEqual(virtualenv_command, 'source ../virtualenv/bin/activate && python3 manage.py test lists')


    def test_can_extract_one_command_and_its_output(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n'
            '<div class="content">\r\n'
            '<pre><code>$ <strong>python3 functional_tests.py</strong>\r\n'
            'Traceback (most recent call last):\r\n'
            '  File "functional_tests.py", line 6, in &lt;module&gt;\r\n'
            '    assert \'Django\' in browser.title\r\n'
            'AssertionError</code></pre>\r\n'
            '</div></div>&#13;\n'
        )
        parsed_listings = parse_listing(listing)
        self.assertEqual(
            parsed_listings,
            [
                'python3 functional_tests.py',
                'Traceback (most recent call last):\n'
                '  File "functional_tests.py", line 6, in <module>\n'
                '    assert \'Django\' in browser.title\n'
                'AssertionError'
            ]
        )
        self.assertEqual(type(parsed_listings[0]), Command)
        self.assertEqual(type(parsed_listings[1]), Output)


    def test_extracting_multiple(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n'
            '<div class="content">\r\n'
            '<pre><code>$ <strong>ls</strong>\r\n'
            'superlists          functional_tests.py\r\n'
            '$ <strong>mv functional_tests.py superlists/</strong>\r\n'
            '$ <strong>cd superlists</strong>\r\n'
            '$ <strong>git init .</strong>\r\n'
            'Initialized empty Git repository in /chapter_1/superlists/.git/</code></pre>\r\n'
            '</div></div>&#13;\n'
        )
        parsed_listings = parse_listing(listing)
        self.assertEqual(
            parsed_listings,
            [
                'ls',
                'superlists          functional_tests.py',
                'mv functional_tests.py superlists/',
                'cd superlists',
                'git init .',
                'Initialized empty Git repository in /chapter_1/superlists/.git/'
            ]
        )
        self.assertEqual(type(parsed_listings[0]), Command)
        self.assertEqual(type(parsed_listings[1]), Output)
        self.assertEqual(type(parsed_listings[2]), Command)
        self.assertEqual(type(parsed_listings[3]), Command)
        self.assertEqual(type(parsed_listings[4]), Command)
        self.assertEqual(type(parsed_listings[5]), Output)


    def test_post_command_comment_with_multiple_spaces(self):
        listing = html.fromstring(
            '<div class="listingblock">'
            '<div class="content">'
            '<pre><code>$ <strong>git diff</strong>  # should show changes to functional_tests.py\n'
            '$ <strong>git commit -am "Functional test now checks we can input a to-do item"</strong></code></pre>'
            '</div></div>&#13;'
        )
        commands = get_commands(listing)
        self.assertEqual(
            commands,
            [
                'git diff',
                'git commit -am "Functional test now checks we can input a to-do item"',
            ]
        )

        parsed_listings = parse_listing(listing)
        self.assertEqual(
            parsed_listings,
            [
                'git diff',
                '# should show changes to functional_tests.py',
                'git commit -am "Functional test now checks we can input a to-do item"',
            ]
        )
        self.assertEqual(type(parsed_listings[0]), Command)
        self.assertEqual(type(parsed_listings[1]), Output)
        self.assertEqual(type(parsed_listings[2]), Command)



    def test_specialcase_for_asterisk(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n<div class="content">\r\n<pre><code>$ <strong>git rm --cached superlists/</strong>*<strong>.pyc</strong>\r\nrm <em>superlists/__init__.pyc</em>\r\nrm <em>superlists/settings.pyc</em>\r\nrm <em>superlists/urls.pyc</em>\r\nrm <em>superlists/wsgi.pyc</em>\r\n\r\n$ <strong>echo "*.pyc" &gt; .gitignore</strong></code></pre>\r\n</div></div>&#13;\n'
        )
        self.assertEqual(
            get_commands(listing),
            [
                'git rm --cached superlists/*.pyc',
                'echo "*.pyc" > .gitignore',
            ]
        )


    def test_catches_command_with_trailing_comment(self):
        listing = html.fromstring(
            dedent("""
                <div class="listingblock">
                    <div class="content">
                        <pre><code>$ <strong>git diff --staged</strong> # will show you the diff that you're about to commit
                </code></pre>
                </div></div>
                """)
        )
        parsed_listings = parse_listing(listing)
        self.assertEqual(
            parsed_listings,
            [
                "git diff --staged",
                "# will show you the diff that you're about to commit",
            ]
        )
        self.assertEqual(type(parsed_listings[0]), Command)
        self.assertEqual(type(parsed_listings[1]), Output)



class GetCommandsTest(unittest.TestCase):

    def test_extracting_one_command(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n<div class="content">\r\n<pre><code>$ <strong>python3 functional_tests.py</strong>\r\nTraceback (most recent call last):\r\n  File "functional_tests.py", line 6, in &lt;module&gt;\r\n    assert \'Django\' in browser.title\r\nAssertionError</code></pre>\r\n</div></div>&#13;\n'
        )
        self.assertEqual(
            get_commands(listing),
            ['python3 functional_tests.py']
        )

    def test_extracting_multiple(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n<div class="content">\r\n<pre><code>$ <strong>ls</strong>\r\nsuperlists          functional_tests.py\r\n$ <strong>mv functional_tests.py superlists/</strong>\r\n$ <strong>cd superlists</strong>\r\n$ <strong>git init .</strong>\r\nInitialized empty Git repository in /chapter_1/superlists/.git/</code></pre>\r\n</div></div>&#13;\n'
        )
        self.assertEqual(
            get_commands(listing),
            [
                'ls',
                'mv functional_tests.py superlists/',
                'cd superlists',
                'git init .',
            ]
        )


    def test_specialcase_for_asterisk(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n<div class="content">\r\n<pre><code>$ <strong>git rm --cached superlists/</strong>*<strong>.pyc</strong>\r\nrm <em>superlists/__init__.pyc</em>\r\nrm <em>superlists/settings.pyc</em>\r\nrm <em>superlists/urls.pyc</em>\r\nrm <em>superlists/wsgi.pyc</em>\r\n\r\n$ <strong>echo "*.pyc" &gt; .gitignore</strong></code></pre>\r\n</div></div>&#13;\n'
        )
        self.assertEqual(
            get_commands(listing),
            [
                'git rm --cached superlists/*.pyc',
                'echo "*.pyc" > .gitignore',
            ]
        )


if __name__ == '__main__':
    unittest.main()
