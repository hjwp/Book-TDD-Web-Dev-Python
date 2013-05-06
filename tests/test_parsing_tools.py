from lxml import html
from mock import Mock
import os
import tempfile
from textwrap import dedent
import unittest

from parsing_tools import (
    CodeListing,
    Command,
    Output,
    get_commands,
    parse_listing,
    write_to_file
)
from examples import CODE_LISTING_WITH_CAPTION

class ParseListingTest(unittest.TestCase):

    def test_recognises_code_listings(self):
        code_listing = CODE_LISTING_WITH_CAPTION.replace('\n', '\r\n')
        listing_only = html.fromstring(code_listing).cssselect('div.listingblock')[0]
        listings = parse_listing(listing_only)
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


    def test_can_extract_one_command_and_its_output(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n'
            '<div class="content">\r\n'
            '<pre><code>$ <strong>python functional_tests.py</strong>\r\n'
            'Traceback (most recent call last):\r\n'
            '  File "functional_tests.py", line 6, in &lt;module&gt;\r\n'
            '    assert \'Django\' in browser.title\r\n'
            'AssertionError</code></pre>\r\n'
            '</div></div>&#13;\n'
        )
        listing.getnext = Mock()
        parsed_listings = parse_listing(listing)
        self.assertEqual(
            parsed_listings,
            [
                'python functional_tests.py',
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
        listing.getnext = Mock()
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



class GetCommandsTest(unittest.TestCase):

    def test_extracting_one_command(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n<div class="content">\r\n<pre><code>$ <strong>python functional_tests.py</strong>\r\nTraceback (most recent call last):\r\n  File "functional_tests.py", line 6, in &lt;module&gt;\r\n    assert \'Django\' in browser.title\r\nAssertionError</code></pre>\r\n</div></div>&#13;\n'
        )
        self.assertEqual(
            get_commands(listing),
            ['python functional_tests.py']
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


class WriteToFileTest(unittest.TestCase):

    def test_write_to_file_simple_case(self):
        tempdir = tempfile.mkdtemp()
        listing = CodeListing(filename='foo.py', contents='abcdef')
        write_to_file(listing, tempdir)
        with open(os.path.join(tempdir, listing.filename)) as f:
            self.assertEqual(f.read(), listing.contents)
        self.assertTrue(listing.was_written)


    def test_write_to_file_strips_line_callouts(self):
        tempdir = tempfile.mkdtemp()
        listing = CodeListing(
            filename='foo.py',
            contents= 'bla bla #\n'
        )
        write_to_file(listing, tempdir)
        with open(os.path.join(tempdir, listing.filename)) as f:
            self.assertEqual(f.read(), 'bla bla\n')


    def test_write_to_file_with_new_contents_then_indented_elipsis_then_appendix(self):
        tempdir = tempfile.mkdtemp()
        old_contents = '#abc\n#def\n#ghi\n#jkl'
        listing = CodeListing(
            filename='foo.py',
            contents = (
                '#abc\n'
                'def foo(v):\n'
                '    return v + 1\n'
                '    #def\n'
                '    [... old stuff as before]\n'
                '# then add this'
            )
        )
        with open(os.path.join(tempdir, 'foo.py'), 'w') as f:
            f.write(old_contents)

        write_to_file(listing, tempdir)

        with open(os.path.join(tempdir, listing.filename)) as f:
            self.assertMultiLineEqual(
                f.read(),
                (
                    '#abc\n'
                    'def foo(v):\n'
                    '    return v + 1\n'
                    '    #def\n'
                    '    #ghi\n'
                    '    #jkl\n'
                    '# then add this'
                )
            )



if __name__ == '__main__':
    unittest.main()
