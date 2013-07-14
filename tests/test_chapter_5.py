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

        self.start_with_checkout(5)
        self.start_dev_server()

        # skips
        self.listings[58].skip = True
        self.listings[67].skip = True

        while self.pos < 76:
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.check_final_diff(5)
        self.assert_all_listings_checked(self.listings)


if __name__ == '__main__':
    unittest.main()
