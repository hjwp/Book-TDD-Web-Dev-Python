import unittest
import subprocess
import tempfile
from textwrap import dedent
import os

from book_parser import CodeListing, Command
from sourcetree import SourceTree


class ApplyGitRefTest(unittest.TestCase):

    def DONTtest_from_real_git_stuff(self):
        repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testrepo'))
        tempdir = tempfile.mkdtemp()
        subprocess.check_output('git init .', shell=True, cwd=tempdir)
        subprocess.check_output('git remote add repo %s' % (repo_path,), shell=True, cwd=tempdir)
        subprocess.check_output('git fetch repo', shell=True, cwd=tempdir)
        subprocess.check_output('git checkout repo/master^', shell=True, cwd=tempdir)
        subprocess.check_output('git reset', shell=True, cwd=tempdir)
        listing = CodeListing(filename='file1.txt', contents=dedent(
            """
            file 1 line 1
            file 1 line 2 amended
            file 1 line 3
            """).lstrip()
        )
        listing.commit_ref = 'ch17l021'

        apply_git_ref(listing, tempdir)

        with open(tempdir + '/file1.txt') as f:
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


