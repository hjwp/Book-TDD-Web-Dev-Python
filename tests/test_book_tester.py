from lxml import html
from mock import Mock
import os
import tempfile
from textwrap import dedent
import unittest

from book_tester import (
    ChapterTest,
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
            self.assertEqual(f.read(), listing.contents + '\n')
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
        old_contents = '#abc\n#def\n#ghi\n#jkl\n'
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
                    '# then add this\n'
                )
            )


    def test_write_to_file_with_two_elipsis_dedented_change(self):
        tempdir = tempfile.mkdtemp()
        old_contents = dedent("""
            class Wibble(object):

                def foo(self):
                    return 2

                def bar(self):
                    return 3
            """).lstrip()

        listing = CodeListing(
            filename='foo.py',
            contents = dedent("""
                [...]
                def foo(self):
                    return 4

                def bar(self):
                [...]
                """
            ).strip()
        )

        with open(os.path.join(tempdir, 'foo.py'), 'w') as f:
            f.write(old_contents)

        write_to_file(listing, tempdir)

        with open(os.path.join(tempdir, listing.filename)) as f:
            self.assertMultiLineEqual(
                f.read(),
                dedent("""
                    class Wibble(object):

                        def foo(self):
                            return 4

                        def bar(self):
                            return 3
                    """).lstrip()
            )


class ChapterTestTest(ChapterTest):

    def test_assert_console_output_correct_simple_case(self):
        actual = 'foo'
        expected = Output('foo')
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_assert_console_output_correct_ignores_test_run_times_and_test_dashes(self):
        actual =dedent("""
            bla bla bla

            ----------------------------------------------------------------------
            Ran 1 test in 1.343s
            """).strip()
        expected = Output(dedent("""
            bla bla bla

             ---------------------------------------------------------------------
            Ran 1 test in 1.456s
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_assert_console_output_correct_handles_elipsis(self):
        actual =dedent("""
            bla
            bla bla
            loads more stuff
            """).strip()
        expected = Output(dedent("""
            bla
            bla bla
            [...]
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_assert_console_output_correct_ignores_diff_indexes(self):
        actual =dedent("""
            diff --git a/functional_tests.py b/functional_tests.py
            index d333591..1f55409 100644
            --- a/functional_tests.py
            """).strip()
        expected = Output(dedent("""
            diff --git a/functional_tests.py b/functional_tests.py
            index d333591..b0f22dc 100644
            --- a/functional_tests.py
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


if __name__ == '__main__':
    unittest.main()
