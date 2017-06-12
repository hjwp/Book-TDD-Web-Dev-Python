#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    write_to_file
)
from update_source_repo import update_sources_for_chapter

os.environ['LC_ALL'] = 'en_GB.UTF-8'
os.environ['LANG'] = 'en_GB.UTF-8'
os.environ['LANGUAGE'] = 'en_GB.UTF-8'


class Chapter1Test(ChapterTest):
    chapter_name = 'chapter_01'

    def write_to_file(self, codelisting):
        # override write to file, in this chapter cwd is root tempdir
        print('writing to file', codelisting.filename)
        write_to_file(codelisting, os.path.join(self.tempdir))
        print('wrote', open(os.path.join(self.tempdir, codelisting.filename)).read())


    def test_listings_and_commands_and_output(self):
        update_sources_for_chapter(self.chapter_name, previous_chapter=None)
        self.parse_listings()
        # self.fail('\n'.join(f'{l.type}: {l}' for l in self.listings))

        # sanity checks
        self.assertEqual(type(self.listings[0]), CodeListing)
        # self.assertEqual(self.listings[1].skip, True)

        self.skip_with_check(6, 'Performing system checks...') # after runserver
        status1_pos = 20
        assert self.listings[status1_pos] == 'git status'
        status2_pos = 26
        assert self.listings[status2_pos] == 'git status'

        startproject_pos = 3
        assert self.listings[startproject_pos] == 'django-admin.py startproject superlists'

        # first code listing
        self.recognise_listing_and_process_it()

        # first couple of commands needs manual cwd-setting
        first_output = self.run_command(self.listings[1], cwd=self.tempdir)
        self.assert_console_output_correct(first_output, self.listings[2])
        self.run_command(self.listings[startproject_pos], cwd=self.tempdir)

        # 4. tree
        self.assert_directory_tree_correct(self.listings[4], cwd=self.tempdir)
        self.pos = 5

        # 6. runserver
        self.recognise_listing_and_process_it()
        self.pos += 1

        second_ft_run_output = self.run_command(self.listings[self.pos], cwd=self.tempdir)
        self.assertFalse(second_ft_run_output)
        self.pos += 1

        self.assertEqual(self.listings[self.pos].strip(), '$')
        self.listings[self.pos].was_checked = True
        self.pos += 1

        ls_output = self.run_command(self.listings[self.pos], cwd=self.tempdir)
        self.pos += 1
        self.assert_console_output_correct(
            ls_output, self.listings[self.pos], ls=True
        )
        self.pos += 1
        self.run_command(self.listings[self.pos], cwd=self.tempdir) # mv
        self.pos += 1
        self.run_command(self.listings[self.pos], cwd=self.tempdir) # cd
        self.pos += 1

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
        # self.sourcetree.run_command(
        #     'sed -i "s:/dev/:/1.7/:g" superlists/settings.py'
        # )

        self.check_final_diff(ignore="SECRET_KEY")


if __name__ == '__main__':
    unittest.main()
