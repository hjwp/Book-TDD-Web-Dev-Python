import os
import signal
import shutil
import subprocess
import tempfile

class ApplyCommitException(Exception):
    pass


class SourceTree(object):

    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.processes = []
        self.dev_server_running = False


    def cleanup(self):
        for process in self.processes:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                pass
        shutil.rmtree(self.tempdir)


    def run_command(self, command, cwd=None, user_input=None, ignore_errors=False):
        if cwd is None:
            cwd = os.path.join(self.tempdir, 'superlists')
        process = subprocess.Popen(
            command, shell=True, cwd=cwd, executable='/bin/bash',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            preexec_fn=os.setsid,
            universal_newlines=True,
        )
        process._command = command
        self.processes.append(process)
        if 'runserver' in command:
            return #test this another day
        if user_input and not user_input.endswith('\n'):
            user_input += '\n'
        #import time
        #time.sleep(1)
        output, _ = process.communicate(user_input)
        if process.returncode and 'test' not in command and not ignore_errors:
            print('process %s return a non-zero code (%s)' % (command, process.returncode))
            print('output:\n', output)
            raise Exception('process %s return a non-zero code (%s)' % (command, process.returncode))
        return output


    def get_local_repo_path(self, chapter_no):
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../source/chapter_%d/superlists' % (chapter_no,)
        ))


    def start_with_checkout(self, chapter):
        self.run_command('mkdir superlists', cwd=self.tempdir)
        self.run_command('git init .')
        self.run_command('git remote add repo %s' % (self.get_local_repo_path(chapter),))
        self.run_command('git fetch repo')
        self.run_command('git checkout chapter_%s' % (chapter - 1,))
        self.chapter = chapter


    def apply_listing_from_commit(self, listing):
        commit_spec = 'repo/chapter_%s^{/--%s--}' % (
                self.chapter -1, listing.commit_ref,
        )

        files = self.run_command(
            'git diff-tree --no-commit-id --name-only -r %s' % (commit_spec,)
        ).split()
        if files != [listing.filename]:
            raise ApplyCommitException('wrong files in commit: %s' % (files,))

        commit_info = self.run_command(
            'git show %s' % (commit_spec,)
        )
        new_lines = [
            l[1:] for l in commit_info.split('\n')
            if l.startswith('+')
            and not l[1] == '+'
            and l[1:].strip()
        ]
        for new_line in new_lines:
            if new_line not in listing.contents.split('\n'):
                raise ApplyCommitException(
                    'could not find line %s in listing %s' % (new_line, listing.contents)
                )
        new_lines_in_listing_order = sorted(new_lines, key=listing.contents.index)
        if new_lines_in_listing_order != new_lines:
            print('listing:\n', listing.contents)
            print('commit:\n', commit_info)
            raise ApplyCommitException('listing lines in wrong order')

        for line in listing.contents.split('\n'):
            if line in new_lines:
                continue
            if not line:
                continue
            if line in commit_info:
                continue
            if line.strip().startswith('[...'):
                continue

            print('commit info')
            print(commit_info)
            raise ApplyCommitException('listing line not found:\n%s' % (line,))


        self.run_command(
            'git checkout %s -- %s' % (commit_spec, listing.filename),

        )


