#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
    Output,
)

class Chapter5Test(ChapterTest):
    chapter_no = 5

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), CodeListing)
        self.assertEqual(type(self.listings[1]), Command)
        self.assertEqual(type(self.listings[2]), Output)

        self.sourcetree.start_with_checkout(5)
        self.start_dev_server()

        # skips
        self.skip_with_check(61, 'fill out the database NAME')
        self.skip_with_check(70, "3: Buy peacock feathers")

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(5, ignore_moves=True)


if __name__ == '__main__':
    unittest.main()
