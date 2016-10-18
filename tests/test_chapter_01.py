#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    write_to_file
)

os.environ['LC_ALL'] = 'en_GB.UTF-8'
os.environ['LANG'] = 'en_GB.UTF-8'
os.environ['LANGUAGE'] = 'en_GB.UTF-8'


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
        self.assertEqual(self.listings[1].skip, True)

        self.skip_with_check(9, 'Performing system checks...') # after runserver
        status1_pos = 22
        assert self.listings[status1_pos] == 'git status'
        status2_pos = 28
        assert self.listings[status2_pos] == 'git status'

        # first code listing
        self.recognise_listing_and_process_it()

        # first couple of commands needs manual cwd-setting
        first_output = self.run_command(self.listings[4], cwd=self.tempdir)
        self.assert_console_output_correct(first_output, self.listings[5])
        self.run_command(self.listings[6], cwd=self.tempdir) # startproject

        # 4. tree
        self.assert_directory_tree_correct(self.listings[7], cwd=self.tempdir)
        self.pos = 8

        # 6. runserver
        self.recognise_listing_and_process_it()

        second_ft_run_output = self.run_command(self.listings[10], cwd=self.tempdir)
        self.assertFalse(second_ft_run_output)
        self.assertEqual(self.listings[11].strip(), '$')
        self.listings[11].was_checked = True

        ls_output = self.run_command(self.listings[12], cwd=self.tempdir)
        self.assert_console_output_correct(
            ls_output, self.listings[13], ls=True
        )
        self.run_command(self.listings[14], cwd=self.tempdir) # mv
        self.run_command(self.listings[15], cwd=self.tempdir) # cd

        self.pos = 16

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
