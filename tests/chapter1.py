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

    def write_to_file(self, codelisting):
        print 'writing to file', codelisting.filename
        with open(os.path.join(self.tempdir, codelisting.filename), 'w') as f:
            f.write(codelisting.contents)
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


    def assert_console_output_correct(self, actual, expected):
        self.assertEqual(type(expected), Output)
        # special case for git init
        if self.tempdir in actual:
            actual = actual.replace(self.tempdir, '/workspace')
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


    def test_listings_and_commands_and_output(self):
        chapter_1 = parsed_html.cssselect('div.sect1')[1]
        listings_nodes = chapter_1.cssselect('div.listingblock')
        listings = [p for n in listings_nodes for p in parse_listing(n)]

        # sanity checks
        self.assertEqual(type(listings[0]), CodeListing)
        self.assertEqual(type(listings[1]), Command)
        self.assertEqual(type(listings[2]), Output)

        self.write_to_file(listings[0])
        first_output = self.run_command(listings[1], cwd=self.tempdir)
        self.assert_console_output_correct(first_output, listings[2])

        self.run_command(listings[3], cwd=self.tempdir) # startproject

        self.assert_directory_tree_correct(listings[4])

        runserver_output = self.run_command(listings[5])
        #self.assert_console_output_correct(runserver_output, listings[6])

        second_ft_run_output = self.run_command(listings[7], cwd=self.tempdir)
        self.assertFalse(second_ft_run_output)
        self.assertEqual(listings[8].strip(), '$')

        ls_output = self.run_command(listings[9], cwd=self.tempdir)
        #self.assert_console_output_correct(
        #    ls_output, listings[10]
        #)
        self.run_command(listings[11], cwd=self.tempdir) # mv
        self.run_command(listings[12], cwd=self.tempdir) # cd
        git_init_output = self.run_command(listings[13])
        self.assert_console_output_correct(git_init_output, listings[14])

        ls_output = self.run_command(listings[15])
        #self.assert_console_output_correct(
        #    ls_output, listings[16]
        #)
        self.run_command(listings[17]) # git add
        git_status_output = self.run_command(listings[18])
        self.assert_console_output_correct(git_status_output, listings[19])

        rm_cached_output = self.run_command(listings[20])
        self.assert_console_output_correct(rm_cached_output, listings[21])
        self.run_command(listings[22])

        git_status_output = self.run_command(listings[23])
        self.assert_console_output_correct(git_status_output, listings[24])

        self.run_command(listings[25])
        #self.run_command(listings[26]) #git commit, no am



if __name__ == '__main__':
    unittest.main()
