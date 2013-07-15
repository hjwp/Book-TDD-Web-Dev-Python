#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import os
import re
from textwrap import dedent


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
    try:
        return next(c for c in functions if c.name == function_name)
    except StopIteration:
        raise Exception('Could not find function named %s' % (function_name,))


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
    function_name = re.search(r'def (\w+)\(.*\):', new_lines[0].strip()).group(1)
    function = _get_function(source, function_name)
    last_line = _find_last_line_in_function(source, function_name)

    indent = get_indent(old_lines[function.lineno - 1])
    return '\n'.join(
        old_lines[:function.lineno - 1] +
        [indent + l for l in new_lines] +
        old_lines[last_line + 1:]
    )


def remove_function(source, function_name):
    print('removing function %s from \n%s' % (function_name, source))
    old_lines = source.split('\n')
    function = _get_function(source, function_name)
    last_line = _find_last_line_in_function(source, function_name)
    new_source = '\n'.join(
        old_lines[:function.lineno - 1] +
        old_lines[last_line + 1:]
    )
    new_source = re.sub(r'\n\n\n\n+', r'\n\n\n', new_source)
    return new_source


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
    stripped_start_line = new_lines[0].strip()
    stripped_old_lines = [l.strip() for l in old_lines]
    try:
        return stripped_old_lines.index(stripped_start_line)
    except ValueError:
        print('could not find start line %r' % (stripped_start_line,))
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
        print('no start line found')
        if 'import' in new_lines[0] and 'import' in old_lines[0]:
            new_contents = new_lines[0] + '\n'
            return new_contents + _replace_lines_in(old_lines[1:], new_lines[1:])

        view_finder = re.compile(r'^def (\w+)\(request.*\):$')
        if view_finder.match(new_lines[0]):
            if any(view_finder.match(l) for l in old_lines):
                view_name = view_finder.search(new_lines[0]).group(1)
                old_views = []
                for old_line in old_lines:
                    if view_finder.match(old_line):
                        old_views.append(view_finder.match(old_line).group(1))
                if view_name in old_views:
                    return _replace_function(old_lines, new_lines)
                return '\n'.join(old_lines) + '\n\n\n' + '\n'.join(new_lines)

        class_finder = re.compile(r'^class \w+\(.+\):$', re.MULTILINE)
        if class_finder.match(new_lines[0]):
            print('found class in input')
            print(class_finder.findall('\n'.join(old_lines)))
            if len(class_finder.findall('\n'.join(old_lines))) > 1:
                print('found classes')
                return '\n'.join(old_lines) + '\n\n\n\n' + '\n'.join(new_lines)

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
    if ',' in codelisting.filename:
        files = codelisting.filename.split(', ')
    else:
        files = [codelisting.filename]
    new_contents = codelisting.contents
    for filename in files:
        path = os.path.join(cwd, filename)
        _write_to_file(path, new_contents)
        with open(os.path.join(path)) as f:
            print(f.read())
    codelisting.was_written = True


def _write_to_file(path, new_contents):
    if not os.path.exists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)

    else:
        with open(path) as f:
            old_contents = f.read()
        old_lines = old_contents.strip().split('\n')
        new_lines = new_contents.strip('\n').split('\n')
        # strip callouts
        new_lines = [re.sub(r' +#$', '', l) for l in new_lines]

        if new_contents.strip() in SPECIAL_CASES:
            to_replace = SPECIAL_CASES[new_contents.strip()]
            replace_with = r'\1' + new_contents.strip() + '\n'
            assert re.search(to_replace, old_contents), 'could not find \n%s\n in \n%r\n' % (to_replace, old_contents)
            new_contents = re.sub(to_replace, replace_with, old_contents)

        elif "[..." not in new_contents:
            new_contents = _replace_lines_in(old_lines, new_lines)

        else:
            if new_contents.count("[...") == 1:
                split_line = [l for l in new_lines if "[..." in l][0]
                split_line_pos = new_lines.index(split_line)

                if split_line_pos == 0:
                    new_contents = _replace_lines_in(old_lines, new_lines[1:])

                elif split_line == new_lines[-1]:
                    new_contents = _replace_lines_in(old_lines, new_lines[:-1])

                elif split_line_pos == 1:
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

                    new_contents = '\n'.join(
                        lines_before +
                        [get_indent(split_line) + l for l in old_lines_after] +
                        lines_after
                    )

            elif new_contents.startswith("[...]") and new_contents.endswith("[...]"):
                new_contents = _replace_lines_in(old_lines, new_lines[1:-1])
            else:
                raise Exception("I don't know how to deal with this")

    # strip trailing whitespace
    new_contents = re.sub(r'^ +$', '', new_contents, flags=re.MULTILINE)

    if not new_contents.endswith('\n'):
        new_contents += '\n'

    with open(os.path.join(path), 'w') as f:
        f.write(new_contents)


