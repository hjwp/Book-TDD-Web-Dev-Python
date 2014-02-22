#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
from collections import OrderedDict
import os
import re
from textwrap import dedent

VIEW_FINDER = re.compile(r'^def (\w+)\(request.*\):$')


class SourceUpdateError(Exception):
    pass


def get_indent(line):
    return (len(line) - len(line.lstrip())) * " "


class Block(object):

    def __init__(self, node, source):
        self.name = node.name
        self.node = node
        self.full_source = source
        self.start_line = self.node.lineno - 1
        self.full_line = self.full_source.split('\n')[self.start_line]
        self.source = '\n'.join(
            self.full_source.split('\n')[self.start_line:self.last_line + 1]
        )


    @property
    def is_view(self):
        return bool(VIEW_FINDER.match(self.full_line))


    @property
    def last_line(self):
        last_line_no = max(
            getattr(n, 'lineno', -1) for n in ast.walk(self.node)
        )
        lines = self.full_source.split('\n')
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
            for node in self.ast:
                if isinstance(node, ast.FunctionDef):
                    block = Block(node, self.contents)
                    self._functions[block.name] = block
        return self._functions


    @property
    def views(self):
        return OrderedDict((f.name, f) for f in self.functions.values() if f.is_view)


    @property
    def ast(self):
        try:
            return list(ast.walk(ast.parse(self.contents)))
        except SyntaxError:
            return []


    @property
    def classes(self):
        if not hasattr(self, '_classes'):
            self._classes = OrderedDict()
            for node in self.ast:
                if isinstance(node, ast.ClassDef):
                    block = Block(node, self.contents)
                    self._classes[block.name] = block
        return self._classes


    @property
    def _import_nodes(self):
        for node in self.ast:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                node.full_line = self.lines[node.lineno - 1]
                yield node

    @property
    def _deduped_import_nodes(self):
        from_imports = {}
        other_imports = []
        for node in self._import_nodes:
            if isinstance(node, ast.Import):
                other_imports.append(node)
            else:
                if node.module in from_imports:
                    if len(node.names) > len(from_imports[node.module].names):
                        from_imports[node.module] = node
                else:
                    from_imports[node.module] = node
        return other_imports + list(from_imports.values())


    @property
    def imports(self):
        for node in self._deduped_import_nodes:
            yield node.full_line

    @property
    def django_imports(self):
        return [i for i in self.imports if i.startswith('from django')]

    @property
    def project_imports(self):
        return [i for i in self.imports if i.startswith('from lists')]

    @property
    def general_imports(self):
        return [i for i in self.imports if i not in self.django_imports and i not in self.project_imports]

    @property
    def fixed_imports(self):
        import_sections = []
        if self.general_imports:
            import_sections.append('\n'.join(sorted(self.general_imports)))
        if self.django_imports:
            import_sections.append('\n'.join(sorted(self.django_imports)))
        if self.project_imports:
            import_sections.append('\n'.join(sorted(self.project_imports)))

        fixed_imports = '\n\n'.join(import_sections)
        if fixed_imports and not fixed_imports.endswith('\n'):
            fixed_imports += '\n'
        return fixed_imports


    def find_first_nonimport_line(self):
        try:
            first_nonimport = next(l for l in self.lines if l and l not in self.imports)
        except StopIteration:
            return len(self.lines)
        pos = self.lines.index(first_nonimport)
        if self._import_nodes:
            if pos < max(n.lineno for n in self._import_nodes):
                raise SourceUpdateError('first nonimport (%s) was before end of imports (%s)' % (
                    first_nonimport, max(n.lineno for n in self._import_nodes))
                )
        return pos


    def replace_function(self, new_lines):
        function_name = re.search(r'def (\w+)\(.*\):', new_lines[0].strip()).group(1)
        print('replacing function', function_name)
        old_function = self.functions[function_name]
        indent = get_indent(old_function.full_line)
        self.contents = '\n'.join(
            self.lines[:old_function.start_line] +
            [indent + l for l in new_lines] +
            self.lines[old_function.last_line + 1:]
        )
        return self.contents


    def remove_function(self, function_name):
        print('removing function %s' % (function_name,))
        function = self.functions[function_name]
        self.contents = '\n'.join(
            self.lines[:function.start_line] +
            self.lines[function.last_line + 1:]
        )
        self.contents = re.sub(r'\n\n\n\n+', r'\n\n\n', self.contents)
        return self.contents


    def find_start_line(self, new_lines):
        if not new_lines:
            raise SourceUpdateError()
        start_line = new_lines[0].strip()
        if start_line == '':
            raise SourceUpdateError()

        try:
            return [l.strip() for l in self.lines].index(start_line.strip())
        except ValueError:
            print('no start line match for', start_line)


    def add_to_class(self, classname, new_lines):
        new_lines = dedent('\n'.join(new_lines)).strip().split('\n')
        klass = self.classes[classname]
        lines_before_class = '\n'.join(self.lines[:klass.start_line])
        print('lines before\n', lines_before_class)
        lines_after_class = '\n'.join(self.lines[klass.last_line + 1:])
        print('lines after\n', lines_after_class)
        new_class = klass.source + '\n\n\n' + '\n'.join(
            '    ' + l for l in new_lines
        )
        print('new class\n', new_class)
        self.contents = lines_before_class + '\n' + new_class + '\n' + lines_after_class


    def find_end_line(self, new_lines):
        if not new_lines:
            raise SourceUpdateError()
        end_line = new_lines[-1].strip()
        if end_line == '':
            raise SourceUpdateError()
        start_line = self.find_start_line(new_lines)

        try:
            from_start = [l.strip() for l in self.lines[start_line:]].index(end_line.strip())
            return start_line + from_start
        except ValueError:
            print('no end line match for', end_line)


    def add_imports(self, imports):
        post_import_lines = self.lines[self.find_first_nonimport_line():]
        self.contents = '\n'.join(imports + self.lines)
        self.contents = (
            self.fixed_imports + '\n' +
            '\n'.join(post_import_lines)
        )


    def update(self, new_contents):
        self.contents = new_contents


    def get_updated_contents(self):
        if not self.contents.endswith('\n'):
            self.contents += '\n'
        return self.contents


    def write(self):
        with open(self.path, 'w') as f:
            f.write(self.get_updated_contents())

