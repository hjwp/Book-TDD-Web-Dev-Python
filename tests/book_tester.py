#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import signal
import subprocess
import shutil
import tempfile
from textwrap import wrap
import unittest

from write_to_file import write_to_file
from book_parser import (
    CodeListing,
    Command,
    Output,
    parsed_html,
    parse_listing,
)



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


def strip_test_speed(output):
    return re.sub(
        r"Ran (\d+) tests? in \d+\.\d\d\ds",
        r"Ran \1 tests in X.Xs",
        output,
    )


def fix_dict_repr_order(string):
    dict_finder = r"({'\w+': .+, '\w+': .+})"
    if not re.search(dict_finder, string):
        return string

    for dict_repr in re.findall(dict_finder, string):
        items = re.search(
            r"{('\w+': .+), ('\w+': .+)}",
            dict_repr,
        ).groups()
        string = string.replace(dict_repr, "{%s}" % (', '.join(sorted(items)),))
    return string


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
        self.tempdir = tempfile.mkdtemp()
        self.processes = []
        self.pos = 0
        self.dev_server_running = False


    def tearDown(self):
        for process in self.processes:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                pass
        shutil.rmtree(self.tempdir)


    def start_with_checkout(self, chapter):
        local_repo_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../source/chapter_%d/superlists' % (chapter,)
        ))
        self.run_command(Command('mkdir superlists'), cwd=self.tempdir)
        self.run_command(Command('git init .'))
        self.run_command(Command('git remote add repo %s' % (local_repo_path,)))
        self.run_command(Command('git fetch repo'))
        self.run_command(Command('git checkout chapter_%s' % (chapter - 1,)))


    def parse_listings(self):
        chapter = parsed_html.cssselect('div.sect1')[self.chapter_no]
        listings_nodes = chapter.cssselect('div.listingblock')
        self.listings = [p for n in listings_nodes for p in parse_listing(n)]


    def check_final_diff(self, chapter):
        diff = self.run_command(Command('git diff -b repo/chapter_%d' % (chapter,)))
        if diff != '':
            raise AssertionError('Final diff was not empty, was:\n%s' % (diff,))


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
        if cwd is None:
            cwd = os.path.join(self.tempdir, 'superlists')
        print('running command', command)
        process = subprocess.Popen(
            command, shell=True, cwd=cwd, executable='/bin/bash',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            preexec_fn=os.setsid,
            universal_newlines=True,
        )
        command.was_run = True
        process._command = command
        self.processes.append(process)
        if 'runserver' in command:
            return #test this another day
        if user_input and not user_input.endswith('\n'):
            user_input += '\n'
        #import time
        #time.sleep(1)
        output, _ = process.communicate(user_input)
        if process.returncode and 'test' not in command:
            print('process %s return a non-zero code (%s)' % (command, process.returncode))
            print('output:\n', output)
            raise Exception('process %s return a non-zero code (%s)' % (command, process.returncode))
        return output


    def assertLineIn(self, line, lines):
        if line not in lines:
            raise AssertionError('%s not found in:\n%s' % (
                repr(line), '\n'.join(repr(l) for l in lines))
            )

    def assert_console_output_correct(self, actual, expected, ls=False):
        print('checking expected output', expected)
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
        #print('actual before')
        #print(actual)
        actual_fixed = wrap_long_lines(actual)
        actual_fixed = strip_test_speed(actual_fixed)
        actual_fixed = strip_git_hashes(actual_fixed)
        actual_fixed = fix_creating_database_line(actual_fixed)
        actual_fixed = fix_dict_repr_order(actual_fixed)

        expected_fixed = fix_test_dashes(expected)
        expected_fixed = strip_test_speed(expected_fixed)
        expected_fixed = strip_git_hashes(expected_fixed)

        if '\t' in actual_fixed:
            actual_fixed = re.sub(r'\s+', ' ', actual_fixed)
            expected_fixed = re.sub(r'\s+', ' ', expected_fixed)
        #print('actual fixed')
        #print(actual_fixed)

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


    def assert_directory_tree_correct(self, expected_tree, cwd=None):
        actual_tree = self.run_command(Command('tree -I *.pyc --noreport'), cwd)
        print('checking tree', expected_tree)
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
        self.run_command(Command("find . -name *.pyc -exec rm {} \;"))
        self.run_command(Command("find . -name __pycache__ -exec rm -r {} \;"))
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
        self.run_command(Command("find . -name *.pyc -exec rm {} \;"))


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
        self.assertIn('insertions', commit)
        self.pos += 1


    def check_diff_or_status(self, pos):
        LIKELY_FILES = ['urls.py', 'tests.py', 'views.py', 'functional_tests.py']
        self.assertTrue(
            'diff' in self.listings[pos] or 'status' in self.listings[pos]
        )
        git_output = self.run_command(self.listings[pos])
        self.assertTrue(
            any('/' + l in git_output for l in LIKELY_FILES),
            'no likely files in diff output %s' % (git_output,)
        )
        self.pos += 1
        comment = self.listings[pos + 1]
        if comment.type != 'output':
            return
        if not any(f in comment for f in LIKELY_FILES):
            print('WARNING -- git comment without files: %s' % (comment,))
            self.pos += 1
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


    def recognise_listing_and_process_it(self):
        listing = self.listings[self.pos]
        if listing.skip:
            print("SKIP")
            listing.was_checked = True
            listing.was_written = True
            self.pos += 1
        elif listing.type == 'test':
            print("TEST RUN")
            self.run_test_and_check_result()
        elif listing.type == 'git diff':
            print("DIFF")
            self.check_diff_or_status(self.pos)
        elif listing.type == 'git status':
            print("STATUS")
            self.check_diff_or_status(self.pos)
        elif listing.type == 'git commit':
            print("COMMIT")
            self.check_commit(self.pos)

        elif listing.type == 'interactive syncdb':
            print("INTERACTIVE SYNCDB")
            expected_output_start = self.listings[self.pos + 1]
            user_input = self.listings[self.pos + 2]
            expected_output_end = self.listings[self.pos + 3]
            expected_output = Output(expected_output_start + ' ' + expected_output_end)

            self.assertTrue(isinstance(user_input, Command))
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

        elif listing.type == 'other command':
            print("A COMMAND")
            output = self.run_command(listing)
            next_listing = self.listings[self.pos + 1]
            if type(next_listing) == Output:
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

        elif listing.type == 'code listing':
            print("CODE")
            self.write_to_file(listing)
            self.pos += 1

        elif listing.type == 'output':
            self._strip_out_any_pycs()
            test_run = self.run_command(Command("python3 manage.py test lists"))
            if 'OK' in  test_run and not 'OK' in listing:
                print('unit tests pass, must be an FT:\n', test_run)
                if os.path.exists(os.path.join(self.tempdir, 'superlists', 'functional_tests')):
                    test_run = self.run_command(Command("python3 manage.py test functional_tests"))
                else:
                    test_run = self.run_command(Command("python3 functional_tests.py"))
            self.assert_console_output_correct(test_run, listing)
            self.pos += 1

        else:
            self.fail('not implemented for ' + listing)

