import unittest
import subprocess
import tempfile
from textwrap import dedent
import os

from book_parser import CodeListing, Command
from sourcetree import SourceTree


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

    def test_from_real_git_stuff(self):
        sourcetree = SourceTree()
        sourcetree.get_local_repo_path = lambda c: os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'testrepo'
        ))
        sourcetree.start_with_checkout(21)
        sourcetree.run_command('git checkout repo/chapter_20^')
        sourcetree.run_command('git reset')

        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            file 1 line 1
            file 1 line 2 amended
            file 1 line 3
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        sourcetree.apply_listing_from_commit(listing)

        with open(sourcetree.tempdir + '/superlists/file1.txt') as f:
            assert f.read() == dedent(
                """
                file 1 line 1
                file 1 line 2 amended
                file 1 line 3
                """).lstrip()



class RunCommand2Test(unittest.TestCase):

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
        sourcetree.run_command(Command('mkdir superlists'), cwd=sourcetree.tempdir)

        command = "python3 -c \"print('input please?'); a = input();print('OK' if a=='yes' else 'NO')\""
        output = sourcetree.run_command(command, user_input='no')
        assert 'NO' in output
        output = sourcetree.run_command(command, user_input='yes')
        assert 'OK' in output


