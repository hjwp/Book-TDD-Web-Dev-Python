import os
import signal
import shutil
import subprocess
import tempfile


class Commit(object):
    def __init__(self, commit_info):
        self.info = commit_info
        self.all_lines = self.info.split('\n')

        self.lines_to_add = [
            l[1:] for l in self.all_lines
            if l.startswith('+')
            and l[1:].strip()
            and not l[1] == '+'
        ]
        self.lines_to_remove = [
            l[1:] for l in self.all_lines
            if l.startswith('-')
            and l[1:].strip()
            and not l[1] == '-'
        ]
        self.moved_lines = [
            l for l in self.lines_to_add if l in self.lines_to_remove
        ]
        self.deleted_lines = [
            l for l in self.lines_to_remove if l not in self.lines_to_add
        ]
        self.new_lines = [
            l for l in self.lines_to_add if l not in self.lines_to_remove
        ]
        for pos, l in enumerate(self.all_lines):
            if l.strip().startswith('diff --git a/'):
                self.first_non_metadata_line_pos = pos
        self.other_lines = [
            l for l in self.all_lines[self.first_non_metadata_line_pos:]
            if l.strip()
            and l[1:].strip()
            and not l[1:] in self.lines_to_remove
            and not l[1:] in self.lines_to_add
            #todo missing +++ lines
        ]



class ApplyCommitException(Exception):
    pass


class SourceTree(object):

    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.processes = []
        self.dev_server_running = False


    def get_contents(self, path):
        with open(os.path.join(self.tempdir, 'superlists', path)) as f:
            return f.read()


    def cleanup(self):
        for process in self.processes:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                pass
        #shutil.rmtree(self.tempdir)


    def run_command(self, command, cwd=None, user_input=None, ignore_errors=False):
        if cwd is None:
            cwd = os.path.join(self.tempdir, 'superlists')

        if command == 'wget -O bootstrap.zip https://codeload.github.com/twbs/bootstrap/zip/v2.3.2':
            #$ *wget -O bootstrap.zip https://github.com/twbs/bootstrap/archive/v3.0.0.zip*
            shutil.copy(
                os.path.join(os.path.dirname(__file__), '../downloads/bootstrap-2-rezipped.zip'),
                os.path.join(cwd, 'bootstrap.zip')
            )
            #TODO: fix this for new bootrstrap
            return
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
            # can't read output, stdout.read just hangs.
            return

        if user_input and not user_input.endswith('\n'):
            user_input += '\n'
        output, _ = process.communicate(user_input)
        if process.returncode and not ignore_errors:
            if 'test' in command:
                return output
            if 'diff' in command:
                return output
            print('process %s return a non-zero code (%s)' % (command, process.returncode))
            print('output:\n', output)
            raise Exception('process %s return a non-zero code (%s)' % (command, process.returncode))
        return output


    def get_local_repo_path(self, chapter_no):
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../source/chapter_{0:02d}/superlists'.format(chapter_no)
        ))


    def start_with_checkout(self, chapter):
        self.run_command('mkdir superlists', cwd=self.tempdir)
        self.run_command('git init .')
        self.run_command('git remote add repo "%s"' % (self.get_local_repo_path(chapter),))
        self.run_command('git fetch repo')
        self.run_command('git checkout chapter_{0:02d}'.format(chapter - 1))
        self.chapter = chapter


    def get_commit_spec(self, commit_ref):
        return 'repo/chapter_{0:02d}^{{/--{1}--}}'.format(self.chapter, commit_ref)


    def get_files_from_commit_spec(self, commit_spec):
        return self.run_command(
            'git diff-tree --no-commit-id --name-only -r %s' % (commit_spec,)
        ).split()


    def show_future_version(self, commit_spec, path):
        return self.run_command('git show %s:%s' % (commit_spec, path),)


    def checkout_file_from_commit_ref(self, commit_ref, path=None):
        commit_spec = self.get_commit_spec(commit_ref)
        if path == None:
            paths = self.get_files_from_commit_spec(commit_spec)
        else:
            paths = [path]
        for path in paths:
            self.run_command('git checkout %s -- %s' % (commit_spec, path))
        self.run_command('git reset')


    def apply_listing_from_commit(self, listing):
        commit_spec = self.get_commit_spec(listing.commit_ref)
        commit_info = self.run_command('git show %s' % (commit_spec,))
        print('Applying listing from commit.\nListing:\n{0}\nCommit:\n:{1}'.format(
            listing.contents, commit_info
        ))

        commit = Commit(commit_info)

        files = self.get_files_from_commit_spec(commit_spec)
        if files != [listing.filename]:
            raise ApplyCommitException(
                'wrong files in commit: {0} should have been {1}'.format(
                    files, listing.filename
            ))

        listing_lines = listing.contents.split('\n')
        listing_lines = [l.rstrip(' #') for l in listing_lines]

        stripped_listing_lines = [l.strip() for l in listing_lines]
        for new_line in commit.new_lines:
            if new_line.strip() not in stripped_listing_lines:
                raise ApplyCommitException(
                    'could not find commit new line {0} in listing:\n{1}'.format(
                        new_line, listing.contents
                    )
                )
        future_contents = self.show_future_version(commit_spec, listing.filename)
        stripped_future_contents = [l.strip() for l in future_contents.split('\n')]

        line_pos_in_commit = 0
        for line in listing_lines:
            if not line or line.strip().startswith('[...'):
                continue
            if line in commit.lines_to_add:
                try:
                    line_pos_in_commit = commit.lines_to_add[line_pos_in_commit:].index(line)
                except ValueError:
                    raise ApplyCommitException(
                        'listing line {0} was in wrong order'.format(line)
                    )
                continue
            if line.strip() in stripped_future_contents:
                continue
            if line in commit.all_lines: # probably a diff listing
                continue
            if line.strip() in [l.strip() for l in commit.deleted_lines]:
                raise ApplyCommitException(
                    'listing line {0} was to be deleted'.format(line)
                )
            raise ApplyCommitException('listing line not found:\n%s' % (line,))

        self.checkout_file_from_commit_ref(listing.commit_ref, listing.filename)
        listing.was_written = True
        print('applied commit')

