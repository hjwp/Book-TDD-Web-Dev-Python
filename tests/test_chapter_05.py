#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import time

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
    Output,
)

class Chapter5Test(ChapterTest):
    chapter_no = 5

    def restart_dev_server(self):
        self.run_command(Command('pkill -f runserver'))
        time.sleep(1)
        self.start_dev_server()
        time.sleep(1)


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), CodeListing)
        self.assertEqual(type(self.listings[1]), Command)
        self.assertEqual(type(self.listings[2]), Output)

        self.sourcetree.start_with_checkout(5)
        self.start_dev_server()

        # skips
        self.skip_with_check(70, "3: Buy peacock feathers")

        while self.pos < len(self.listings):
            if self.pos ==  66:
                self.restart_dev_server()

            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(5, ignore_moves=True)


if __name__ == '__main__':
    unittest.main()
