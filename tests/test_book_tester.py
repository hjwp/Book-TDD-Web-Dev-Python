#!/usr/bin/env python3
import os
from textwrap import dedent
import unittest

from book_tester import (
    ChapterTest,
    fix_dict_repr_order,
    wrap_long_lines,
)
from book_parser import (
    Command,
    Output,
)
from test_write_to_file import *
from test_book_parser import *



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



class RunCommandTest(ChapterTest):

    def test_running_interactive_command(self):
        self.run_command(Command('mkdir superlists'), cwd=self.tempdir)

        command = Command(
            "python3 -c \"print 'input please?'; a = raw_input();print 'OK' if a=='yes' else 'NO'\""
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
            MyException: a really long exception, which will eventually wrap into multiple lines, so much so that it just gets boring after a while and we just stop caring...

            and then there's some stuff afterwards we don't care about
            """).strip()
        expected = Output(dedent("""
            [...]
            MyException: a really long exception, which will eventually wrap into multiple
            lines, so much so that it just gets boring after a while and [...]
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


    def test_handles_dict_key_ordering_randomness(self):
        expected = Output(
            dedent("""
            line 334, in resolve
                raise Resolver404({'path': new_path, 'tried': tried})
            django.core.urlresolvers.Resolver404: {'path': '', 'tried': []}
            """).lstrip()
        )
        actual = dedent(
            """
            line 440, in resolve
                return get_resolver(urlconf).resolve(path)
              File "/usr/local/lib/python3.3/dist-packages/django/core/urlresolvers.py",
            line 334, in resolve
                raise Resolver404({'tried': tried, 'path': new_path})
            django.core.urlresolvers.Resolver404: {'path': '', 'tried': []}
            """
        )
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


class FixDictReprOrderingTest(unittest.TestCase):

    def test_fixing_dict_ordering(self):
        self.assertEqual(
            fix_dict_repr_order(
                "django.core.urlresolvers.Resolver404: {'tried': [], 'path': ''}"
            ),
            "django.core.urlresolvers.Resolver404: {'path': '', 'tried': []}"
        )


    def test_fixing_dict_ordering_doesnt_barf_if_no_dict(self):
        self.assertEqual(
            fix_dict_repr_order(
                "foo"
            ),
            "foo"
        )

    def test_fixing_dict_ordering_for_more_that_one(self):
        self.assertEqual(
            fix_dict_repr_order(
                "bla {'b': 1, 'a': 2}\n"
                "wiz {'d': 9, 'c': 3}\n"
            ),
            "bla {'a': 2, 'b': 1}\n"
            "wiz {'c': 3, 'd': 9}\n"
    )



if __name__ == '__main__':
    unittest.main()
