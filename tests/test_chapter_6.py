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

        self.start_with_checkout(self.chapter_no)
        self.start_dev_server()

        # other prep
        self.run_command(Command('python3 manage.py syncdb --noinput'))

        # skips
        self.listings[18].skip = True

        while self.pos < 100:
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.check_final_diff(self.chapter_no)
        self.assert_all_listings_checked(self.listings)


if __name__ == '__main__':
    unittest.main()
