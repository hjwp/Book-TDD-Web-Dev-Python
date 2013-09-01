#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
    Output,
    write_to_file
)

class Chapter1Test(ChapterTest):
    chapter_no = 1

    def write_to_file(self, codelisting):
        # override write to file, in this chapter cwd is root tempdir
        print('writing to file', codelisting.filename)
        write_to_file(codelisting, os.path.join(self.tempdir))
        print('wrote', open(os.path.join(self.tempdir, codelisting.filename)).read())


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), CodeListing)
        self.assertEqual(type(self.listings[1]), Command)
        self.assertEqual(type(self.listings[2]), Output)

        self.write_to_file(self.listings[0])
        first_output = self.run_command(self.listings[1], cwd=self.tempdir)
        self.assert_console_output_correct(first_output, self.listings[2])

        self.run_command(self.listings[3], cwd=self.tempdir) # startproject

        self.assert_directory_tree_correct(self.listings[4])

        runserver_output = self.run_command(self.listings[5])
        #self.assert_console_output_correct(runserver_output, self.listings[6])
        self.listings[6].was_checked = True #TODO - fix

        second_ft_run_output = self.run_command(self.listings[7], cwd=self.tempdir)
        self.assertFalse(second_ft_run_output)
        self.assertEqual(self.listings[8].strip(), '$')
        self.listings[8].was_checked = True

        ls_output = self.run_command(self.listings[9], cwd=self.tempdir)
        self.assert_console_output_correct(
            ls_output, self.listings[10], ls=True
        )
        self.run_command(self.listings[11], cwd=self.tempdir) # mv
        self.run_command(self.listings[12], cwd=self.tempdir) # cd
        git_init_output = self.run_command(self.listings[13])
        self.assert_console_output_correct(git_init_output, self.listings[14])

        ls_output = self.run_command(self.listings[15])
        self.assert_console_output_correct(
            ls_output, self.listings[16], ls=True
        )
        self.run_command(self.listings[17]) # git add
        git_status_output = self.run_command(self.listings[18])
        self.assert_console_output_correct(git_status_output, self.listings[19])

        rm_cached_output = self.run_command(self.listings[20])
        self.assert_console_output_correct(rm_cached_output, self.listings[21])
        self.run_command(self.listings[22]) # ignore __pycache__
        self.run_command(self.listings[23]) # ignore pycs

        git_status_output = self.run_command(self.listings[24])
        self.assert_console_output_correct(git_status_output, self.listings[25])

        self.run_command(self.listings[26])
        #self.run_command(self.listings[26]) #git commit, no am
        commit = Command(self.listings[27] + ' -am"first commit"')
        self.run_command(commit)
        self.listings[27].was_run = True # TODO
        local_repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../source/chapter_01/superlists'))
        self.run_command(Command('git remote add repo %s' % (local_repo_path,)))
        self.run_command(Command('git fetch repo'))
        diff = self.run_command(Command('git diff -b repo/chapter_01'))
        actual_diff_lines = diff.strip().split('\n')

        expected_diff_lines = [
           u"diff --git a/superlists/settings.py b/superlists/settings.py",
            "index 2326f30..956bff8 100644",
            "--- a/superlists/settings.py",
            "+++ b/superlists/settings.py",
            "@@ -83,7 +83,7 @@ STATICFILES_FINDERS = (",
            " )",
            " ",
            " # Make this unique, and don't share it with anybody.",
            "-SECRET_KEY = 'k0(t##0$lx9d#7do0d-47tdxo)pvs+knkc@&mfapc(e%_74ghq'",
            "+SECRET_KEY = '-pr7xq9-786$n9vasjc1!covnbayhfw%p0@zm9c-p-(-4y#lqf'",
            " ",
            " # List of callables that know how to import templates from various sources.",
            " TEMPLATE_LOADERS = (",
        ]
        self.assertEqual(actual_diff_lines[0], expected_diff_lines[0])
        self.assertTrue(actual_diff_lines[1].startswith("index"))
        self.assertEqual(actual_diff_lines[2:9], expected_diff_lines[2:9])
        self.assertEqual(actual_diff_lines[10:], expected_diff_lines[10:])
        self.assertTrue(actual_diff_lines[8].startswith("-SECRET_KEY"))

        self.assert_all_listings_checked(self.listings)


if __name__ == '__main__':
    unittest.main()
