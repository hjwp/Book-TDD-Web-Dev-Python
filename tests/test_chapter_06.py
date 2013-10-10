#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from source_updater import Source
from book_parser import CodeListing
from book_tester import (
    ChapterTest,
    Command,
)

class Chapter6Test(ChapterTest):
    chapter_no = 6

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Command)
        self.assertEqual(type(self.listings[2]), Command)

        self.sourcetree.start_with_checkout(self.chapter_no)

        # other prep
        self.run_command(Command('python3 manage.py syncdb --noinput'))

        # skips
        self.skip_with_check(18, 'msg eg') # git
        self.skip_with_check(53, 'should show 4 changed files') # git
        self.skip_with_check(58, 'add a message summarising') # git
        self.skip_with_check(73, '5 changed files') # git
        self.skip_with_check(75, 'forms x2') # git
        self.skip_with_check(90, '3 changed files') # git

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 60
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch06l021-1')
            ))

        while self.pos < 44:
            print(self.pos)
            self.recognise_listing_and_process_it()


        # special-case: we have a touch followed by some output.
        # just do this one manually
        if self.pos < 45:
            touch = self.listings[44]
            assert 'touch' in touch
            output = self.run_command(touch)
            self.assertFalse(output)
            touch.was_checked = True
            self.pos = 45

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
