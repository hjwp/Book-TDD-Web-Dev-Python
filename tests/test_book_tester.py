from lxml import html
import os
import shutil
import tempfile
from textwrap import dedent
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
    Output,
    _find_last_line_for_class,
    _replace_function,
    get_commands,
    number_of_identical_chars,
    parse_listing,
    wrap_long_lines,
    write_to_file,
)
from examples import CODE_LISTING_WITH_CAPTION


class ClassFinderTest(unittest.TestCase):

    def test_find_last_line_for_class(self):
        source = dedent(
            """
            import topline

            class ClassA(object):
                def metha(self):
                    pass

                def metha2(self):
                    pass

            class ClassB(object):
                def methb(self):
                    pass
            """
        )

        lineno = _find_last_line_for_class(source, 'ClassA')
        self.assertEqual(lineno, 9)
        # sanity-check
        self.assertEqual(source.split('\n')[lineno -1].strip(), 'pass')

        lineno = _find_last_line_for_class(source, 'ClassB')
        self.assertEqual(lineno, 13)



class ReplaceFunctionTest(unittest.TestCase):

    def test_changing_the_end_of_a_method(self):
        old = dedent("""
            class A(object):
                def method1(self):
                    # do step 1
                    # do step 2
                    # do step 3
                    # do step 4
                    # do step 5
                    pass

                def method2(self):
                    # do stuff
                    pass
            """
        )
        new = dedent("""
            def method1(self):
                # do step 1
                # do step 2
                # do step A
                # do step B
            """
        ).strip()
        expected = dedent("""
            class A(object):
                def method1(self):
                    # do step 1
                    # do step 2
                    # do step A
                    # do step B

                def method2(self):
                    # do stuff
                    pass
            """
        )
        result = _replace_function(old.split('\n'), new.split('\n'))
        self.assertMultiLineEqual(result, expected)



class WrapLongLineTest(unittest.TestCase):

    def test_wrap_long_lines_with_words(self):
        self.assertEqual(wrap_long_lines('normal line'), 'normal line')
        text = (
            "This is a short line\n"
            "This is a long line which should wrap just before the word that "
            "takes it over 79 chars in length\n"
            "This line is fine though."
        )
        expected_text = (
            "This is a short line\n"
            "This is a long line which should wrap just before the word that "
            "takes it over\n"
            "79 chars in length\n"
            "This line is fine though."
        )
        self.assertMultiLineEqual(wrap_long_lines(text), expected_text)


    def test_wrap_long_lines_with_words_2(self):
        text = "ViewDoesNotExist: Could not import superlists.views.home. Parent module superlists.views does not exist."
        expected_text = "ViewDoesNotExist: Could not import superlists.views.home. Parent module\nsuperlists.views does not exist."
        self.assertMultiLineEqual(wrap_long_lines(text), expected_text)


    def test_wrap_long_lines_with_words_3(self):

        text = '  File "/usr/local/lib/python2.7/dist-packages/django/db/backends/__init__.py", line 442, in supports_transactions'
        expected_text = '  File "/usr/local/lib/python2.7/dist-packages/django/db/backends/__init__.py",\nline 442, in supports_transactions'
        self.assertMultiLineEqual(wrap_long_lines(text), expected_text)


    def test_wrap_long_lines_doesnt_swallow_spaces(self):
        text  =  "A  really  long  line  that  uses  multiple  spaces  to  go  over  80  chars  by  a  country  mile"
        expected_text = "A  really  long  line  that  uses  multiple  spaces  to  go  over  80  chars\nby  a  country  mile"
        #TODO: handle trailing space corner case?
        self.assertMultiLineEqual(wrap_long_lines(text), expected_text)


    def test_wrap_long_lines_with_unbroken_chars(self):
        text = "." * 479
        expected_text = (
                "." * 79 + "\n" +
                "." * 79 + "\n" +
                "." * 79 + "\n" +
                "." * 79 + "\n" +
                "." * 79 + "\n" +
                "." * 79 + "\n" +
                "....."
        )
        self.assertMultiLineEqual(wrap_long_lines(text), expected_text)


    def test_wrap_long_lines_with_unbroken_chars_2(self):
        text = (
            "E\n"
            "======================================================================\n"
            "ERROR: test_root_url_resolves_to_home_page_view (lists.tests.HomePageTest)"
        )
        expected_text = (
            "E\n"
            "======================================================================\n"
            "ERROR: test_root_url_resolves_to_home_page_view (lists.tests.HomePageTest)"
        )
        self.assertMultiLineEqual(wrap_long_lines(text), expected_text)



    def test_wrap_long_lines_with_indent(self):
        text = (
            "This is a short line\n"
            "   This is a long line with an indent which should wrap just "
            "before the word that takes it over 79 chars in length\n"
            "   This is a short indented line\n"
            "This is a long line which should wrap just before the word that "
            "takes it over 79 chars in length"
        )
        expected_text = (
            "This is a short line\n"
            "   This is a long line with an indent which should wrap just "
            "before the word\n"
            "that takes it over 79 chars in length\n"
            "   This is a short indented line\n"
            "This is a long line which should wrap just before the word that "
            "takes it over\n"
            "79 chars in length"
        )
        self.assertMultiLineEqual(wrap_long_lines(text), expected_text)



