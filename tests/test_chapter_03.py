#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
    Output,
)

class Chapter3Test(ChapterTest):
    chapter_no = 3

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Output)
        self.assertEqual(type(self.listings[2]), CodeListing)

        self.sourcetree.start_with_checkout(self.chapter_no)

        self.skip_with_check(10, 'will show you')

        self.run_command(Command('python3 manage.py runserver'))

        while self.pos < 43:
            print(self.pos)
            self.recognise_listing_and_process_it()
        self.start_dev_server()
        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.check_final_diff(self.chapter_no)
        self.assert_all_listings_checked(self.listings)


if __name__ == '__main__':
    unittest.main()
