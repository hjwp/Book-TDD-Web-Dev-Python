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
    chapter_name = 'chapter_03'
    previous_chapter = 'chapter_02'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Output)
        self.assertEqual(type(self.listings[2]), CodeListing)

        self.sourcetree.start_with_checkout(self.previous_chapter)

        self.skip_with_check(10, 'will show you')

        self.start_dev_server()

        final_ft = 41
        self.assertIn('Finish the test', self.listings[final_ft + 1])

        while self.pos < final_ft:
            print(self.pos)
            self.recognise_listing_and_process_it()
        self.restart_dev_server()

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff()


if __name__ == '__main__':
    unittest.main()