class ParseListingTest(unittest.TestCase):

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


class LineFinderTest(unittest.TestCase):

    def test_number_of_identical_chars(self):
        self.assertEqual(
            number_of_identical_chars('1234', '5678'),
            0
        )
        self.assertEqual(
            number_of_identical_chars('1234', '1235'),
            3
        )
        self.assertEqual(
            number_of_identical_chars('1234', '1243'),
            2
        )
        self.assertEqual(
            number_of_identical_chars('12345', '123WHATEVER45'),
            5
        )





class WriteToFileTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_simple_case(self):
        listing = CodeListing(filename='foo.py', contents='abc\ndef')
        write_to_file(listing, self.tempdir)
        with open(os.path.join(self.tempdir, listing.filename)) as f:
            self.assertEqual(f.read(), listing.contents + '\n')
        self.assertTrue(listing.was_written)


    def assert_write_to_file_gives(
        self, old_contents, new_contents, expected_contents
    ):
        listing = CodeListing(filename='foo.py', contents=new_contents)
        with open(os.path.join(self.tempdir, 'foo.py'), 'w') as f:
            f.write(old_contents)

        write_to_file(listing, self.tempdir)

        with open(os.path.join(self.tempdir, listing.filename)) as f:
            actual = f.read()
            self.assertMultiLineEqual(actual, expected_contents)

    def test_strips_line_callouts(self):
        contents= 'hello\nbla #'
        self.assert_write_to_file_gives('', contents, 'hello\nbla\n')


    def test_doesnt_mess_with_multiple_newlines(self):
        contents= 'hello\n\n\nbla'
        self.assert_write_to_file_gives('', contents, 'hello\n\n\nbla\n')



    def test_existing_file_bears_no_relation_means_replaced(self):
        old = '#abc\n#def\n#ghi\n#jkl\n'
        new = '#mno\n#pqr\n#stu\n#vvv\n'
        expected = new
        self.assert_write_to_file_gives(old, new, expected)


    def test_adding_import_at_top_then_elipsis_then_modified_stuff(self):
        old = dedent("""
            import topline
            # some stuff
            class C():
                def foo():
                    return 1
            """)
        new = dedent("""
            import newtopline
            [...]

                def foo():
                    return 2
            """
        )
        expected = dedent("""
            import newtopline
            import topline
            # some stuff
            class C():
                def foo():
                    return 2
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_adding_import_at_top_then_elipsis_then_totally_new_stuff(self):
        old = dedent("""
            import topline

            # some stuff
            class C():
                pass
            """)
        new = dedent("""
            import newtopline
            [...]

            class Nu():
                pass
            """
        )
        expected = dedent("""
            import newtopline
            import topline

            # some stuff
            class C():
                pass


            class Nu():
                pass
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_elipsis_indicating_which_class_to_add_new_method_to(self):
        old = dedent("""
            import topline

            class A(object):
                def metha(self):
                    pass

            class B(object):
                def methb(self):
                    pass
            """)
        new = dedent("""
            class A(object):
                [...]

                def metha2(self):
                    pass
            """
        )
        expected = dedent("""
            import topline

            class A(object):
                def metha(self):
                    pass

                def metha2(self):
                    pass

            class B(object):
                def methb(self):
                    pass
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_adding_import_at_top_sorts_alphabetically_respecting_django_and_locals(self):
        old = dedent("""
            import atopline

            from django import monkeys
            from django import chickens

            from lists.views import thing

            # some stuff
            class C():
                def foo():
                    return 1
            """)
        new = dedent("""
            import btopline
            [...]

                def foo():
                    return 2
            """
        )
        expected = dedent("""
            import atopline
            import btopline

            from django import chickens
            from django import monkeys

            from lists.views import thing

            # some stuff
            class C():
                def foo():
                    return 2
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


        new = dedent("""
            from django import dickens
            [...]

                def foo():
                    return 2
            """
        )
        expected = dedent("""
            import atopline

            from django import chickens
            from django import dickens
            from django import monkeys

            from lists.views import thing

            # some stuff
            class C():
                def foo():
                    return 2
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


        new = dedent("""
            from lists.zoos import thing
            [...]

                def foo():
                    return 2
            """
        )
        expected = dedent("""
            import atopline

            from django import chickens
            from django import monkeys

            from lists.views import thing
            from lists.zoos import thing

            # some stuff
            class C():
                def foo():
                    return 2
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_new_contents_then_indented_elipsis_then_appendix(self):
        old = '#abc\n#def\n#ghi\n#jkl\n'
        new = (
            '#abc\n'
            'def foo(v):\n'
            '    return v + 1\n'
            '    #def\n'
            '    [... old stuff as before]\n'
            '# then add this'
        )
        expected = (
            '#abc\n'
            'def foo(v):\n'
            '    return v + 1\n'
            '    #def\n'
            '    #ghi\n'
            '    #jkl\n'
            '# then add this\n'
        )
        self.assert_write_to_file_gives(old, new, expected)


    def test_for_existing_file_replaces_matching_lines(self):
        old = dedent("""
            class Foo(object):
                def method_1(self):
                    return 1

                def method_2(self):
                    # two
                    return 2
            """
        ).lstrip()
        new = dedent("""
                def method_2(self):
                    # two
                    return 'two'
                """
        ).strip()
        expected = dedent("""
            class Foo(object):
                def method_1(self):
                    return 1

                def method_2(self):
                    # two
                    return 'two'
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_for_existing_file_doesnt_swallow_whitespace(self):
        old = dedent("""
            one = (
                1,
            )

            two = (
                2,
            )

            three = (
                3,
            )
            """).lstrip()
        new = dedent("""
            two = (
                2,
                #two
            )
            """
        ).strip()


        expected = dedent("""
            one = (
                1,
            )

            two = (
                2,
                #two
            )

            three = (
                3,
            )
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_longer_new_file_starts_replacing_from_first_different_line(self):
        old = dedent("""
            # line 1
            # line 2
            # line 3

            """
        ).lstrip()
        new = dedent("""
            # line 1
            # line 2

            # line 3

            # line 4
            """
        ).strip()
        expected = dedent("""
            # line 1
            # line 2

            # line 3

            # line 4
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_changing_the_end_of_a_method(self):
        old = dedent("""
            class A(object):
                def method1(self):
                    # do step 1
                    # do step 2
                    # do step 3
                    # do step 4
                    # do step 5
                    pass

                def method2(self):
                    # do stuff
                    pass
            """
        ).lstrip()
        new = dedent("""
            def method1(self):
                # do step 1
                # do step 2
                # do step A
                # do step B
            """
        ).strip()
        expected = dedent("""
            class A(object):
                def method1(self):
                    # do step 1
                    # do step 2
                    # do step A
                    # do step B

                def method2(self):
                    # do stuff
                    pass
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_for_existing_file_inserting_new_lines_between_comments(self):
        old = dedent("""
            # test 1
            a = foo()
            assert  a == 1

            if a:
                # test 2
                self.fail('finish me')

                # test 3

                # the end
            # is here
            """).lstrip()
        new = dedent("""
            # test 2
            b = bar()
            assert b == 2

            # test 3
            assert True
            self.fail('finish me')

            # the end
            [...]
            """
        ).lstrip()

        expected = dedent("""
            # test 1
            a = foo()
            assert  a == 1

            if a:
                # test 2
                b = bar()
                assert b == 2

                # test 3
                assert True
                self.fail('finish me')

                # the end
            # is here
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_single_line_replacement(self):
        old = dedent("""
            def wiggle():
                abc def
                abcd fghi
                jkl mno
            """
        ).lstrip()

        new = dedent("""
            abcd abcd
            """
        ).strip()

        expected = dedent("""
            def wiggle():
                abc def
                abcd abcd
                jkl mno
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_single_line_replacement_finds_most_probable_line(self):
        old = dedent("""
            abc
            abc daf ghi
            abc dex xyz
            jkl mno
            """
        ).lstrip()

        new = dedent("""
            abc deFFF ghi
            """
        ).strip()

        expected = dedent("""
            abc
            abc deFFF ghi
            abc dex xyz
            jkl mno
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_single_line_assertion_replacement(self):
        old = dedent("""
            class Wibble(unittest.TestCase):

                def test_number_1(self):
                    self.assertEqual(1 + 1, 2)
            """
        ).lstrip()

        new = dedent("""
                self.assertEqual(1 + 1, 3)
                """
        ).strip()

        expected = dedent("""
            class Wibble(unittest.TestCase):

                def test_number_1(self):
                    self.assertEqual(1 + 1, 3)
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_single_line_assertion_replacement_finds_right_one(self):
        old = dedent("""
            class Wibble(unittest.TestCase):

                def test_number_1(self):
                    self.assertEqual(1 + 1, 2)

                def test_number_2(self):
                    self.assertEqual(1 + 2, 3)
            """
        ).lstrip()

        new = dedent("""
                self.assertEqual(1 + 2, 4)
                """
        ).strip()

        expected = dedent("""
            class Wibble(unittest.TestCase):

                def test_number_1(self):
                    self.assertEqual(1 + 1, 2)

                def test_number_2(self):
                    self.assertEqual(1 + 2, 4)
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_changing_function_signature_and_stripping_comment(self):
        old = dedent(
            """
            # stuff

            def foo():
                pass
            """
        ).lstrip()

        new = dedent(
            """
            def foo(bar):
                pass
            """
        ).strip()

        expected = new + '\n'
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_two_elipsis_dedented_change(self):
        old = dedent("""
            class Wibble(object):

                def foo(self):
                    return 2

                def bar(self):
                    return 3
            """).lstrip()

        new = dedent("""
                [...]
                def foo(self):
                    return 4

                def bar(self):
                [...]
                """
        ).strip()

        expected = dedent("""
            class Wibble(object):

                def foo(self):
                    return 4

                def bar(self):
                    return 3
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_indents_in_new_dont_confuse_things(self):
        old = dedent("""
            class Wibble():
                def foo(self):
                    # comment 1
                    do something
                    # comment 2
                    do something else
                    and keep going
            """).lstrip()

        new = (
            "    # comment 2\n"
            "    time.sleep(2)\n"
            "    do something else\n"
        )

        expected = dedent("""
            class Wibble():
                def foo(self):
                    # comment 1
                    do something
                    # comment 2
                    time.sleep(2)
                    do something else
                    and keep going
            """).lstrip()
        self.assert_write_to_file_gives(old, new, expected)

    def test_double_indents_in_new_dont_confuse_things(self):
        old = dedent("""
            class Wibble():
                def foo(self):
                    if something:
                        do something
                # end of class
            """).lstrip()

        new = dedent(
            """
                if something:
                    do something else
            # end of class
            """)

        expected = dedent("""
            class Wibble():
                def foo(self):
                    if something:
                        do something else
                # end of class
            """).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_special_case_assertIn_row_for_rows_chap_5(self):
        old = dedent("""
            class Case(object):
                def foo():
                    bla
                    self.assertTrue(
                        any(row.text == '1: Buy peacock feathers' for row in rows),
                        "New to-do item did not appear in table -- its text was:\\n%s" % (
                            table.text,
                        )
                    )
                    stuff
            """.lstrip()
        )

        new = "self.assertIn('1: Buy peacock feathers', [row.text for row in rows])\n"

        expected = dedent("""
            class Case(object):
                def foo():
                    bla
                    self.assertIn('1: Buy peacock feathers', [row.text for row in rows])
                    stuff
            """.lstrip()
        )
        self.assert_write_to_file_gives(old, new, expected)



class RunCommandTest(ChapterTest):

    def test_running_interactive_command(self):
        self.run_command(Command('mkdir superlists'), cwd=self.tempdir)

        command = Command(
            "python -c \"print 'input please?'; a = raw_input();print 'OK' if a=='yes' else 'NO'\""
        )
        output = self.run_command(command, user_input='no')
        self.assertIn('NO', output)
        output = self.run_command(command, user_input='yes')
        self.assertIn('OK', output)



class AssertConsoleOutputCorrectTest(ChapterTest):

    def test_simple_case(self):
        actual = 'foo'
        expected = Output('foo')
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_test_run_times_and_test_dashes(self):
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


    def test_handles_elipsis(self):
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


    def test_with_start_elipsis_and_OK(self):
        actual =dedent("""
            bla

            OK

            and some epilogue
            """).strip()
        expected = Output(dedent("""
            [...]
            OK
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_with_elipsis_finds_assertionerrors(self):
        actual =dedent("""
            bla
            bla bla
                self.assertSomething(burgle)
            AssertionError: nope

            and then there's some stuff afterwards we don't care about
            """).strip()
        expected = Output(dedent("""
            [...]
                self.assertSomething(burgle)
            AssertionError: nope
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_with_start_elipsis_and_end_longline_elipsis(self):
        actual =dedent("""
            bla
            bla bla
            loads more stuff
                raise MyException('eek')
            MyException: a really long exception, which will eventually wrap into multiple lines, so much so that it gets boring after a while...

            and then there's some stuff afterwards we don't care about
            """).strip()
        expected = Output(dedent("""
            [...]
            MyException: a really long exception, which will eventually wrap into multiple
            lines, so much so that [...]
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_with_start_elipsis_and_end_longline_elipsis_with_assertionerror(self):
        actual =dedent("""
            bla
                self.assertSomething(bla)
            AssertionError: a really long exception, which will eventually wrap into multiple lines, so much so that it gets boring after a while...

            and then there's some stuff afterwards we don't care about
            """).strip()
        expected = Output(dedent("""
            [...]
            AssertionError: a really long exception, which will eventually [...]
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_for_short_expected_with_trailing_elipsis(self):
        actual =dedent("""
            bla
            bla bla
                self.assertSomething(burgle)
            AssertionError: a long assertion error which ends up wrapping so we have to have it across two lines but then it really goes on and on and on, so much so that it gets boring and we chop it off"""
            ).strip()
        expected = Output(dedent("""
            AssertionError: a long assertion error which ends up wrapping so we have to
            have it across two lines but then it really goes on and on [...]
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_elipsis_lines_still_checked(self):
        actual =dedent("""
            AssertionError: a long assertion error which ends up wrapping so we have to have it across two lines but then it changes and ends up saying something different from what was expected so we shoulf fail
            """
            ).strip()
        expected = Output(dedent("""
            AssertionError: a long assertion error which ends up wrapping so we have to
            have it across two lines but then it really goes on and on [...]
            """).strip()
        )

        with self.assertRaises(AssertionError):
            self.assert_console_output_correct(actual, expected)


    def test_with_middle_elipsis(self):
        actual =dedent("""
            bla
            bla bla
            ERROR: the first line

            some more blurg
                something else
                an indented penultimate line
            KeyError: something
            more stuff happens later
            """
            ).strip()
        expected = Output(dedent("""
            ERROR: the first line
            [...]
                an indented penultimate line
            KeyError: something
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ls(self):
        expected = Output('superlists          functional_tests.py')
        actual = 'functional_tests.py\nsuperlists\n'
        self.assert_console_output_correct(actual, expected, ls=True)
        self.assertTrue(expected.was_checked)


    def test_working_directory_substitution(self):
        expected = Output('bla bla /workspace/foo stuff')
        actual = 'bla bla %s/foo stuff' % (self.tempdir,)
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_tabs(self):
        expected = Output('#       bla bla')
        actual = '#\tbla bla'
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_diff_indexes(self):
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


    def test_ignores_git_commit_numers_in_logs(self):
        actual =dedent("""
            ea82222 Basic view now returns minimal HTML
            7159049 First unit test and url mapping, dummy view
            edba758 Add app for lists, with deliberately failing unit test
            """).strip()
        expected = Output(dedent("""
            a6e6cc9 Basic view now returns minimal HTML
            450c0f3 First unit test and url mapping, dummy view
            ea2b037 Add app for lists, with deliberately failing unit test
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)

        actual =dedent("""
            abc Basic view now returns minimal HTML
            123 First unit test and url mapping, dummy view
            """).strip()
        expected = Output(dedent("""
            bad Basic view now returns minimal HTML
            456 First unit test and url mapping, dummy view
            """).strip()
        )

        with self.assertRaises(AssertionError):
            self.assert_console_output_correct(actual, expected)


    def test_fixes_stdout_stderr_for_creating_db(self):
        actual = dedent("""
            ======================================================================
            FAIL: test_basic_addition (lists.tests.SimpleTest)
            ----------------------------------------------------------------------
            Traceback etc

            ----------------------------------------------------------------------
            Ran 1 tests in X.Xs

            FAILED (failures=1)
            Creating test database for alias 'default'...
            Destroying test database for alias 'default'
            """).strip()

        expected = Output(dedent("""
            Creating test database for alias 'default'...
            ======================================================================
            FAIL: test_basic_addition (lists.tests.SimpleTest)
            ----------------------------------------------------------------------
            Traceback etc

            ----------------------------------------------------------------------
            Ran 1 tests in X.Xs

            FAILED (failures=1)
            Destroying test database for alias 'default'
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)

    def test_handles_long_lines(self):
        actual = dedent("""
            A normal line
                An indented line, that's longer than 80 chars. it goes on for a while you see.
                a normal indented line
            """).strip()

        expected = Output(dedent("""
            A normal line
                An indented line, that's longer than 80 chars. it goes on for a while you
            see.
                a normal indented line
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_for_minimal_expected(self):
        actual = dedent(
            """
            Creating test database for alias 'default'...
            E
            ======================================================================
            ERROR: test_root_url_resolves_to_home_page_view (lists.tests.HomePageTest)
            ----------------------------------------------------------------------
            Traceback (most recent call last):
              File "/workspace/superlists/lists/tests.py", line 8, in test_root_url_resolves_to_home_page_view
                found = resolve('/')
              File "/usr/local/lib/python2.7/dist-packages/django/core/urlresolvers.py", line 440, in resolve
                return get_resolver(urlconf).resolve(path)
              File "/usr/local/lib/python2.7/dist-packages/django/core/urlresolvers.py", line 104, in get_callable
                (lookup_view, mod_name))
            ViewDoesNotExist: Could not import superlists.views.home. Parent module superlists.views does not exist.
            ----------------------------------------------------------------------
            Ran 1 tests in X.Xs

            FAILED (errors=1)
            Destroying test database for alias 'default'...
            """).strip()

        expected = Output(dedent(
            """
            ViewDoesNotExist: Could not import superlists.views.home. Parent module
            superlists.views does not exist.
            """).strip()
        )
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_for_long_traceback(self):
        with open(os.path.join(os.path.dirname(__file__), "actual_manage_py_test.output")) as f:
            actual = f.read().strip()
        expected = Output(dedent("""
[... lots and lots of traceback]

Traceback (most recent call last):
  File "/usr/local/lib/python2.7/dist-packages/django/test/testcases.py", line
259, in __call__
    self._pre_setup()
  File "/usr/local/lib/python2.7/dist-packages/django/test/testcases.py", line
479, in _pre_setup
    self._fixture_setup()
  File "/usr/local/lib/python2.7/dist-packages/django/test/testcases.py", line
829, in _fixture_setup
    if not connections_support_transactions():
  File "/usr/local/lib/python2.7/dist-packages/django/test/testcases.py", line
816, in connections_support_transactions
    for conn in connections.all())
  File "/usr/local/lib/python2.7/dist-packages/django/test/testcases.py", line
816, in <genexpr>
    for conn in connections.all())
  File "/usr/local/lib/python2.7/dist-packages/django/utils/functional.py",
line 43, in __get__
    res = instance.__dict__[self.func.__name__] = self.func(instance)
  File "/usr/local/lib/python2.7/dist-packages/django/db/backends/__init__.py",
line 442, in supports_transactions
    self.connection.enter_transaction_management()
  File
"/usr/local/lib/python2.7/dist-packages/django/db/backends/dummy/base.py", line
15, in complain
    raise ImproperlyConfigured("settings.DATABASES is improperly configured. "
ImproperlyConfigured: settings.DATABASES is improperly configured. Please
supply the ENGINE value. Check settings documentation for more details.

 ---------------------------------------------------------------------
Ran 85 tests in 0.788s

FAILED (errors=404, skipped=1)
AttributeError: _original_allowed_hosts
""").strip()
        )
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)

if __name__ == '__main__':
    unittest.main()
