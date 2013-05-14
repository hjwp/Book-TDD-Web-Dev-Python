# -*- coding: utf-8 -*-
import os
import re
import signal
import subprocess
import shutil
import tempfile
import unittest
from lxml import html

base_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
raw_html = open(os.path.join(base_dir, 'book.html')).read()
parsed_html = html.fromstring(raw_html)


class CodeListing(object):
    def __init__(self, filename, contents):
        self.filename = filename
        self.contents = contents
        self.was_written = False



class Command(unicode):
    def __init__(self, a_string):
        self.was_run = False
        unicode.__init__(a_string)



class Output(unicode):
    def __init__(self, a_string):
        self.was_checked = False
        unicode.__init__(a_string)



def wrap_long_lines(text):
    if any(len(l) > 80 for l in text.split('\n')):

        fixed_text = ''
        for line in text.split('\n'):
            if len(line) < 80:
                fixed_text += line + '\n'
            elif " " not in line:
                textlist = list(text)
                newline = ''
                while textlist:
                    if len(newline) < 79:
                        newline += textlist.pop(0)
                    else:
                        fixed_text += newline + "\n"
                        newline = ""
                fixed_text += newline
            else:
                broken_line = ''
                broken_line += get_indent(line)

                for word in line.split():
                    if len(broken_line + " " + word) < 80:
                        broken_line += word + " "
                    else:
                        fixed_text += broken_line.rstrip() + "\n"
                        broken_line = word + " "
                fixed_text += broken_line.strip() + "\n"
        return fixed_text.strip()
    return text


def parse_listing(listing):
    next_element = listing.getnext()
    if next_element is not None and next_element.get('class') == 'paragraph caption':
        filename = listing.getnext().text_content()
        contents = listing.text_content().strip().replace('\r\n', '\n')
        return [CodeListing(filename, contents)]

    else:
        commands = get_commands(listing)
        lines = listing.text_content().strip().replace('\r\n', '\n').split('\n')
        outputs = []
        output_after_command = ''
        for line in lines:
            line_start, hash, line_comments = line.partition(" #")
            commands_in_this_line = filter(line_start.endswith, commands)
            if commands_in_this_line:
                if output_after_command:
                    outputs.append(Output(output_after_command.rstrip()))
                output_after_command = (hash + line_comments).strip()
                outputs.append(Command(commands_in_this_line[0]))
            else:
                output_after_command += line + '\n'
        if output_after_command:
            outputs.append(Output(output_after_command.rstrip()))
        return outputs


def get_commands(node):
    commands = [
        el.text_content()
        for el in node.cssselect('pre code strong')
    ]
    if commands.count("git rm --cached superlists/"):
        ## hack -- listings with a star in are weird
        fix_pos = commands.index("git rm --cached superlists/")
        commands.remove("git rm --cached superlists/")
        commands.remove(".pyc")
        commands.insert(fix_pos, "git rm --cached superlists/*.pyc")

    return commands

def get_indent(line):
    return (len(line) - len(line.lstrip())) * " "



def _replace_lines_from_to(old_lines, new_lines, start_pos, end_pos):
    indented_new_lines = [get_indent(old_lines[start_pos]) + l for l in new_lines]
    return '\n'.join(
        old_lines[:start_pos] +
        indented_new_lines +
        old_lines[end_pos + 1:]
    )


def _replace_lines_from(old_lines, new_lines, start_pos):
    start_line_in_old = old_lines[start_pos]
    indent = get_indent(start_line_in_old)
    for ix, new_line in enumerate(new_lines):
        if len(old_lines) > start_pos + ix:
            old_lines[start_pos + ix] = indent + new_line
        else:
            old_lines.append(indent + new_line)
    return '\n'.join(old_lines)


def _replace_single_assertion(old_lines, new_lines):
    new_line = new_lines[0]
    assert new_line.startswith("self.assert")
    assertion = new_line.split("(")[0]
    old_line = [
        l for l in old_lines if l.strip().startswith(assertion)
    ][0]
    new_line = get_indent(old_line) + new_line
    return '\n'.join(old_lines).replace(old_line, new_line)


def _find_start_line(old_lines, new_lines):
    stripped_old_lines = [l.strip() for l in old_lines]
    try:
        return stripped_old_lines.index(new_lines[0])
    except ValueError:
        return None


def _find_end_line(old_lines, new_lines):
    start_pos = _find_start_line(old_lines, new_lines)
    stripped_old_lines = [l.strip() for l in old_lines][start_pos:]
    try:
        return stripped_old_lines.index(new_lines[-1].strip()) + start_pos
    except ValueError:
        return None


