#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import os
import re
import signal
import subprocess
import shutil
import tempfile
from textwrap import dedent, wrap
import unittest
from lxml import html

base_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
with open(os.path.join(base_dir, 'book.html')) as f:
    raw_html = f.read()
parsed_html = html.fromstring(raw_html)


class CodeListing(object):
    type = 'code listing'

    def __init__(self, filename, contents):
        self.filename = filename
        self.contents = contents
        self.was_written = False
        self.skip = False

    def __repr__(self):
        return '<CodeListing %s: %s...>' % (self.filename, self.contents.split('\n')[0])




class Command(str):
    def __init__(self, a_string):
        self.was_run = False
        self.skip = False
        str.__init__(a_string)

    @property
    def type(self):
        for git_cmd in ('git diff', 'git status', 'git commit'):
            if git_cmd in self:
                return git_cmd
        if self.startswith('python') and 'test' in self:
            return 'test'
        if self == 'python3 manage.py syncdb':
            return 'interactive syncdb'
        else:
            return 'other command'

    def __repr__(self):
        return '<Command %s>' % (str.__repr__(self),)




class Output(str):

    def __init__(self, a_string):
        self.was_checked = False
        self.skip = False
        str.__init__(a_string)

    @property
    def type(self):
        if u'├' in self:
            return 'tree'
        else:
            return 'output'


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

def parse_listing(listing):
    if  'sourcecode' in listing.get('class').split():
        filename = listing.cssselect('.title')[0].text_content().strip()
        contents = listing.cssselect('.content')[0].text_content().replace('\r\n', '\n').strip('\n')
        return [CodeListing(filename, contents)]

    else:
        commands = get_commands(listing)
        lines = listing.text_content().strip().replace('\r\n', '\n').split('\n')
        outputs = []
        output_after_command = ''
        for line in lines:
            line_start, hash, line_comments = line.partition(" #")
            commands_in_this_line = list(filter(line_start.strip().endswith, commands))
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
    print('replace lines from line', start_pos, 'to line', end_pos)
    old_indent = get_indent(old_lines[start_pos])
    new_indent = get_indent(new_lines[0])
    if new_indent:
        missing_indent = old_indent[:-len(new_indent)]
    else:
        missing_indent = old_indent
    indented_new_lines = [missing_indent + l for l in new_lines]
    return '\n'.join(
        old_lines[:start_pos] +
        indented_new_lines +
        old_lines[end_pos + 1:]
    )


def _get_function(source, function_name):
    functions = [
        n for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.FunctionDef)
    ]
    return next(c for c in functions if c.name == function_name)


def _find_last_line_in_function(source, function_name):
    function = _get_function(source, function_name)
    last_line_no = max(
        getattr(n, 'lineno', -1) for n in ast.walk(function)
    )
    lines = source.split('\n')
    if len(lines) > last_line_no:
        for line in lines[last_line_no:]:
            if not line:
                break
            last_line_no += 1
    return last_line_no - 1


def _replace_function(old_lines, new_lines):
    print('replace function')
    source = '\n'.join(old_lines)
    function_name = re.search(r'def (\w+)\(\w*\):', new_lines[0].strip()).group(1)
    function = _get_function(source, function_name)
    last_line = _find_last_line_in_function(source, function_name)

    indent = get_indent(old_lines[function.lineno - 1])
    return '\n'.join(
        old_lines[:function.lineno - 1] +
        [indent + l for l in new_lines] +
        old_lines[last_line + 1:]
    )


def _replace_lines_from(old_lines, new_lines, start_pos):
    print('replace lines from line', start_pos)
    start_line_in_old = old_lines[start_pos]
    indent = get_indent(start_line_in_old)
    for ix, new_line in enumerate(new_lines):
        if len(old_lines) > start_pos + ix:
            old_lines[start_pos + ix] = indent + new_line
        else:
            old_lines.append(indent + new_line)
    return '\n'.join(old_lines)


def _number_of_identical_chars_at_beginning(string1, string2):
    n = 0
    for char1, char2 in zip(string1, string2):
        if char1 != char2:
            return n
        n += 1
    return n

def number_of_identical_chars(string1, string2):
    string1, string2 = string1.strip(), string2.strip()
    start_num = _number_of_identical_chars_at_beginning(string1, string2)
    end_num = _number_of_identical_chars_at_beginning(
            reversed(string1), reversed(string2)
    )
    return min(len(string1), start_num + end_num)


def _replace_single_line(old_lines, new_lines):
    print('replace single line')
    new_line = new_lines[0]
    line_finder = lambda l: number_of_identical_chars(l, new_line)
    likely_line = sorted(old_lines, key=line_finder)[-1]
    new_line = get_indent(likely_line) + new_line
    new_content = '\n'.join(old_lines).replace(likely_line, new_line)
    return new_content


def _find_start_line(old_lines, new_lines):
    stripped_old_lines = [l.strip() for l in old_lines]
    try:
        return stripped_old_lines.index(new_lines[0].strip())
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
    if new_lines[0].strip() == '':
        new_lines.pop(0)
    new_lines = dedent('\n'.join(new_lines)).split('\n')
    if len(new_lines) == 1:
       return _replace_single_line(old_lines, new_lines)

    start_pos = _find_start_line(old_lines, new_lines)
    if start_pos is None:
        if 'import' in new_lines[0] and 'import' in old_lines[0]:
            new_contents = new_lines[0] + '\n'
            return new_contents + _replace_lines_in(old_lines[1:], new_lines[1:])
        return '\n'.join(new_lines)

    end_pos = _find_end_line(old_lines, new_lines)
    if end_pos is None:
        if new_lines[0].strip().startswith('def '):
            return _replace_function(old_lines, new_lines)
        else:
            #TODO: can we get rid of this?
            return _replace_lines_from(old_lines, new_lines, start_pos)

    else:
        return _replace_lines_from_to(old_lines, new_lines, start_pos, end_pos)


