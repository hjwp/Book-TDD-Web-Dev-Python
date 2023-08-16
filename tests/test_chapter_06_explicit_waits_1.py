#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_tester import (
    ChapterTest,
    Command,
)

class Chapter6Test(ChapterTest):
    chapter_name = 'chapter_06_explicit_waits_1'
    previous_chapter = 'chapter_05_post_and_database'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Command)
        self.assertEqual(type(self.listings[2]), Command)

        # skips
        self.skip_with_check(15, 'msg eg') # git

        # other prep
        self.start_with_checkout()
        self.unset_PYTHONDONTWRITEBYTECODE()
        self.run_command(Command('python3 manage.py migrate --noinput'))

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 127
            self.sourcetree.run_command('git checkout {}'.format(
                self.sourcetree.get_commit_spec('ch06l036-2')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff()


if __name__ == '__main__':
    unittest.main()
