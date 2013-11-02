#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
)

class Chapter2Test(ChapterTest):
    chapter_no = 2

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), CodeListing)
        self.assertEqual(type(self.listings[2]), Command)

        self.sourcetree.start_with_checkout(self.chapter_no)

        self.listings[1].skip = True # aside
        self.listings[5].skip = True # aside
        while self.pos < 13:
            print(self.pos)
            self.recognise_listing_and_process_it()
        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
