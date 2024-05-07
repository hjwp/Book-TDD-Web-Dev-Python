#!/usr/bin/env python
from lxml import html
import re
from textwrap import dedent
import unittest

from book_parser import (
    COMMIT_REF_FINDER,
    CodeListing,
    Command,
    Output,
    get_commands,
    parse_listing,
    _strip_callouts,
)
import examples



class CodeListingTest(unittest.TestCase):

    def test_stringify(self):
        c = CodeListing(filename='a.py', contents='abc\ndef')
        assert 'abc' in str(c)
        assert 'a.py' in str(c)
        assert c.is_server_listing is False


    def test_server_codelisting(self):
        c = CodeListing(filename='server: a_filename.py', contents='foo')
        assert c.contents == 'foo'
        assert c.filename == 'a_filename.py'
        assert c.is_server_listing is True


class CommitRefFinderTest(unittest.TestCase):

    def test_base_finder(self):
        assert re.search(COMMIT_REF_FINDER, 'bla bla ch09l027-2')
        assert re.findall(COMMIT_REF_FINDER, 'bla bla ch09l027-2') == ['ch09l027-2']
        assert not re.search(COMMIT_REF_FINDER, 'bla bla 09l6666')

    def test_finder_on_codelisting(self):
        matches = re.match(
            CodeListing.COMMIT_REF_FINDER,
            'some_filename.txt (ch09l027-2)'
        )
        assert matches.group(1) == 'some_filename.txt'
        assert matches.group(2) == 'ch09l027-2'


