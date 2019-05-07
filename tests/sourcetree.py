import getpass
import os
import io
import re
import signal
import shutil
import subprocess
import tempfile

def strip_comments(line):
    match_python = re.match(r"^(.+\S) +#$", line)
    if match_python:
        print('match python')
        return match_python.group(1)
    match_js = re.match(r"^(.+\S) +//$", line)
    if match_js:
        return match_js.group(1)
    return line


BOOTSTRAP_WGET = 'wget -O bootstrap.zip https://github.com/twbs/bootstrap/releases/download/v3.3.4/bootstrap-3.3.4-dist.zip'


class Commit(object):

    @staticmethod
    def from_diff(commit_info):
        commit = Commit()
        commit.info = commit_info
        commit.all_lines = commit.info.split('\n')

        commit.lines_to_add = [
            l[1:] for l in commit.all_lines
            if l.startswith('+') and
            l[1:].strip() and
            not l[1] == '+'
        ]
        commit.lines_to_remove = [
            l[1:] for l in commit.all_lines
            if l.startswith('-') and
            l[1:].strip() and
            not l[1] == '-'
        ]
        commit.moved_lines = [
            l for l in commit.lines_to_add if l in commit.lines_to_remove
        ]
        commit.deleted_lines = [
            l for l in commit.lines_to_remove if l not in commit.lines_to_add
        ]
        commit.new_lines = [
            l for l in commit.lines_to_add if l not in commit.lines_to_remove
        ]
        return commit



class ApplyCommitException(Exception):
    pass


class SourceTree(object):

    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.processes = []
        self.dev_server_running = False


    def get_contents(self, path):
        with open(os.path.join(self.tempdir, path)) as f:
            return f.read()


    def cleanup(self):
        for process in self.processes:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                pass
        if getpass.getuser() != 'harry':
            shutil.rmtree(self.tempdir)


    def run_command(self, command, cwd=None, user_input=None, ignore_errors=False, silent=False):
        if cwd is None:
            cwd = self.tempdir

        if command == BOOTSTRAP_WGET:
            shutil.copy(
                os.path.join(os.path.dirname(__file__), '../downloads/bootstrap.zip'),
                os.path.join(cwd, 'bootstrap.zip')
            )
            return
        actual_command = command
        if command.startswith('fab deploy'):
            actual_command = f'cd deploy_tools && {command}'
            actual_command = actual_command.replace(
                'fab deploy',
                'fab -D -i ~/Dropbox/Book/.vagrant/machines/default/virtualbox/private_key deploy'
            )
        elif command.startswith('curl'):
            actual_command = command.replace('curl', 'curl --silent --show-error')
        process = subprocess.Popen(
            actual_command, shell=True, cwd=cwd, executable='/bin/bash',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            preexec_fn=os.setsid,
            universal_newlines=True,
        )
        process._command = command
        self.processes.append(process)
        if 'runserver' in command:
            # can't read output, stdout.read just hangs.
            # TODO: readline?
            return

        if user_input and not user_input.endswith('\n'):
            user_input += '\n'
        if user_input:
            print('sending user input: {}'.format(user_input))
        output, _ = process.communicate(user_input)
        if process.returncode and not ignore_errors:
            if 'test' in command or 'diff' in command or 'migrate' in command:
                return output
            print('process %s return a non-zero code (%s)' % (command, process.returncode))
            print('output:\n', output)
            raise Exception('process %s return a non-zero code (%s)' % (command, process.returncode))
        if not silent:
            try:
                print(output)
            except io.BlockingIOError as e:
                print(e)
                pass
        return output


    def get_local_repo_path(self, chapter_name):
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../source/{}/superlists'.format(chapter_name)
        ))


    def start_with_checkout(self, chapter, previous_chapter):
        print('starting with checkout')
        self.run_command('git init .')
        self.run_command('git remote add repo "{}"'.format(
            self.get_local_repo_path(chapter)
        ))
        self.run_command('git fetch repo')
        self.run_command('git reset --hard repo/{}'.format(previous_chapter))
        print(self.run_command('git status'))
        self.chapter = chapter


    def get_commit_spec(self, commit_ref):
        return 'repo/{chapter}^{{/--{commit_ref}--}}'.format(chapter=self.chapter, commit_ref=commit_ref)


    def get_files_from_commit_spec(self, commit_spec):
        return self.run_command(
            'git diff-tree --no-commit-id --name-only --find-renames -r {}'.format(
                commit_spec
            )
        ).split()


    def show_future_version(self, commit_spec, path):
        return self.run_command('git show {}:{}'.format(commit_spec, path), silent=True)


    def patch_from_commit(self, commit_ref, path=None):
        commit_spec = self.get_commit_spec(commit_ref)
        self.run_command(
            #'git diff {commit}^ {commit} | patch'.format(commit=commit_spec)
            'git show -M {commit} | patch -p1 --fuzz=3 --no-backup-if-mismatch'.format(commit=commit_spec)
        )
        #self.run_command('git reset')


    def apply_listing_from_commit(self, listing):
        commit_spec = self.get_commit_spec(listing.commit_ref)
        commit_info = self.run_command('git show %s' % (commit_spec,))
        print('Applying listing from commit.\nListing:\n' + listing.contents)

        commit = Commit.from_diff(commit_info)

        files = self.get_files_from_commit_spec(commit_spec)
        if files != [listing.filename]:
            raise ApplyCommitException(
                'wrong files in listing: {0} should have been {1}'.format(
                    listing.filename, files
                )
            )
        future_contents = self.show_future_version(commit_spec, listing.filename)

        check_listing_matches_commit(listing, commit, future_contents)

        self.patch_from_commit(listing.commit_ref, listing.filename)
        listing.was_written = True
        print('applied commit.')



