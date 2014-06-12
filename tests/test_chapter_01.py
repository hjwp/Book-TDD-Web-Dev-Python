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

        self.skip_with_check(6, 'Validating models...') # after runserver
        status1_pos = 19
        assert self.listings[status1_pos] == 'git status'
        status2_pos = 25
        assert self.listings[status2_pos] == 'git status'

        # first code listing
        self.recognise_listing_and_process_it()

        # first couple of commands needs manual cwd-setting
        first_output = self.run_command(self.listings[1], cwd=self.tempdir)
        self.assert_console_output_correct(first_output, self.listings[2])
        self.run_command(self.listings[3], cwd=self.tempdir) # startproject

        # 4. tree
        self.assert_directory_tree_correct(self.listings[4], cwd=self.tempdir)
        self.pos = 5

        # 6. runserver
        self.recognise_listing_and_process_it()

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

        self.pos = 13

        while self.pos < status1_pos:
            print(self.pos)
            self.recognise_listing_and_process_it()

        status1_output = self.run_command(self.listings[status1_pos])
        expected_output = self.listings[status1_pos + 1]
        self.assert_console_output_correct(status1_output, expected_output)
        self.pos = status1_pos + 2

        while self.pos < status2_pos:
            print(self.pos)
            self.recognise_listing_and_process_it()

        status2_output = self.run_command(self.listings[status2_pos])
        expected_output = self.listings[status2_pos + 1]
        self.assert_console_output_correct(status2_output, expected_output)
        self.pos = status2_pos + 2

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)

        # manually add repo, we didn't do it at the beginning
        local_repo_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../source/chapter_01/superlists'
        ))
        self.sourcetree.run_command(
            'git remote add repo "{}"'.format(local_repo_path)
        )
        self.sourcetree.run_command(
            'git fetch repo'
        )

        # manual fix of dev settings docs links
        self.sourcetree.run_command(
            'sed -i "s:/dev/:/1.7/:g" superlists/settings.py'
        )

        self.check_final_diff(self.chapter_no, ignore_secret_key=True)


if __name__ == '__main__':
    unittest.main()