def insert_new_import(import_line, old_lines):
    print('inserting new import')
    general_imports = []
    django_imports = []
    project_imports = []
    other_lines = []
    last_import = next(reversed([l for l in old_lines if 'import' in l]))
    found_last_import = False
    for line in old_lines + [import_line]:
        if line == last_import:
            found_last_import = True
        if line.startswith('from django'):
            django_imports.append(line)
        elif line.startswith('from lists'):
            project_imports.append(line)
        elif 'import' in line:
            general_imports.append(line)
        elif line == '' and not found_last_import:
            pass
        else:
            other_lines.append(line)
    general_imports.sort()
    if general_imports and django_imports or general_imports and project_imports:
        general_imports.append('')
    django_imports.sort()
    if django_imports and project_imports:
        django_imports.append('')
    project_imports.sort()
    return general_imports + django_imports + project_imports + other_lines


def add_import_and_new_lines(new_lines, old_lines):
    print('add import and new lines')
    lines_with_import = insert_new_import(new_lines[0], old_lines)
    new_lines_remaining = '\n'.join(new_lines[2:]).strip('\n').split('\n')
    start_pos = _find_start_line(old_lines, new_lines_remaining)
    if start_pos is None:
        return '\n'.join(lines_with_import) + '\n\n\n' + '\n'.join(new_lines_remaining)
    else:
        return _replace_lines_in(lines_with_import, new_lines_remaining)


def _find_last_line_for_class(source, classname):
    all_nodes = list(ast.walk(ast.parse(source)))
    classes = [n for n in all_nodes if isinstance(n, ast.ClassDef)]
    our_class = next(c for c in classes if c.name == classname)
    last_line_in_our_class = max(
            getattr(thing, 'lineno', 0) for thing in ast.walk(our_class)
    )
    return last_line_in_our_class


def add_to_class(new_lines, old_lines):
    print('adding to class')
    classname = re.search(r'class (\w+)\(\w+\):', new_lines[0]).group(1)
    insert_point = _find_last_line_for_class('\n'.join(old_lines), classname)
    return '\n'.join(
        old_lines[:insert_point] + new_lines[2:] + old_lines[insert_point:]
    )



SPECIAL_CASES = {
    "self.assertIn('1: Buy peacock feathers', [row.text for row in rows])":
    (
        r'(\s+)self.assertTrue\(\n'
        r"\s+any\(row.text == '1: Buy peacock feathers' for row in rows\),\n"
        r'\s+"New to-do item did not appear in table -- its text was:\\n%s" % \(\n'
        r'\s+table.text,\n'
        r'\s+\)\n'
        r'\s+\)\n'
    )
}


def write_to_file(codelisting, cwd):
    path = os.path.join(cwd, codelisting.filename)
    if not os.path.exists(path):
        new_contents = codelisting.contents
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)

    else:
        with open(path) as f:
            old_contents = f.read()
        old_lines = old_contents.strip().split('\n')
        new_lines = codelisting.contents.strip('\n').split('\n')
        # strip callouts
        new_lines = [re.sub(r' +#$', '', l) for l in new_lines]

        if codelisting.contents.strip() in SPECIAL_CASES:
            to_replace = SPECIAL_CASES[codelisting.contents.strip()]
            replace_with = r'\1' + codelisting.contents.strip() + '\n'
            assert re.search(to_replace, old_contents), 'could not find \n%s\n in \n%r\n' % (to_replace, old_contents)
            new_contents = re.sub(to_replace, replace_with, old_contents)

        elif "[..." not in codelisting.contents:
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
                    if split_line_pos == 1:
                        if 'import' in new_lines[0]:
                            new_contents = add_import_and_new_lines(new_lines, old_lines)
                        elif 'class' in new_lines[0]:
                            new_contents = add_to_class(new_lines, old_lines)

                    else:
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

                        new_contents += '\n'.join(
                            lines_before +
                            [get_indent(split_line) + l for l in old_lines_after] +
                            lines_after
                        )

            elif codelisting.contents.startswith("[...]") and codelisting.contents.endswith("[...]"):
                new_contents = _replace_lines_in(old_lines, new_lines[1:-1])
            else:
                raise Exception("I don't know how to deal with this")

    # strip trailing whitespace
    new_contents = re.sub(r'^ +$', '', new_contents, flags=re.MULTILINE)


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
        with open(os.path.join(self.tempdir, 'superlists', codelisting.filename)) as f:
            print(f.read())


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
        output, return_code = process.communicate(user_input)
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
        for expected_file in LIKELY_FILES:
            if '/' + expected_file in git_output:
                comment = self.listings[pos + 1]
                if not expected_file in comment:
                    self.fail(
                        "could not find %s in comment %r given git output\n%s" % (
                            expected_file, comment, git_output)
                    )
                self.listings[pos + 1].was_checked = True
        self.pos += 2


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
            self.listings[self.pos + 1].was_checked = True
            self.listings[self.pos + 2].was_checked = True
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


        elif listing.type == 'code listing':
            print("CODE")
            self.write_to_file(listing)
            self.pos += 1

        elif listing.type == 'output':
            self._strip_out_any_pycs()
            test_run = self.run_command(Command("python3 manage.py test lists"))
            if 'OK' in  test_run:
                print('unit tests pass, must be an FT:\n', test_run)
                test_run = self.run_command(Command("python3 functional_tests.py"))
            self.assert_console_output_correct(test_run, listing)
            self.pos += 1

        else:
            self.fail('not implemented for ' + listing)



