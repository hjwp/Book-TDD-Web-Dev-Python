#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

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

        # skips
        self.skip_with_check(15, 'msg eg') # git
        self.skip_with_check(60, 'should show 4 changed files') # git
        self.skip_with_check(65, 'add a message summarising') # git
        self.skip_with_check(80, '5 changed files') # git
        self.skip_with_check(82, 'forms x2') # git
        self.skip_with_check(109, '3 changed files') # git
        touch_pos = 53
        touch = self.listings[touch_pos]
        assert 'touch' in touch

        # other prep
        self.sourcetree.start_with_checkout(self.chapter_no)
        self.run_command(Command('python3 manage.py migrate --noinput'))

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 114
            self.sourcetree.run_command('git checkout {}'.format(
                self.sourcetree.get_commit_spec('ch06l033')
            ))

        while self.pos < touch_pos:
            print(self.pos)
            self.recognise_listing_and_process_it()


        # special-case: we have a touch followed by some output.
        # just do this one manually
        if self.pos < touch_pos + 1:
            output = self.run_command(touch)
            self.assertFalse(output)
            touch.was_checked = True
            self.pos = touch_pos + 1

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no, ignore_moves=True)


if __name__ == '__main__':
    unittest.main()
