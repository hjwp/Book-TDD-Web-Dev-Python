# -*- coding: utf-8 -*-
import os
import signal
import subprocess
import shutil
import tempfile
import unittest
from lxml import html

from parsing_tools import (
    CodeListing,
    Command,
    Output,
    parse_listing,
)

base_dir = os.path.split(os.path.dirname(__file__))[0]
raw_html = open(os.path.join(base_dir, 'book.html')).read()
parsed_html = html.fromstring(raw_html)



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
                print 'error killing', process._command
        shutil.rmtree(self.tempdir)


    def write_to_file(self, codelisting):
        print 'writing to file', codelisting.filename
        write_to_file(codelisting, self.tempdir)
        print 'wrote', open(os.path.join(self.tempdir, codelisting.filename)).read()


    def run_command(self, command, cwd=None):
        self.assertEqual(type(command), Command)
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
        print 'directory listing is now', os.listdir(self.tempdir)
        if 'runserver' in command:
            return #test this another day
        process.wait()
        return process.stdout.read().decode('utf8')


    def assert_console_output_correct(self, actual, expected, ls=False):
        self.assertEqual(type(expected), Output)
        # special case for git init
        if self.tempdir in actual:
            actual = actual.replace(self.tempdir, '/workspace')
        if ls:
            actual=actual.strip()
            self.assertItemsEqual(actual.split('\n'), expected.split())
        else:
            self.assertMultiLineEqual(
                actual.strip().replace('\t', '       '),
                expected.replace('\r\n', '\n'),
            )
        expected.was_checked = True


    def assert_directory_tree_correct(self, expected_tree, cwd=None):
        actual_tree = self.run_command(Command('tree -I *.pyc --noreport'), cwd)
        # special case for first listing:
        if expected_tree.startswith('superlists/'):
            print 'FIXING'
            expected_tree = Output(
                expected_tree.replace('superlists/', '.', 1)
            )
        self.assert_console_output_correct(actual_tree, expected_tree)
        return expected_tree