class ParseCodeListingTest(unittest.TestCase):

    def test_recognises_code_listings(self):
        code_html = examples.CODE_LISTING_WITH_CAPTION.replace('\n', '\r\n')
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
        code_html = examples.CODE_LISTING_WITH_CAPTION_AND_GIT_COMMIT_REF.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        self.assertEqual(len(listings), 1)
        listing = listings[0]
        self.assertEqual(type(listing), CodeListing)
        self.assertEqual(listing.filename, 'functional_tests/tests.py')
        self.assertEqual(listing.commit_ref, 'ch06l001')
        self.assertEqual(listing.type, 'code listing with git ref')


    def test_recognises_git_commit_refs_even_if_formatted_as_diffs(self):
        code_html = examples.CODE_LISTING_WITH_DIFF_FORMATING_AND_COMMIT_REF.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        self.assertEqual(len(listings), 1)
        listing = listings[0]
        self.assertEqual(type(listing), CodeListing)
        self.assertEqual(listing.filename, 'lists/tests/test_models.py')
        self.assertEqual(listing.commit_ref, 'ch09l010')
        self.assertEqual(listing.type, 'code listing with git ref')
        self.assertTrue(listing.is_diff())

    def test_recognises_diffs_even_if_they_dont_have_atat(self):
        code_html = examples.EXAMPLE_DIFF_LISTING.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        [listing] = parse_listing(node)
        self.assertEqual(listing.type, 'code listing with git ref')
        self.assertTrue(listing.is_diff())


    def test_recognises_skipme_tag_on_unmarked_code_listing(self):
        code_html = examples.OUTPUT_WITH_SKIPME.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        self.assertEqual(len(listings), 1)
        listing = listings[0]
        self.assertEqual(listing.skip, True)


    def test_recognises_skipme_tag_on_code_listing(self):
        code_html = examples.CODE_LISTING_WITH_SKIPME.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        self.assertEqual(len(listings), 1)
        listing = listings[0]
        self.assertEqual(listing.skip, True)


    def test_recognises_currentcontents_tag(self):
        code_html = examples.OUTPUTS_WITH_CURRENTCONTENTS.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        self.assertEqual(len(listings), 1)
        listing = listings[0]
        assert listing.currentcontents is True
        assert listing.type == 'code listing currentcontents'


    def test_recognises_dofirst_tag(self):
        code_html = examples.OUTPUTS_WITH_DOFIRST.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        listing = listings[0]
        assert listing.dofirst == 'ch09l058'
        self.assertEqual(len(listings), 2)


    def test_recognises_qunit_tag(self):
        code_html = examples.OUTPUT_QUNIT.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        self.assertEqual(len(listings), 1)
        listing = listings[0]
        self.assertEqual(listing.type, 'qunit output')
        self.assertEqual(
            listing,
            '2 assertions of 2 passed, 0 failed.\n1. smoke test (2)'
        )

    def test_recognises_server_commands(self):
        code_html = examples.SERVER_COMMAND.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        print(listings)
        self.assertEqual(len(listings), 1)
        listing = listings[0]
        self.assertEqual(listing.type, 'server command')
        self.assertEqual(listing, 'sudo do stuff')


    def test_recognises_virtualenv_commands(self):
        code_html = examples.COMMANDS_WITH_VIRTUALENV.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        print(listings)
        virtualenv_command = listings[1]
        self.assertEqual(virtualenv_command, 'source ./.venv/bin/activate && python manage.py test lists')
        self.assertEqual(len(listings), 3)


    def test_recognises_command_with_ats(self):
        code_html = examples.COMMAND_MADE_WITH_ATS.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        print(listings)
        self.assertEqual(len(listings), 1)
        command = listings[0]
        self.assertEqual(command, 'grep id_new_item functional_tests/tests/test*')
        self.assertEqual(command.type, 'other command')


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
                '  # should show changes to functional_tests.py',
                'git commit -am "Functional test now checks we can input a to-do item"',
            ]
        )
        self.assertEqual(type(parsed_listings[0]), Command)
        self.assertEqual(type(parsed_listings[1]), Output)
        self.assertEqual(type(parsed_listings[2]), Command)



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
                " # will show you the diff that you're about to commit",
            ]
        )
        self.assertEqual(type(parsed_listings[0]), Command)
        self.assertEqual(type(parsed_listings[1]), Output)


    def test_handles_multiline_commands(self):
        listing = html.fromstring(dedent(
            """
            <div class="listingblock">
            <div class="content">
            <pre><code>$ <strong>do something\\
            that continues on this line</strong>
            OK
            </code></pre>
            </div></div>
                """
        ))
        commands = get_commands(listing)
        assert len(commands) == 1
        #assert commands[0] == 'do something\\\nthat continues on this line'
        assert commands[0] == 'do somethingthat continues on this line'

        # too hard for now
        parsed_listings = parse_listing(listing)
        print(parsed_listings)
        self.assertEqual(type(parsed_listings[0]), Command)
        self.assertEqual(parsed_listings[0], commands[0])


    def test_handles_inline_inputs(self):
        listing = html.fromstring(examples.OUTPUT_WITH_COMMANDS_INLINE)
        commands = get_commands(listing)
        self.assertEqual(
            [str(c) for c in commands],
            [
                'python manage.py makemigrations',
                '1',
                "''",
            ]
        )

        # too hard for now
        parsed_listings = parse_listing(listing)
        print(parsed_listings)
        self.assertEqual(type(parsed_listings[0]), Command)
        self.assertEqual(parsed_listings[0], commands[0])

        print(parsed_listings[1])
        self.assertIn('Select an option:', parsed_listings[1])
        self.assertTrue(
            parsed_listings[1].endswith('Select an option: ')
        )


    def test_strips_asciidoctor_callouts_from_code(self):
        code_html = examples.CODE_LISTING_WITH_ASCIIDOCTOR_CALLOUTS.replace('\n', '\r\n')
        node = html.fromstring(code_html)
        listings = parse_listing(node)
        listing = listings[0]
        self.assertEqual(type(listing), CodeListing)
        self.assertNotIn('(1)', listing.contents)
        self.assertNotIn('(2)', listing.contents)
        self.assertNotIn('(3)', listing.contents)
        self.assertNotIn('(4)', listing.contents)
        self.assertNotIn('(7)', listing.contents)


    def test_strips_asciidoctor_callouts_from_output(self):
        listing_html = examples.OUTPUT_WITH_CALLOUTS.replace('\n', '\r\n')
        node = html.fromstring(listing_html)
        listings = parse_listing(node)
        output = listings[1]
        self.assertEqual(type(output), Output)
        self.assertNotIn('(1)', output)
        # self.assertIn('assertEqual(\n', output)  ## TODO: re-enable


    def test_strip_callouts_helper(self):
        self.assertEqual(
            _strip_callouts('foo  (1)'),
            'foo'
        )
        self.assertEqual(
            _strip_callouts('foo (1)'),
            'foo'
        )
        self.assertEqual(
            _strip_callouts('foo (112)'),
            'foo'
        )
        self.assertEqual(
            _strip_callouts('line1\nline2 (2)\nline3'),
            'line1\nline2\nline3'
        )
        self.assertEqual(
            _strip_callouts('foo  (ya know)  (2)'),
            'foo  (ya know)'
        )
        self.assertEqual(
            _strip_callouts('foo  (1)\n  bar  (7)'),
            'foo\n  bar'
        )
        self.assertEqual(
            _strip_callouts('foo  (1)\n  bar  (7)\n'),
            'foo\n  bar\n'
        )

        self.assertEqual(
            _strip_callouts('foo  (hi)'),
            'foo  (hi)',
        )
        self.assertEqual(
            _strip_callouts('this  (4) foo'),
            'this  (4) foo',
        )
        self.assertEqual(
            _strip_callouts('foo(1)'),
            'foo(1)',
        )
        self.assertEqual(
            _strip_callouts('foo  (1) (2)'),
            'foo'
        )
        self.assertEqual(
            _strip_callouts('<form>  (1)'),
            '<form>'
        )



class GetCommandsTest(unittest.TestCase):

    def test_extracting_one_command(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n<div class="content">\r\n<pre><code>$ <strong>python functional_tests.py</strong>\r\nTraceback (most recent call last):\r\n  File "functional_tests.py", line 6, in &lt;module&gt;\r\n    assert \'Django\' in browser.title\r\nAssertionError</code></pre>\r\n</div></div>&#13;\n'  # noqa
        )
        self.assertEqual(
            get_commands(listing),
            ['python functional_tests.py']
        )

    def test_extracting_multiple(self):
        listing = html.fromstring(
            '<div class="listingblock">\r\n<div class="content">\r\n<pre><code>$ <strong>ls</strong>\r\nsuperlists          functional_tests.py\r\n$ <strong>mv functional_tests.py superlists/</strong>\r\n$ <strong>cd superlists</strong>\r\n$ <strong>git init .</strong>\r\nInitialized empty Git repository in /chapter_1/superlists/.git/</code></pre>\r\n</div></div>&#13;\n'  # noqa
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

