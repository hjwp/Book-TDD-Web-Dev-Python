#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lxml import html
import os
import re
import subprocess
import tempfile
from textwrap import wrap
import unittest

from write_to_file import write_to_file
from book_parser import (
    CodeListing,
    Command,
    Output,
    parse_listing,
)
from sourcetree import Commit, SourceTree



def wrap_long_lines(text):
    paragraphs = text.split('\n')
    return '\n'.join(
        '\n'.join(wrap(p, 79, break_long_words=True, break_on_hyphens=False))
        for p in paragraphs
    )


def fix_test_dashes(output):
    return output.replace(' ' + '-' * 69, '-' * 70)


def strip_git_hashes(output):
    fixed_indexes = re.sub(
        r"index .......\.\........ 100644",
        r"index XXXXXXX\.\.XXXXXXX 100644",
        output,
    )
    fixed_commit_numbers = re.sub(
            r"^[a-f0-9]{7} ",
            r"XXXXXXX ",
            fixed_indexes,
            flags=re.MULTILINE,

    )
    return fixed_commit_numbers


def strip_callouts(output):
    return re.sub(
        r"^(.+)( ?<\d+>)$",
        r"\1",
        output,
        flags=re.MULTILINE,
    )


def strip_test_speed(output):
    return re.sub(
        r"Ran (\d+) tests? in \d+\.\d\d\ds",
        r"Ran \1 tests in X.Xs",
        output,
    )


def fix_creating_database_line(actual_text):
    if "Creating test database for alias 'default'..." in actual_text:
        actual_lines = actual_text.split('\n')
        actual_lines.remove("Creating test database for alias 'default'...")
        actual_lines.insert(0, "Creating test database for alias 'default'...")
        actual_text = '\n'.join(actual_lines)
    return actual_text


class ChapterTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.sourcetree = SourceTree()
        self.tempdir = self.sourcetree.tempdir
        self.processes = []
        self.pos = 0
        self.dev_server_running = False
        self.current_server_cd = None


    def tearDown(self):
        self.sourcetree.cleanup()


    def parse_listings(self):
        base_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
        filename = 'chapter_{0:02d}.html'.format(self.chapter_no)
        with open(os.path.join(base_dir, filename), encoding='utf-8') as f:
            raw_html = f.read()
        parsed_html = html.fromstring(raw_html)
        listings_nodes = parsed_html.cssselect('div.listingblock')
        self.listings = [p for n in listings_nodes for p in parse_listing(n)]


    def check_final_diff(self, chapter, ignore_moves=False, ignore_secret_key=False):
        diff = self.run_command(Command(
            'git diff -b repo/chapter_{0:02d}'.format(chapter)
        ))
        print('checking final diff', diff)
        start_marker = 'diff --git a/\n'
        commit = Commit(start_marker + diff)
        error = AssertionError('Final diff was not empty, was:\n{}'.format(diff))

        if ignore_secret_key:
            for line in commit.lines_to_add + commit.lines_to_remove:
                if 'SECRET_KEY' not in line:
                    raise error

        elif ignore_moves:
            if commit.deleted_lines or commit.new_lines:
                raise error

        elif commit.lines_to_add or commit.lines_to_remove:
            raise error



    def write_to_file(self, codelisting):
        self.assertEqual(
            type(codelisting), CodeListing,
            "passed a non-Codelisting to write_to_file:\n%s" % (codelisting,)
        )
        print('writing to file', codelisting.filename)
        write_to_file(codelisting, os.path.join(self.tempdir, 'superlists'))
        filenames = codelisting.filename.split(', ')
        for filename in filenames:
            with open(os.path.join(self.tempdir, 'superlists', filename)) as f:
                print('wrote:')
                print(f.read())


    def apply_patch(self, codelisting):
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.write(codelisting.contents.encode('utf8'))
        tf.write('\n'.encode('utf8'))
        tf.close()
        print('patch:\n', codelisting.contents)
        patch_output = self.run_command(
            Command('patch %s %s' % (codelisting.filename, tf.name))
        )
        print(patch_output)
        self.assertNotIn('malformed', patch_output)
        self.assertNotIn('failed', patch_output.lower())
        codelisting.was_checked = True
        with open(os.path.join(self.tempdir, 'superlists', codelisting.filename)) as f:
            print(f.read())
        os.remove(tf.name)
        self.pos += 1
        codelisting.was_written = True


    def run_command(self, command, cwd=None, user_input=None):
        self.assertEqual(type(command), Command,
            "passed a non-Command to run-command:\n%s" % (command,)
        )
        print('running command', command)
        output = self.sourcetree.run_command(command, cwd=cwd, user_input=user_input)
        command.was_run = True
        return output


    def _cleanup_runserver(self):
            self.run_server_command('pkill -f runserver', ignore_errors=True)

    RUN_SERVER_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'run_server_command.py')
    )
    def run_server_command(self, command, ignore_errors=False):
        cd_finder = re.compile(r'cd (.+)$')
        if cd_finder.match(command):
            self.current_server_cd = cd_finder.match(command).group(1)
        if command.startswith('sudo apt-get install '):
            command = command.replace('install ', 'install -y ')
        if self.current_server_cd:
            command = 'cd %s && %s' % (self.current_server_cd, command)
        if '$SITENAME' in command:
            command = 'SITENAME=superlists-staging.ottg.eu; ' + command
        if command.endswith('python3 manage.py runserver'):
            command = command.replace(
                'python3 manage.py runserver',
                'dtach -n /tmp/dtach.sock python3 manage.py runserver'
            )

        print('running command on server', command)
        commands = ['python2.7', self.RUN_SERVER_PATH]
        if ignore_errors:
            commands.append('--ignore-errors')
        commands.append(command)
        output = subprocess.check_output(commands).decode('utf8')

        print(output.encode('utf-8'))
        return output


    def write_file_on_server(self, target, contents):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(contents.encode('utf8'))
            tf.flush()
            output = subprocess.check_output(
                ['python2.7', self.RUN_SERVER_PATH, tf.name, target]
            ).decode('utf8')
            print(output)


    def assertLineIn(self, line, lines):
        if line not in lines:
            raise AssertionError('%s not found in:\n%s' % (
                repr(line), '\n'.join(repr(l) for l in lines))
            )

    def assert_console_output_correct(self, actual, expected, ls=False):
        print('checking expected output', expected.encode('utf-8'))
        self.assertEqual(
            type(expected), Output,
            "passed a non-Output to run-command:\n%s" % (expected,)
        )

        if self.tempdir in actual:
            actual = actual.replace(self.tempdir, '/workspace')

        if ls:
            actual=actual.strip()
            self.assertCountEqual(actual.split('\n'), expected.split())
            expected.was_checked = True
            return

        actual_fixed = wrap_long_lines(actual)
        actual_fixed = strip_test_speed(actual_fixed)
        actual_fixed = strip_git_hashes(actual_fixed)
        actual_fixed = fix_creating_database_line(actual_fixed)

        expected_fixed = fix_test_dashes(expected)
        expected_fixed = strip_test_speed(expected_fixed)
        expected_fixed = strip_git_hashes(expected_fixed)
        expected_fixed = strip_callouts(expected_fixed)

        if '\t' in actual_fixed:
            actual_fixed = re.sub(r'\s+', ' ', actual_fixed)
            expected_fixed = re.sub(r'\s+', ' ', expected_fixed)

        actual_lines = actual_fixed.split('\n')
        expected_lines = expected_fixed.split('\n')

        for line in expected_lines:
            if line.startswith('[...'):
                continue
            if line.endswith('[...]'):
                line = line.rstrip('[...]').rstrip()
                self.assertLineIn(line, [l[:len(line)] for l in actual_lines])
            elif line.startswith(' '):
                self.assertLineIn(line, actual_lines)
            else:
                self.assertLineIn(line, [l.strip() for l in actual_lines])

        if len(expected_lines) > 4 and '[...' not in expected_fixed:
            self.assertMultiLineEqual(actual_fixed.strip(), expected_fixed.strip())

        expected.was_checked = True


    def skip_with_check(self, pos, expected_content):
        listing = self.listings[pos]
        if hasattr(listing, 'contents'):
            assert expected_content in listing.contents
        else:
            assert expected_content in listing
        listing.skip = True



    def assert_directory_tree_correct(self, expected_tree, cwd=None):
        actual_tree = self.sourcetree.run_command('tree -I *.pyc --noreport', cwd)
        print('checking tree', expected_tree.encode('utf-8'))
        # special case for first listing:
        original_tree = expected_tree
        if expected_tree.startswith('superlists/'):
            expected_tree = Output(
                expected_tree.replace('superlists/', '.', 1)
            )
        self.assert_console_output_correct(actual_tree, expected_tree)
        original_tree.was_checked = True


    def assert_all_listings_checked(self, listings, exceptions=[]):
        for i, listing in enumerate(listings):
            if i in exceptions:
                continue
            if listing.skip:
                continue

            if type(listing) == CodeListing:
                self.assertTrue(
                    listing.was_written,
                    'Listing %d not written:\n%s' % (i, listing)
                )
            if type(listing) == Command:
                self.assertTrue(
                    listing.was_run,
                    'Command %d not run:\n%s' % (i, listing)
                )
            if type(listing) == Output:
                self.assertTrue(
                    listing.was_checked,
                    'Output %d not checked:\n%s' % (i, listing)
                )


    def check_test_code_cycle(self, pos, test_command_in_listings=True, ft=False):
        self.write_to_file(self.listings[pos])
        self._strip_out_any_pycs()
        if test_command_in_listings:
            pos += 1
            self.assertIn('test', self.listings[pos])
            test_run = self.run_command(self.listings[pos])
        elif ft:
            test_run = self.run_command(Command("python3 functional_tests.py"))
        else:
            test_run = self.run_command(Command("python3 manage.py test lists"))
        pos += 1
        self.assert_console_output_correct(test_run, self.listings[pos])


    def _strip_out_any_pycs(self):
        self.sourcetree.run_command(
            "find . -name __pycache__ -exec rm -r {} \;",
            ignore_errors=True
        )


    def run_test_and_check_result(self):
        self.assertIn('test', self.listings[self.pos])
        self._strip_out_any_pycs()
        test_run = self.run_command(self.listings[self.pos])
        self.assert_console_output_correct(test_run, self.listings[self.pos + 1])
        self.pos += 2


    def check_commit(self, pos):
        if self.listings[pos].endswith('commit -a'):
            self.listings[pos] = Command(
                self.listings[pos] + 'm "commit for listing %d"' % (self.pos,)
            )
        elif self.listings[pos].endswith('commit'):
            self.listings[pos] = Command(
                self.listings[pos] + ' -am "commit for listing %d"' % (self.pos,)
            )

        commit = self.run_command(self.listings[pos])
        self.assertIn('insertion', commit)
        self.pos += 1


    def check_diff_or_status(self, pos):
        LIKELY_FILES = [
            'urls.py', 'tests.py', 'views.py', 'functional_tests.py',
            'settings.py', 'home.html', 'list.html', 'base.html',
            'tests/test_',
        ]
        self.assertTrue(
            'diff' in self.listings[pos] or 'status' in self.listings[pos]
        )
        git_output = self.run_command(self.listings[pos])
        if not any('/' + l in git_output for l in LIKELY_FILES):
            if not 'lists/' in git_output:
                self.fail('no likely files in diff output %s' % (git_output,))
        self.pos += 1
        comment = self.listings[pos + 1]
        if comment.skip:
            comment.was_checked = True
            self.pos += 1
            return
        if comment.type != 'output':
            return
        for expected_file in LIKELY_FILES:
            if '/' + expected_file in git_output:
                if not expected_file in comment:
                    self.fail(
                        "could not find %s in comment %r given git output\n%s" % (
                            expected_file, comment, git_output)
                    )
                self.listings[pos + 1].was_checked = True
        comment.was_checked = True
        self.pos += 1


    def check_git_diff_and_commit(self, pos):
        self.check_diff_or_status(pos)
        self.check_commit(pos + 2)


    def start_dev_server(self):
        self.run_command(Command('python3 manage.py runserver'))
        self.dev_server_running = True


    def run_fts(self):
        if os.path.exists(os.path.join(self.tempdir, 'superlists', 'functional_tests')):
            return self.run_command(Command("python3 manage.py test functional_tests"))
        else:
            return self.run_command(Command("python3 functional_tests.py"))

    def recognise_listing_and_process_it(self):
        listing = self.listings[self.pos]
        if listing.dofirst:
            print("DOFIRST", listing.dofirst)
            self.sourcetree.checkout_file_from_commit_ref(
                listing.dofirst,
            )
        if listing.skip:
            print("SKIP")
            listing.was_checked = True
            listing.was_written = True
            self.pos += 1
        elif listing.type == 'test':
            print("TEST RUN")
            self.run_test_and_check_result()
        elif listing.type == 'git diff':
            print("GIT DIFF")
            self.check_diff_or_status(self.pos)
        elif listing.type == 'git status':
            print("STATUS")
            self.check_diff_or_status(self.pos)
        elif listing.type == 'git commit':
            print("COMMIT")
            self.check_commit(self.pos)

        elif listing.type == 'interactive manage.py':
            print("INTERACTIVE MANAGE.PY")
            user_input = self.listings[self.pos + 2]
            assert isinstance(user_input, Command)

            expected_output_start = self.listings[self.pos + 1]
            assert isinstance(expected_output_start, Output)
            expected_output_end = self.listings[self.pos + 3]
            assert isinstance(expected_output_end, Output)
            expected_output = Output(wrap_long_lines(expected_output_start + ' ' + expected_output_end))

            output = self.run_command(listing, user_input=user_input)
            self.assert_console_output_correct(output, expected_output)
            listing.was_checked = True
            user_input.was_run = True
            self.listings[self.pos + 1].was_checked = True
            self.listings[self.pos + 3].was_checked = True
            self.pos += 4

        elif listing.type == 'tree':
            print("TREE")
            self.assert_directory_tree_correct(listing)
            self.pos += 1

        elif listing.type == 'server command':
            self.run_server_command(listing)
            self.pos += 1
            listing.was_run = True

        elif listing.type == 'other command':
            print("A COMMAND")
            output = self.run_command(listing)
            next_listing = self.listings[self.pos + 1]
            if next_listing.type == 'output' and not next_listing.skip:
                ls = listing.startswith('ls')
                self.assert_console_output_correct(output, next_listing, ls=ls)
                next_listing.was_checked = True
                listing.was_checked = True
                self.pos += 2
            elif 'tree' in listing and next_listing.type == 'tree':
                self.assert_console_output_correct(output, next_listing)
                next_listing.was_checked = True
                listing.was_checked = True
                self.pos += 2
            else:
                listing.was_checked = True
                self.pos += 1

        elif listing.type == 'diff':
            print("DIFF")
            self.apply_patch(listing)

        elif listing.type == 'code listing currentcontents':
            actual_contents = self.sourcetree.get_contents(
                listing.filename
            )
            print("CHECK CURRENT CONTENTS")
            if '[...]' in listing.contents:
                stripped_actual_lines = [l.strip() for l in actual_contents.split('\n')]
                for line in listing.contents.split('\n'):
                    if line and not '[...]' in line:
                        self.assertIn(line.strip(), stripped_actual_lines)
            else:
                self.assertEqual(
                    listing.contents.strip(),
                    actual_contents.strip(),
                )
            listing.was_written = True
            self.pos += 1

        elif listing.type == 'code listing':
            print("CODE")
            self.write_to_file(listing)
            self.pos += 1

        elif listing.type == 'code listing with git ref':
            print("CODE FROM GIT REF")
            self.sourcetree.apply_listing_from_commit(listing)
            self.pos += 1

        elif listing.type == 'server code listing':
            print("SERVER CODE")
            self.write_file_on_server(listing.filename, listing.contents)
            self.pos += 1

        elif listing.type == 'output':
            self._strip_out_any_pycs()
            test_run = self.run_command(Command("python3 manage.py test lists"))
            if 'OK' in  test_run and not 'OK' in listing:
                print('unit tests pass, must be an FT:\n', test_run)
                test_run = self.run_fts()
            try:
                self.assert_console_output_correct(test_run, listing)
            except AssertionError as e:
                if 'OK' in test_run and 'OK' in listing:
                    print('got error when checking unit tests', e)
                    test_run = self.run_fts()
                    self.assert_console_output_correct(test_run, listing)
                else:
                    raise

            self.pos += 1

        else:
            self.fail('not implemented for ' + str(listing))

