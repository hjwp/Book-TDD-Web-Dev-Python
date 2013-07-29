#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_parser import CodeListing, Command, Output
from book_tester import ChapterTest

class Chapter7Test(ChapterTest):
    chapter_no = 7

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), CodeListing)
        self.assertEqual(type(self.listings[1]), Command)
        self.assertEqual(type(self.listings[2]), Output)

        self.sourcetree.start_with_checkout(self.chapter_no)
        #self.start_dev_server()

        # other prep
        self.run_command(Command('python3 manage.py syncdb --noinput'))

        # skips
        self.listings[18].skip = True


        while self.pos < 200:
            print(self.pos)
            self.recognise_listing_and_process_it()

        #import time
        #print(self.tempdir)
        #time.sleep(200)


        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
