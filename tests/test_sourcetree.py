from mock import patch
import unittest
import subprocess
from textwrap import dedent
import os

from book_parser import CodeListing
from sourcetree import ApplyCommitException, SourceTree


class GetFileTest(unittest.TestCase):

    def test_get_contents(self):
        sourcetree = SourceTree()
        os.makedirs(sourcetree.tempdir + '/superlists')
        with open(sourcetree.tempdir + '/superlists/foo.txt', 'w') as f:
            f.write('bla bla')
        assert sourcetree.get_contents('foo.txt') == 'bla bla'


class StartWithCheckoutTest(unittest.TestCase):

    def test_get_local_repo_path(self):
        sourcetree = SourceTree()
        assert sourcetree.get_local_repo_path(12) == os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../source/chapter_12/superlists'
        ))


    def test_checks_out_repo_current_chapter(self):
        sourcetree = SourceTree()
        sourcetree.get_local_repo_path = lambda c: os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'testrepo'
        ))
        sourcetree.start_with_checkout(21)
        remotes = sourcetree.run_command('git remote').split()
        assert remotes == ['repo']
        branch = sourcetree.run_command('git branch').strip()
        assert branch == '* chapter_20'
        assert sourcetree.chapter == 21



class ApplyFromGitRefTest(unittest.TestCase):

    def setUp(self):
        self.sourcetree = SourceTree()
        self.sourcetree.get_local_repo_path = lambda c: os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'testrepo'
        ))
        self.sourcetree.start_with_checkout(17)
        self.sourcetree.run_command('git checkout test-start')
        self.sourcetree.run_command('git reset')


    def test_from_real_git_stuff(self):
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            file 1 line 2 amended
            file 1 line 3
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        self.sourcetree.apply_listing_from_commit(listing)

        with open(self.sourcetree.tempdir + '/superlists/file1.txt') as f:
            assert f.read() == dedent(
                """
                file 1 line 1
                file 1 line 2 amended
                file 1 line 3
                """).lstrip()

        assert listing.was_written


    def test_leaves_staging_empty(self):
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            file 1 line 2 amended
            file 1 line 3
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        self.sourcetree.apply_listing_from_commit(listing)

        staged = self.sourcetree.run_command('git diff --staged')
        assert staged == ''


    def test_raises_if_wrong_file(self):
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            file 1 line 1
            file 1 line 2 amended
            file 1 line 3
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)


    def test_raises_if_too_many_files_in_commit(self):
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            file 1 line 1
            file 1 line 2
            """).lstrip()
        )
        listing.commit_ref = 'ch17l023'

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)


    def test_raises_if_listing_doesnt_show_all_new_lines_in_diff(self):
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            file 1 line 3
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)


    def test_raises_if_listing_lines_in_wrong_order(self):
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            file 1 line 3
            file 1 line 2 amended
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)


    def test_line_ordering_check_isnt_confused_by_dupe_lines(self):
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            another line changed
            some duplicate lines coming up...

            hello
            goodbye
            hello
            """).lstrip()
        )
        listing.commit_ref = 'ch17l027'
        self.sourcetree.apply_listing_from_commit(listing)


    def test_raises_if_any_other_listing_lines_not_in_before_version(self):
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            what is this?
            file 1 line 2 amended
            file 1 line 3
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)


    def test_happy_with_lines_in_before_and_after_version(self):
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            file 2 line 1 changed
            [...]

            hello
            hello

            one more line at end
            """).lstrip()
        )
        listing.commit_ref = 'ch17l028'

        self.sourcetree.apply_listing_from_commit(listing)


    def test_raises_if_listing_line_not_in_after_version(self):
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            hello
            goodbye
            hello

            one more line at end
            """).lstrip()
        )
        listing.commit_ref = 'ch17l028'

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)


    def test_happy_with_lines_from_just_before_diff(self):
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            file 1 line 1
            file 1 line 2 amended
            file 1 line 3
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        self.sourcetree.apply_listing_from_commit(listing)


    def test_happy_with_elipsis(self):
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            [...]
            file 1 line 2 amended
            file 1 line 3
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        self.sourcetree.apply_listing_from_commit(listing)


    def test_happy_with_callouts(self):
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            [...]
            file 1 line 2 amended #
            file 1 line 3 #
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        self.sourcetree.apply_listing_from_commit(listing)



    def test_happy_with_blank_lines(self):
        listing = CodeListing(filename='file2.txt', contents=dedent(
            """
            file 2 line 1 changed

            another line changed
            """).lstrip()
        )
        listing.commit_ref = 'ch17l024'

        self.sourcetree.apply_listing_from_commit(listing)


    def test_handles_indents(self):
        self.sourcetree.run_command('git checkout f70efb1')
        listing = CodeListing(filename='pythonfile.py', contents=dedent(
            """
            def method1(self):
                # amend method 1
                return 2

            [...]
            """).lstrip()
        )
        listing.commit_ref = 'ch17l026'

        self.sourcetree.apply_listing_from_commit(listing)


