# -*- coding: utf-8 -*-
import os
import signal
import subprocess
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



class Chapter1Test(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.processes = []

    def tearDown(self):
        for process in self.processes:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                print 'error killing', process._command

    def write_to_file(self, codelisting):
        print 'writing to file', codelisting.filename
        with open(os.path.join(self.tempdir, codelisting.filename), 'w') as f:
            f.write(codelisting.contents)
        print 'wrote', open(os.path.join(self.tempdir, codelisting.filename)).read()


    def run_command(self, command):
        self.assertEqual(type(command), Command)
        cwd = self.tempdir
        if 'superlists' in os.listdir(self.tempdir):
            cwd = os.path.join(self.tempdir, 'superlists')
        if 'functional_tests.py' in command and 'functional_tests.py' in os.listdir(self.tempdir):
            cwd = self.tempdir
        print 'running command', command
        process = subprocess.Popen(
            command, shell=True, cwd=cwd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        command.was_run = True
        process._command = command
        self.processes.append(process)
        print 'directory listing is now', os.listdir(self.tempdir)
        if 'runserver' in command:
            return
        process.wait()
        return process.stdout.read().decode('utf8')


    def assert_console_output_correct(self, actual, expected):
        self.assertEqual(type(expected), Output)
        self.assertMultiLineEqual(
            actual.strip(),
            expected.replace('\r\n', '\n'),
        )
        expected.was_checked = True


    def assert_directory_tree_correct(self, expected_tree):
        actual_tree = self.run_command(Command('tree -I *.pyc --noreport'))
        # special case for first listing:
        if expected_tree.startswith('superlists/'):
            print 'FIXING'
            expected_tree = Output(
                expected_tree.replace('superlists/', '.', 1)
            )
        self.assert_console_output_correct(actual_tree, expected_tree)


    def test_listings_and_commands_and_output(self):
        chapter_1 = parsed_html.cssselect('div.sect1')[1]
        listings_nodes = chapter_1.cssselect('div.listingblock')
        listings = [p for n in listings_nodes for p in parse_listing(n)]

        self.assertEqual(type(listings[0]), CodeListing)
        self.assertEqual(type(listings[1]), Command)
        self.assertEqual(type(listings[2]), Output)

        self.write_to_file(listings[0])
        first_output = self.run_command(listings[1])
        self.assert_console_output_correct(first_output, listings[2])

        self.run_command(listings[3])

        self.assert_directory_tree_correct(listings[4])




if __name__ == '__main__':
    unittest.main()