def check_listing_matches_commit(listing, commit, future_contents):
    if listing.is_diff():
        diff = Commit.from_diff(listing.contents)
        if diff.new_lines != commit.new_lines:
            raise ApplyCommitException(
                'diff new lines did not match.\n{}\n!=\n{}'.format(diff.new_lines, commit.new_lines)
            )

        return

    listing_lines = listing.contents.split('\n')
    listing_lines = [strip_comments(l) for l in listing_lines]

    stripped_listing_lines = [l.strip() for l in listing_lines]
    for new_line in commit.new_lines:
        if new_line.strip() not in stripped_listing_lines:
            # print('stripped_listing_lines', stripped_listing_lines)
            raise ApplyCommitException(
                'could not find commit new line {0} in listing:\n{1}'.format(
                    new_line, listing.contents
                )
            )

    future_lines = future_contents.split('\n')
    stripped_future_lines = [l.strip() for l in future_lines]

    check_indentation(listing_lines, future_lines)

    line_pos_in_commit = 0
    for listing_pos, line in enumerate(listing_lines):
        if not line:
            continue
        if line.startswith('[...]'):
            continue
        if line.endswith('[...]'):
            line_start = line.rstrip('[...]').strip()
            if not any(l.startswith(line_start) for l in stripped_future_lines):
                raise ApplyCommitException(
                    'Could not find a line that started with {} in {}'.format(
                        line_start, '\n'.join(stripped_future_lines)
                    )
                )

            continue
        if line in commit.lines_to_add:
            # print('line {} in commit lines to add'.format(line))
            if listing_lines.count(line) > 1:
                # skip duped lines
                # (no way of telling whether dupe is 1st or 2nd)
                assert line in commit.lines_to_add
                print('skipping a dupe commit line')
                continue
            try:
                line_pos_in_commit = commit.lines_to_add[line_pos_in_commit:].index(line)
            except ValueError:
                raise ApplyCommitException(
                    'listing line {} was in wrong order'.format(line)
                )
            continue
        if line.strip() in stripped_future_lines:
            continue
        if line.strip() in [l.strip() for l in commit.deleted_lines]:
            raise ApplyCommitException(
                'listing line {0} was to be deleted'.format(line)
            )
        raise ApplyCommitException('listing line not found:\n%s' % (line,))


def get_offset(lines, future_lines):
    for line in lines:
        if line == '':
            continue
        if line in future_lines:
            return ''
        else:
            for future_line in future_lines:
                if future_line.endswith(line):
                    return future_line[:-len(line)]


def check_indentation(listing_lines, future_lines):
    offset = get_offset(listing_lines, future_lines)
    for listing_line in listing_lines:
        if listing_line and '[...]' not in listing_line:
            fixed_line = offset + listing_line
            if fixed_line not in future_lines:
                raise ApplyCommitException('Could not find {!r} in future contents:\n{}'.format(fixed_line, '\n'.join(future_lines)))