class SourceTreeRunCommandTest(unittest.TestCase):

    def test_running_simple_command(self):
        sourcetree = SourceTree()
        sourcetree.run_command('touch foo', cwd=sourcetree.tempdir)
        assert os.path.exists(os.path.join(sourcetree.tempdir, 'foo'))


    def test_default_directory_is_superlists(self):
        sourcetree = SourceTree()
        os.makedirs(os.path.join(sourcetree.tempdir, 'superlists'))
        sourcetree.run_command('touch foo')
        assert os.path.exists(os.path.join(sourcetree.tempdir, 'superlists', 'foo'))


    def test_returns_output(self):
        sourcetree = SourceTree()
        output = sourcetree.run_command('echo hello', cwd=sourcetree.tempdir)
        assert output == 'hello\n'


    def test_raises_on_errors(self):
        sourcetree = SourceTree()
        with self.assertRaises(Exception):
            sourcetree.run_command('synt!tax error', cwd=sourcetree.tempdir)
        sourcetree.run_command('synt!tax error', cwd=sourcetree.tempdir, ignore_errors=True)


    def test_environment_variables(self):
        sourcetree = SourceTree()
        output = sourcetree.run_command('echo $PIP_DOWNLOAD_CACHE', cwd=sourcetree.tempdir)
        assert output == '/home/harry/.pip-download-cache\n'


    def test_doesnt_raise_for_some_things_where_a_return_code_is_ok(self):
        sourcetree = SourceTree()
        sourcetree.run_command('diff foo bar', cwd=sourcetree.tempdir)
        sourcetree.run_command('python test.py', cwd=sourcetree.tempdir)


    def test_cleanup_kills_backgrounded_processes_and_rmdirs(self):
        sourcetree = SourceTree()
        sourcetree.run_command('python -c"import time; time.sleep(5)" & #runserver', cwd=sourcetree.tempdir)
        assert len(sourcetree.processes) == 1
        sourcetree_pid = sourcetree.processes[0].pid
        pids = subprocess.check_output('pgrep -f time.sleep', shell=True).decode('utf8').split()
        print('sourcetree_pid', sourcetree_pid)
        print('pids', pids)
        sids = []
        for pid in reversed(pids):
            print('checking', pid)
            cmd = 'ps -o sid --no-header -p %s' % (pid,)
            print(cmd)
            try:
                sid = subprocess.check_output(cmd, shell=True)
                print('sid', sid)
                sids.append(sid)
                assert sourcetree_pid == int(sid)
            except subprocess.CalledProcessError:
                pass
        assert sids

        sourcetree.cleanup()
        assert 'time.sleep' not in subprocess.check_output('ps auxf', shell=True).decode('utf8')
        assert not os.path.exists(sourcetree.tempdir)



    def test_running_interactive_command(self):
        sourcetree = SourceTree()
        sourcetree.run_command('mkdir superlists', cwd=sourcetree.tempdir)

        command = "python3 -c \"print('input please?'); a = input();print('OK' if a=='yes' else 'NO')\""
        output = sourcetree.run_command(command, user_input='no')
        assert 'NO' in output
        output = sourcetree.run_command(command, user_input='yes')
        assert 'OK' in output


    def test_special_cases_wget_bootstrap(self):
        sourcetree = SourceTree()
        sourcetree.run_command('mkdir superlists', cwd=sourcetree.tempdir)
        with patch('sourcetree.subprocess') as mock_subprocess:
            mock_subprocess.Popen.return_value.communicate.return_value = (
                    'bla bla', None
            )
            sourcetree.run_command(
                'wget -O bootstrap.zip https://codeload.github.com/twbs/bootstrap/zip/v2.3.2'
            )
            assert not mock_subprocess.Popen.called
        assert os.path.exists(os.path.join(sourcetree.tempdir, 'superlists', 'bootstrap.zip'))
        diff = sourcetree.run_command('diff %s bootstrap.zip' % (
            os.path.join(os.path.dirname(__file__), '..', 'downloads', 'bootstrap-2-rezipped.zip'))
        )
        assert diff == ''

