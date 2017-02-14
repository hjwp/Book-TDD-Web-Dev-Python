#!/usr/bin/env python3
import os
import unittest
from unittest.mock import Mock
from textwrap import dedent

from book_tester import (
    ChapterTest,
    PHANTOMJS_RUNNER,
    contains,
    wrap_long_lines,

)
from book_parser import (
    Command,
    Output,
)
from test_write_to_file import *  # noqa
from test_book_parser import *  # noqa
from test_source_updater import *  # noqa
from test_sourcetree import *  # noqa



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
        text = "A  really  long  line  that  uses  multiple  spaces  to  go  over  80  chars  by  a  country  mile"
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

    def test_calls_sourcetree_run_command_and_marks_as_run(self):
        self.sourcetree.run_command = Mock()
        cmd = Command('foo')
        output = self.run_command(cmd, cwd='bar', user_input='thing')
        assert output == self.sourcetree.run_command.return_value
        self.sourcetree.run_command.assert_called_with(
            'foo', cwd='bar', user_input='thing', ignore_errors=False,
        )
        assert cmd.was_run


    def test_raises_if_not_command(self):
        with self.assertRaises(AssertionError):
            self.run_command('foo')



class RunServerCommandTest(ChapterTest):

    @patch('book_tester.subprocess')
    def test_uses_python2_run_server_command(self, mock_subprocess):
        mock_subprocess.check_output.return_value = b'some bytes'
        result = self.run_server_command('foo bar')
        assert result == 'some bytes'
        mock_subprocess.check_output.assert_called_with(
            ['python2.7', self.RUN_SERVER_PATH, 'foo bar'],
        )


    @patch('book_tester.subprocess')
    def test_hacks_in_dash_y_for_apt_gets(self, mock_subprocess):
        mock_subprocess.check_output.return_value = b'some bytes'
        result = self.run_server_command('sudo apt-get install something')
        assert result == 'some bytes'
        self.RUN_SERVER_PATH = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'run_server_command.py')
        )
        mock_subprocess.check_output.assert_called_with(
            ['python2.7', self.RUN_SERVER_PATH, 'sudo apt-get install -y something'],
        )


    @patch('book_tester.subprocess')
    def test_hacks_in_SITENAME_if_needed(self, mock_subprocess):
        mock_subprocess.check_output.return_value = b'some bytes'
        result = self.run_server_command('mkdir /foo/$SITENAME')
        assert result == 'some bytes'
        self.RUN_SERVER_PATH = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'run_server_command.py')
        )
        mock_subprocess.check_output.assert_called_with(
            ['python2.7', self.RUN_SERVER_PATH, 'SITENAME=superlists-staging.ottg.eu; mkdir /foo/$SITENAME'],
        )
        # but not for the export itself
        self.run_server_command('export SITENAME=foo')
        mock_subprocess.check_output.assert_called_with(
            ['python2.7', self.RUN_SERVER_PATH, 'export SITENAME=foo'],
        )


    @patch('book_tester.subprocess')
    def test_hacks_in_cd_if_one_set_by_last_command(self, mock_subprocess):
        mock_subprocess.check_output.return_value = b'some bytes'
        assert self.current_server_cd is None
        self.run_server_command('cd /foo')
        assert self.current_server_cd == '/foo'
        self.run_server_command('do something')
        mock_subprocess.check_output.assert_called_with(
            ['python2.7', self.RUN_SERVER_PATH, 'cd /foo && do something'],
        )


    @patch('book_tester.subprocess')
    def test_hacks_in_cd_correctly_when_theres_also_a_SITENAME(self, mock_subprocess):
        mock_subprocess.check_output.return_value = b'some bytes'
        assert self.current_server_cd is None
        self.run_server_command('cd /foo/$SITENAME')
        self.run_server_command('do something')
        mock_subprocess.check_output.assert_called_with(
            ['python2.7', self.RUN_SERVER_PATH, 'SITENAME=superlists-staging.ottg.eu; cd /foo/$SITENAME && do something'],
        )


    @patch('book_tester.subprocess')
    def test_hacks_in_dtach_for_runserver(self, mock_subprocess):
        mock_subprocess.check_output.return_value = b'some bytes'
        self.run_server_command('cd /foo/$SITENAME')
        self.run_server_command('source ../virtualenv/bin/activate && python3 manage.py runserver')
        mock_subprocess.check_output.assert_called_with(
            [
                'python2.7',
                self.RUN_SERVER_PATH,
                'SITENAME=superlists-staging.ottg.eu;'
                ' cd /foo/$SITENAME && source ../virtualenv/bin/activate'
                ' && dtach -n /tmp/dtach.sock python3 manage.py runserver'
            ],
        )



