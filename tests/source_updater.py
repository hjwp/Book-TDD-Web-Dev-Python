#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import os
import re

VIEW_FINDER = re.compile(r'^def (\w+)\(request.*\):$')

class Function(object):

    def __init__(self, function, source):
        self.name = function.name
        self.function = function
        self.source = source
        self.full_line = self.source.split('\n')[self.function.lineno -1]

    @property
    def is_view(self):
        return bool(VIEW_FINDER.match(self.full_line))


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
            self._functions = []
            for node in ast.walk(ast.parse(self.contents)):
                if isinstance(node, ast.FunctionDef):
                    self._functions.append(Function(node, self.contents))
        return self._functions


    @property
    def views(self):
        return [f for f in self.functions if f.is_view]


    def update(self, new_contents):
        self.new_contents = new_contents
        self.new_contents = re.sub(r' +#$', '', self.new_contents, re.MULTILINE)

        self.to_write = self.new_contents
        if not self.to_write.endswith('\n'):
            self.to_write += '\n'


    def write(self):
        with open(self.path, 'w') as f:
            f.write(self.to_write)