def _replace_lines_in(old_lines, new_lines):
    if len(new_lines) == 1:
       return _replace_single_assertion(old_lines, new_lines)
    start_pos = _find_start_line(old_lines, new_lines)
    end_pos = _find_end_line(old_lines, new_lines)
    if start_pos is None:
        return '\n'.join(new_lines)

    elif end_pos is None:
        return _replace_lines_from(old_lines, new_lines, start_pos)

    else:
        return _replace_lines_from_to(old_lines, new_lines, start_pos, end_pos)

def write_to_file(codelisting, cwd):
    path = os.path.join(cwd, codelisting.filename)
    if not os.path.exists(path):
        new_contents = codelisting.contents

    else:
        old_contents = open(path).read()
        old_lines = old_contents.strip().split('\n')
        new_lines = codelisting.contents.strip().split('\n')

        if "[..." not in codelisting.contents:
            new_contents = _replace_lines_in(old_lines, new_lines)

        else:
            new_contents = ''
            if codelisting.contents.count("[...") == 1:
                if codelisting.contents.strip().endswith("[...]"):
                    new_lines = new_lines[:-1]
                    new_contents = _replace_lines_in(old_lines, new_lines)

                else:
                    split_line = [l for l in new_lines if "[..." in l][0]
                    split_line_pos = new_lines.index(split_line)
                    lines_before = new_lines[:split_line_pos]
                    last_line_before = lines_before[-1]
                    lines_after = new_lines[split_line_pos + 1:]

                    last_old_line = [
                        l for l in old_lines if l.strip() == last_line_before.strip()
                    ][0]
                    last_old_line_pos = old_lines.index(last_old_line)
                    old_lines_after = old_lines[last_old_line_pos + 1:]

                    # special-case: stray browser.quit in chap. 2
                    if 'rest of comments' in split_line:
                        assert old_lines_after[-1] == 'browser.quit()'
                        old_lines_after.pop()

                    newline_indent = '\n' + get_indent(split_line)

                    new_contents += '\n'.join(lines_before)
                    new_contents += newline_indent
                    new_contents += newline_indent.join(old_lines_after)
                    new_contents += '\n'
                    new_contents += '\n'.join(lines_after)

            elif codelisting.contents.startswith("[...]") and codelisting.contents.endswith("[...]"):
                #TODO replace this with smart block-replacer
                first_line_to_find = new_lines[1]
                last_old_line = [
                    l for l in old_lines if l.strip() == first_line_to_find.strip()
                ][0]
                last_old_line_pos = old_lines.index(last_old_line)

                second_line_to_find = new_lines[-2]
                old_resume_line = [
                    l for l in old_lines if l.strip() == second_line_to_find.strip()
                ][0]
                old_lines_resume_pos = old_lines.index(old_resume_line)

                newline_indent = '\n' + get_indent(last_old_line)
                new_contents += '\n'.join(old_lines[:last_old_line_pos + 1])
                new_contents += newline_indent
                new_contents += newline_indent.join(new_lines[2:-2])
                new_contents += '\n'.join(old_lines[old_lines_resume_pos - 1:])

    new_contents = '\n'.join(
        l.rstrip(' #') for l in new_contents.split('\n')
    )

    if not new_contents.endswith('\n'):
        new_contents += '\n'

    with open(os.path.join(cwd, codelisting.filename), 'w') as f:
        f.write(new_contents)

    codelisting.was_written = True


class ChapterTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.processes = []


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


    def write_to_file(self, codelisting):
        self.assertEqual(
            type(codelisting), CodeListing,
            "passed a non-Codelisting to write_to_file:\n%s" % (codelisting,)
        )
        print 'writing to file', codelisting.filename
        write_to_file(codelisting, os.path.join(self.tempdir, 'superlists'))
        print 'wrote', open(os.path.join(self.tempdir, 'superlists', codelisting.filename)).read()


    def run_command(self, command, cwd=None):
        self.assertEqual(type(command), Command,
            "passed a non-Command to run-command:\n%s" % (command,)
        )
        if cwd is None:
            cwd = os.path.join(self.tempdir, 'superlists')
        print 'running command', command
        process = subprocess.Popen(
            command, shell=True, cwd=cwd, executable='/bin/bash',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        command.was_run = True
        process._command = command
        self.processes.append(process)
        if 'runserver' in command:
            return #test this another day
        output, return_code = process.communicate()
        return output.decode('utf8')


    def assert_console_output_correct(self, actual, expected, ls=False):
        self.assertEqual(
            type(expected), Output,
            "passed a non-Output to run-command:\n%s" % (expected,)
        )

        # special case for git init
        if self.tempdir in actual:
            actual = actual.replace(self.tempdir, '/workspace')

        if ls:
            actual=actual.strip()
            self.assertItemsEqual(actual.split('\n'), expected.split())

        else:
            actual_text = actual.strip().replace('\t', '       ')
            expected_text = expected.replace(' -----', '------')
            actual_text = re.sub(
                r"Ran (\d+) tests? in \d+\.\d\d\ds",
                r"Ran \1 tests in X.Xs",
                actual_text,
            )
            expected_text = re.sub(
                r"Ran (\d+) tests? in \d+\.\d\d\ds",
                r"Ran \1 tests in X.Xs",
                expected_text,
            )
            actual_text = re.sub(
                r"index .......\.\........ 100644",
                r"index XXXXXXX\.\.XXXXXXX 100644",
                actual_text,
            )
            expected_text = re.sub(
                r"index .......\.\........ 100644",
                r"index XXXXXXX\.\.XXXXXXX 100644",
                expected_text,
            )
            actual_text = re.sub(
                r"^[a-f0-9]{7} ",
                r"XXXXXXX ",
                actual_text,
                flags=re.MULTILINE,

            )
            expected_text = re.sub(
                r"^[a-f0-9]{7} ",
                r"XXXXXXX ",
                expected_text,
                flags=re.MULTILINE,
            )

            if expected_text.endswith("[...]"):
                expected_lines = expected_text.split('\n')[:-1]
                expected_text = '\n'.join(l.strip() for l in expected_lines)
                actual_lines = actual_text.split('\n')[:len(expected_lines)]
                actual_text = '\n'.join(l.strip() for l in actual_lines)

            elif expected_text.strip().startswith("[..."):
                # long traceback, only care about output from raise onwards
                expected_lines = expected_text.strip().split('\n')
                raise_line = [
                    l for l in expected_lines if l.strip().startswith("raise")
                ][-1]
                self.assertIn(raise_line, actual_text)
                actual_text = actual_text.split(raise_line)[-1]
                expected_text = expected_text.split(raise_line)[-1].strip()

            elif len(expected_text.split('\n')) < 3:
                for expected_line in expected_text.split('\n'):
                    self.assertIn(expected_line, actual_text)
                expected.was_checked = True
                return

            if "Creating test database for alias 'default'..." in actual_text:
                actual_lines = actual_text.split('\n')
                actual_lines.remove("Creating test database for alias 'default'...")
                actual_lines.insert(0, "Creating test database for alias 'default'...")
                actual_text = '\n'.join(actual_lines)

            actual_text = wrap_long_lines(actual_text)

            self.assertMultiLineEqual(actual_text, expected_text)
        expected.was_checked = True


    def assert_directory_tree_correct(self, expected_tree, cwd=None):
        actual_tree = self.run_command(Command('tree -I *.pyc --noreport'), cwd)
        print 'checking tree', expected_tree
        # special case for first listing:
        if expected_tree.startswith('superlists/'):
            expected_tree = Output(
                expected_tree.replace('superlists/', '.', 1)
            )
        self.assert_console_output_correct(actual_tree, expected_tree)
        return expected_tree


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


    def check_test_code_cycle(self, pos, test_command_in_listings=True):
        self.write_to_file(self.listings[pos])
        self.run_command(Command("find . -name *.pyc -exec rm {} \;"))
        if test_command_in_listings:
            pos += 1
            self.assertIn('test', self.listings[pos])
            test_run = self.run_command(self.listings[pos])
        else:
            test_run = self.run_command(Command("python manage.py test lists"))
        pos += 1
        self.assert_console_output_correct(test_run, self.listings[pos])


    def check_git_diff_and_commit(self, pos):
        LIKELY_FILES = ['urls.py', 'tests.py', 'views.py', 'functional_tests.py']
        self.assertIn('git diff', self.listings[pos])
        git_diff = self.run_command(self.listings[pos])
        self.assertTrue(
            any(l in git_diff for l in LIKELY_FILES),
            'no likely files in diff output %s' % (git_diff,)
        )
        for expected_file in LIKELY_FILES:
            if expected_file in git_diff:
                self.assertIn(expected_file, self.listings[pos + 1])
                self.listings[pos + 1].was_checked = True
        commit = self.run_command(self.listings[pos + 2])
        self.assertIn('insertions', commit)