class AssertConsoleOutputCorrectTest(ChapterTest):

    def test_simple_case(self):
        actual = 'foo'
        expected = Output('foo')
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_test_run_times_and_test_dashes(self):
        actual = dedent("""
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
        actual = dedent("""
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


    def test_handles_elipsis_at_end_of_line_where_theres_actually_a_linebreak(self):
        actual = dedent("""
            bla bla bla
            loads more stuff
            """).strip()
        expected = Output(dedent("""
            bla bla bla [...]
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_with_start_elipsis_and_OK(self):
        actual = dedent("""
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
        actual = dedent("""
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
        actual = dedent("""
            bla
            bla bla
            loads more stuff
                raise MyException('eek')
            MyException: a really long exception, which will eventually wrap into multiple lines, so much so that it just gets boring after a while and we just stop caring...

            and then there's some stuff afterwards we don't care about
            """).strip()  # noqa
        expected = Output(dedent("""
            [...]
            MyException: a really long exception, which will eventually wrap into multiple
            lines, so much so that it just gets boring after a while and [...]
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_with_start_elipsis_and_end_longline_elipsis_with_assertionerror(self):
        actual = dedent("""
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
        actual = dedent(
            """
            bla
            bla bla
                self.assertSomething(burgle)
            AssertionError: a long assertion error which ends up wrapping so we have to have it across two lines but then it really goes on and on and on, so much so that it gets boring and we chop it off
            """  # noqa
        ).strip()
        expected = Output(dedent("""
            AssertionError: a long assertion error which ends up wrapping so we have to
            have it across two lines but then it really goes on and on [...]
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_elipsis_lines_still_checked(self):
        actual = dedent(
            """
            AssertionError: a long assertion error which ends up wrapping so we have to have it across two lines but then it changes and ends up saying something different from what was expected so we shoulf fail
            """  # noqa
        ).strip()
        expected = Output(dedent("""
            AssertionError: a long assertion error which ends up wrapping so we have to
            have it across two lines but then it really goes on and on [...]
            """).strip()
        )

        with self.assertRaises(AssertionError):
            self.assert_console_output_correct(actual, expected)


    def test_with_middle_elipsis(self):
        actual = dedent(
            """
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
        expected = Output('bla bla /.../foo stuff')
        actual = 'bla bla %s/foo stuff' % (self.tempdir,)
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_tabs(self):
        expected = Output('#       bla bla')
        actual = '#\tbla bla'
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_diff_indexes(self):
        actual = dedent("""
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


    def test_ignores_callouts(self):
        actual = dedent("""
            bla bla
            stuff
            """).strip()
        expected = Output(dedent("""
            bla bla  <12>
            stuff
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_asciidoctor_callouts(self):
        actual = dedent("""
            bla bla
            stuff
            """).strip()
        expected = Output(dedent("""
            bla bla  (12)
            stuff
            """).strip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_git_commit_numers_in_logs(self):
        actual = dedent("""
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

        actual = dedent("""
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


    def test_ignores_mock_ids(self):
        actual = dedent("""
                self.assertEqual(user, mock_user)
            AssertionError: None != <Mock name='mock()' id='46962183546064'>
            """).rstrip()
        expected = Output(dedent("""
                self.assertEqual(user, mock_user)
            AssertionError: None != <Mock name='mock()' id='139758452629392'>
            """).rstrip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)

    def test_ignores_mock_ids_when_they_dont_have_names(self):
        actual = dedent("""
                self.assertEqual(user, mock_user)
            AssertionError: None != <Mock id='46962183546064'>
            """).rstrip()
        expected = Output(dedent("""
                self.assertEqual(user, mock_user)
            AssertionError: None != <Mock id='139758452629392'>
            """).rstrip()
        )

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_phantomjs_run_times(self):
        actual = "Took 24ms to run 2 tests. 2 passed, 0 failed."
        expected = Output("Took 15ms to run 2 tests. 2 passed, 0 failed.")
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_bdd_run_times(self):
        actual = "features/steps/my_lists.py:19 0.187s"
        expected = Output("features/steps/my_lists.py:19 0.261s")
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_object_ids(self):
        actual = "<AnonymousUser object at 0x2b3629047150>"
        expected = Output("<AnonymousUser object at 0x7f364795ef90>")
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_migration_timestamps(self):
        actual = "  0005_auto_20140414_2038.py:"
        expected = Output("  0005_auto_20140414_2108.py:")
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_session_ids(self):
        actual = "qnslckvp2aga7tm6xuivyb0ob1akzzwl"
        expected = Output("jvhzc8kj2mkh06xooqq9iciptead20qq")
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_ignores_3_5_x_AssertionError_None_thing(self):
        actual = "AssertionError"
        expected = Output("AssertionError: None")
        self.assert_console_output_correct(actual, expected)
        actual2 = "AssertionError: something"
        with self.assertRaises(AssertionError):
            self.assert_console_output_correct(actual2, expected)



    def test_ignores_localhost_server_port(self):
        actual = "//localhost:2021/my-url is a thing"
        expected = Output("//localhost:3339/my-url is a thing")
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_only_ignores_exactly_32_char_strings_no_whitespace(self):
        actual = "qnslckvp2aga7tm6xuivyb0ob1akzzwl"
        expected = Output("jvhzc8kj2mkh06xooqq9iciptead20qq")
        with self.assertRaises(AssertionError):
            self.assert_console_output_correct(actual[:-1], expected[:-1])
            self.assert_console_output_correct(actual + '1', expected + 'a')
            self.assert_console_output_correct(' ' + actual, ' ' + expected)


    def test_ignores_screenshot_times(self):
        actual = (
            'screenshotting to /.../superlists/functional_tests/screendumps/MyListsTes\n'
            't.test_logged_in_users_lists_are_saved_as_my_lists-window0-2014-03-09T11.39.38.\n'
            'png\n'
            'dumping page HTML to /.../superlists/functional_tests/screendumps/MyLists\n'
            'Test.test_logged_in_users_lists_are_saved_as_my_lists-window0-2014-03-09T11.39.\n'
            '38.html\n'
        )
        expected = Output(
            'screenshotting to /.../superlists/functional_tests/screendumps/MyListsTes\n'
            't.test_logged_in_users_lists_are_saved_as_my_lists-window0-2013-04-09T13.40.39.\n'
            'png\n'
            'dumping page HTML to /.../superlists/functional_tests/screendumps/MyLists\n'
            'Test.test_logged_in_users_lists_are_saved_as_my_lists-window0-2014-04-04T12.43.\n'
            '42.html\n'
        )
        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)


    def test_matches_system_vs_virtualenv_install_paths(self):
        actual = dedent(
            """
              File "/home/harry/.virtualenvs/Book/lib/python3.4/site-packages/django/core/urlresolvers.py", line 521, in resolve
                return get_resolver(urlconf).resolve(path)
            """
        ).rstrip()
        expected = Output(dedent(
            """
              File "...-packages/django/core/urlresolvers.py", line 521, in resolve
                return get_resolver(urlconf).resolve(path)
            """
        ).rstrip())

        self.assert_console_output_correct(actual, expected)
        self.assertTrue(expected.was_checked)

        incorrect_actual = dedent(
            """
              File "/home/harry/.virtualenvs/Book/lib/python3.4/site-packages/django/core/urlresolvers.py", line 522, in resolve
                return get_resolver(urlconf).resolve(path)
            """
        ).rstrip()
        with self.assertRaises(AssertionError):
            self.assert_console_output_correct(incorrect_actual, expected)
        incorrect_actual = dedent(
            """
              File "/home/harry/.virtualenvs/Book/lib/python3.4/site-packages/django/core/another_file.py", line 521, in resolve
                return get_resolver(urlconf).resolve(path)
            """
        ).rstrip()
        with self.assertRaises(AssertionError):
            self.assert_console_output_correct(incorrect_actual, expected)




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
              File "/.../superlists/lists/tests.py", line 8, in test_root_url_resolves_to_home_page_view
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
              File "[...]-packages/django/test/testcases.py", line 259, in __call__
                self._pre_setup()
              File "[...]-packages/django/test/testcases.py", line 479, in _pre_setup
                self._fixture_setup()
              File "[...]-packages/django/test/testcases.py", line 829, in _fixture_setup
                if not connections_support_transactions():
              File "[...]-packages/django/test/testcases.py", line 816, in
            connections_support_transactions
                for conn in connections.all())
              File "[...]-packages/django/test/testcases.py", line 816, in <genexpr>
                for conn in connections.all())
              File "[...]-packages/django/utils/functional.py", line 43, in __get__
                res = instance.__dict__[self.func.__name__] = self.func(instance)
              File "[...]-packages/django/db/backends/__init__.py", line 442, in supports_transactions
                self.connection.enter_transaction_management()
              File "[...]-packages/django/db/backends/dummy/base.py", line 15, in complain
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



class CurrentContentsTest(ChapterTest):

    def test_ok_for_correct_current_contents(self):
        actual_contents = dedent(
            """
            line 0
            line 1
            line 2
            line 3
            line 4
            """
        )
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            line 1
            line 2
            line 3
            """).lstrip()
        )
        self.check_current_contents(listing, actual_contents)  # should not raise


    def test_raises_for_any_line_not_in_actual_contents(self):
        actual_contents = dedent(
            """
            line 0
            line 1
            line 2
            line 3
            line 4
            """
        )
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            line 3
            line 4
            line 5
            """).lstrip()
        )
        with self.assertRaises(AssertionError):
            self.check_current_contents(listing, actual_contents)


    def test_indentation_is_ignored(self):
        actual_contents = dedent(
            """
            line 0
                line 1
            line 2
            line 3
            """
        )
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            line 1
            line 2
            line 3
            """).lstrip()
        )
        self.check_current_contents(listing, actual_contents)


    def test_raises_if_lines_not_in_order(self):
        actual_contents = dedent(
            """
            line 1
            line 2
            line 3
            line 4
            """
        )
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            line 1
            line 3
            line 2
            """).lstrip()
        )
        listing.currentcontents = True

        with self.assertRaises(AssertionError):
            self.check_current_contents(listing, actual_contents)


    def test_checks_elipsis_blocks_separately(self):
        actual_contents = dedent(
            """
            line 1
            line 2
            line 3
            line 4
            line 5
            """
        )
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            line 1
            line 2
            [...]
            line 4
            """).lstrip()
        )
        listing.currentcontents = True
        self.check_current_contents(listing, actual_contents)  # should not raise



class TestContains:

    def test_smoketest(self):
        assert contains([1, 2, 3, 4], [1, 2])

    def testcontains_end_seq(self):
        assert contains([1, 2, 3, 4], [3, 4])

    def testcontains_middle_seq(self):
        assert contains([1, 2, 3, 4, 5], [3, 4])

    def testcontains_oversized_seq(self):
        assert contains([1, 2, 3, 4, 4], [1, 2, 3, 4])

    def testcontains_iteslf(self):
        assert contains([1, 2, 3], [1, 2, 3])




class DictOrderingTest(ChapterTest):

    def test_dict_ordering_is_stable(self):
        assert list({'a': 'b', 'c': 'd'}.keys()) == ['a', 'c']
        self.assertEqual(os.environ['PYTHONHASHSEED'], "0")



class CheckQunitOuptutTest(ChapterTest):

    def test_partial_listing_passes(self):
        self.chapter_name = 'chapter_14'
        self.sourcetree.start_with_checkout('chapter_deploying_validation', 'chapter_14')
        expected = Output("2 assertions of 2 passed, 0 failed.")
        self.check_qunit_output(expected) # should pass
        assert expected.was_checked

    def test_fails_if_lists_fail_and_no_accounts(self):
        self.chapter_name = 'chapter_14'
        self.sourcetree.start_with_checkout('chapter_deploying_validation', 'chapter_14')
        with self.assertRaises(AssertionError):
            self.check_qunit_output(Output('arg'))


    def test_runs_phantomjs_runner_against_lists_tests(self):
        self.chapter_name = 'chapter_javascript'
        self.sourcetree.start_with_checkout('chapter_deploying_validation', 'chapter_14')
        lists_tests = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '../source/chapter_javascript/superlists/lists/static/tests/tests.html'
        )

        manual_run = subprocess.check_output(['phantomjs', PHANTOMJS_RUNNER, lists_tests])
        expected = Output(manual_run.strip().decode())
        self.check_qunit_output(expected) # should pass


    def DONTtest_runs_against_accounts_if_lists_pass(self):
        self.chapter_name = 'chapter_deploying_validation'
        self.sourcetree.start_with_checkout('chapter_deploying_validation', 'chapter_14')
        lists_tests = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../source/chapter_advanced_forms/superlists/lists/static/tests/tests.html'
        ))
        accounts_tests = lists_tests.replace('/lists/', '/accounts/')

        def test_results(path):
            if path == lists_tests:
                return '0 failed'
            if path == accounts_tests:
                return '2 failed'
        self.run_js_tests = test_results
        self.assert_console_output_correct = Mock()

        self.check_qunit_output('expected')
        assert self.assert_console_output_correct.call_args_list == [
            call('0 failed', 'expected'),
            call('2 failed', 'expected'),
        ]



