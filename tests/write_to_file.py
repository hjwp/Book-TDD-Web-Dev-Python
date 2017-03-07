#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import os
import re
from textwrap import dedent

from source_updater import (
    VIEW_FINDER,
    get_indent,
    Source,
)

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


def _replace_lines_in(old_lines, new_lines):
    source = Source._from_contents('\n'.join(old_lines))
    if new_lines[0].strip() == '':
        new_lines.pop(0)
    new_lines = dedent('\n'.join(new_lines)).split('\n')
    if len(new_lines) == 1:
        return _replace_single_line(old_lines, new_lines)

    start_pos = source.find_start_line(new_lines)
    if start_pos is None:
        print('no start line found')
        if 'import' in new_lines[0] and 'import' in old_lines[0]:
            new_contents = new_lines[0] + '\n'
            return new_contents + _replace_lines_in(old_lines[1:], new_lines[1:])

        if VIEW_FINDER.match(new_lines[0]):
            if source.views:
                view_name = VIEW_FINDER.search(new_lines[0]).group(1)
                if view_name in source.views:
                    return source.replace_function(new_lines)
                return '\n'.join(old_lines) + '\n\n' + '\n'.join(new_lines)

        class_finder = re.compile(r'^class \w+\(.+\):$', re.MULTILINE)
        if class_finder.match(new_lines[0]):
            print('found class in input')
            if len(source.classes) > 1:
                print('found classes')
                return '\n'.join(old_lines) + '\n\n\n' + '\n'.join(new_lines)

        return '\n'.join(new_lines)

    end_pos = source.find_end_line(new_lines)
    if end_pos is None:
        if new_lines[0].strip().startswith('def '):
            return source.replace_function(new_lines)

        else:
            #TODO: can we get rid of this?
            return _replace_lines_from(old_lines, new_lines, start_pos)

    else:
        return _replace_lines_from_to(old_lines, new_lines, start_pos, end_pos)



def add_import_and_new_lines(new_lines, old_lines):
    source = Source._from_contents('\n'.join(old_lines))
    print('add import and new lines')
    source.add_imports(new_lines[:1])
    lines_with_import = source.get_updated_contents().split('\n')
    new_lines_remaining = '\n'.join(new_lines[2:]).strip('\n').split('\n')
    start_pos = source.find_start_line(new_lines_remaining)
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
    source = Source._from_contents('\n'.join(old_lines))
    classname = re.search(r'class (\w+)\(\w+\):', new_lines[0]).group(1)
    source.add_to_class(classname, new_lines[2:])
    return source.get_updated_contents()



def write_to_file(codelisting, cwd):
    if ',' in codelisting.filename:
        files = codelisting.filename.split(', ')
    else:
        files = [codelisting.filename]
    new_contents = codelisting.contents
    for filename in files:
        path = os.path.join(cwd, filename)
        _write_to_file(path, new_contents)
        #with open(os.path.join(path)) as f:
        #    print(f.read())
    codelisting.was_written = True


def _write_to_file(path, new_contents):
    source = Source.from_path(path)
    # strip callouts
    new_contents = re.sub(r' +#$', '', new_contents, flags=re.MULTILINE)
    new_contents = re.sub(r' +//$', '', new_contents, flags=re.MULTILINE)

    if not os.path.exists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)

    else:
        old_lines = source.lines
        new_lines = new_contents.strip('\n').split('\n')

        if "[..." not in new_contents:
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
                        assert 'browser.quit()' in [l.strip() for l in old_lines_after]
                        assert old_lines_after[-2] == 'browser.quit()'
                        old_lines_after = old_lines_after[:-2]

                    new_contents = '\n'.join(
                        lines_before +
                        [get_indent(split_line) + l for l in old_lines_after] +
                        lines_after
                    )

            elif new_contents.strip().startswith("[...]") and new_contents.endswith("[...]"):
                new_contents = _replace_lines_in(old_lines, new_lines[1:-1])
            else:
                raise Exception("I don't know how to deal with this")

    # strip trailing whitespace
    new_contents = re.sub(r'^ +$', '', new_contents, flags=re.MULTILINE)
    source.update(new_contents)
    source.write()

