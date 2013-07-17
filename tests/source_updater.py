#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

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

    @property
    def lines(self):
        return self.contents.split('\n')


    def update(self, new_contents):
        self.new_contents = new_contents
        if not self.new_contents.endswith('\n'):
            self.new_contents += '\n'


    def write(self):
        with open(self.path, 'w') as f:
            f.write(self.new_contents)