class CheckFinalDiffTest(ChapterTest):
    chapter_name = 'chapter_01'

    def test_empty_passes(self):
        self.run_command = lambda _: ""
        self.check_final_diff() # should pass


    def test_diff_fails(self):
        diff = dedent(
            """
            + a missing line
            - a line that was wrong
            bla
            """
        )
        self.run_command = lambda _: diff
        with self.assertRaises(AssertionError):
            self.check_final_diff()


    def test_blank_lines_ignored(self):
        diff = dedent(
            """
            +
            -
            bla
            """
        )
        self.run_command = lambda _: diff
        self.check_final_diff() # should pass


    def test_ignore_moves(self):
        diff = dedent(
            """
            + some
            + block
            stuff
            - some
            - block

            bla
            """
        )
        self.run_command = lambda _: diff
        with self.assertRaises(AssertionError):
            self.check_final_diff()
        self.check_final_diff(ignore=["moves"]) # should pass
        with self.assertRaises(AssertionError):
            diff += '\n+a genuinely different line'
            self.check_final_diff(ignore=["moves"])


    def test_ignore_secret_key_and_generated_by_django(self):
        diff = dedent(
            """
            diff --git a/superlists/settings.py b/superlists/settings.py
            index 7463a4c..6eb4bde 100644
            --- a/superlists/settings.py
            +++ b/superlists/settings.py
            @@ -17,7 +17,7 @@ BASE_DIR = os.path.dirname(os.path.dirname(__file__))
             # See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

             # SECURITY WARNING: keep the secret key used in production secret!
            -SECRET_KEY = '!x8-9w9o%s#c8u(4^zb9n2g(xy4q*@c^$9axl2o48wkz(v%_!*'
            +SECRET_KEY = 'y)exet(6z6z6)(b!v1m8it$a0q^e=b^#*r8a2o5er1u(=sl=7f'

             # SECURITY WARNING: don't run with debug turned on in production!

            -# Generated by Django 1.10.3 on 2016-12-01 21:11
            +# Generated by Django 1.10.3 on 2016-12-02 10:19
             from __future__ import unicode_literals
            """
        )
        self.run_command = lambda _: diff
        with self.assertRaises(AssertionError):
            self.check_final_diff()
        self.check_final_diff(ignore=["SECRET_KEY", "Generated by Django 1.10"]) # should pass
        with self.assertRaises(AssertionError):
            diff += '\n+a genuinely different line'
            self.check_final_diff(ignore=["SECRET_KEY", "Generated by Django 1.10"])


    def test_ignore_moves_and_custom(self):
        diff = dedent(
            """
            + some
            + block
            stuff
            - some
            - block

            bla
            + ignore me
            """
        )
        self.run_command = lambda _: diff
        with self.assertRaises(AssertionError):
            self.check_final_diff()
        self.check_final_diff(ignore=["moves", "ignore me"]) # should pass
        with self.assertRaises(AssertionError):
            diff += '\n+a genuinely different line'
            self.check_final_diff(ignore=["moves", "ignore me"])

