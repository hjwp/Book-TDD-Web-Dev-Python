#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from lxml import html


base_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
with open(os.path.join(base_dir, 'book.html')) as f:
    raw_html = f.read()
parsed_html = html.fromstring(raw_html)


class CodeListing(object):

    def __init__(self, filename, contents):
        self.filename = filename
        self.contents = contents
        self.was_written = False
        self.skip = False

    @property
    def type(self):
        if any(l.count('@@') > 1 for l in self.contents.split('\n')):
            return 'diff'
        else:
            return 'code listing'

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

