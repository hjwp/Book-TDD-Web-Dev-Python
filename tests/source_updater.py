#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
from collections import OrderedDict
import os
import re

VIEW_FINDER = re.compile(r'^def (\w+)\(request.*\):$')

def get_indent(line):
    return (len(line) - len(line.lstrip())) * " "


class Block(object):

    def __init__(self, node, source):
        self.name = node.name
        self.node = node
        self.source = source
        self.full_line = self.source.split('\n')[self.node.lineno -1]
        self.start_line = self.node.lineno - 1

    @property
    def is_view(self):
        return bool(VIEW_FINDER.match(self.full_line))


    @property
    def last_line(self):
        last_line_no = max(
            getattr(n, 'lineno', -1) for n in ast.walk(self.node)
        )
        lines = self.source.split('\n')
        if len(lines) > last_line_no:
            for line in lines[last_line_no:]:
                if line.strip() == '':
                    break
                last_line_no += 1
        return last_line_no - 1



class Source(object):

    def __init__(self):
        self.contents = ''

    @classmethod
    def from_path(kls, path):
        source = Source()
        if os.path.exists(path):
            with open(path) as f:
                source.contents = f.read()
        source.path = path
        return source


    @classmethod
    def _from_contents(kls, contents):
        source = Source()
        source.contents = contents
        return source


    @property
    def lines(self):
        return self.contents.split('\n')


    @property
    def functions(self):
        if not hasattr(self, '_functions'):
            self._functions = OrderedDict()
            for node in ast.walk(ast.parse(self.contents)):
                if isinstance(node, ast.FunctionDef):
                    block = Block(node, self.contents)
                    self._functions[block.name] = block
        return self._functions


    @property
    def views(self):
        return OrderedDict((f.name, f) for f in self.functions.values() if f.is_view)


    @property
    def classes(self):
        if not hasattr(self, '_classes'):
            self._classes = OrderedDict()
            for node in ast.walk(ast.parse(self.contents)):
                if isinstance(node, ast.ClassDef):
                    block = Block(node, self.contents)
                    self._classes[block.name] = block
        return self._classes


    def replace_function(self, new_lines):
        function_name = re.search(r'def (\w+)\(.*\):', new_lines[0].strip()).group(1)
        print('replacing function', function_name)
        old_function = self.functions[function_name]
        indent = get_indent(old_function.full_line)
        self.to_write = '\n'.join(
            self.lines[:old_function.start_line] +
            [indent + l for l in new_lines] +
            self.lines[old_function.last_line + 1:]
        )
        return self.to_write


    def remove_function(self, function_name):
        print('removing function %s from \n%s' % (function_name, self.contents))
        function = self.functions[function_name]
        self.to_write = '\n'.join(
            self.lines[:function.start_line] +
            self.lines[function.last_line + 1:]
        )
        self.to_write = re.sub(r'\n\n\n\n+', r'\n\n\n', self.to_write)
        return self.to_write


    def update(self, new_contents):
        self.new_contents = new_contents
        self.new_contents = re.sub(r' +#$', '', self.new_contents, re.MULTILINE)

        self.to_write = self.new_contents
        if not self.to_write.endswith('\n'):
            self.to_write += '\n'


    def write(self):
        with open(self.path, 'w') as f:
            f.write(self.to_write)

