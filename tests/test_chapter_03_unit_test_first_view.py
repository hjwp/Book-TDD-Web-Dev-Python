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

class Chapter3Test(ChapterTest):
    chapter_name = 'chapter_03_unit_test_first_view'
    previous_chapter = 'chapter_02_unittest'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Output)
        self.assertEqual(type(self.listings[2]), CodeListing)

        self.skip_with_check(10, 'will show you')
        final_ft = 43
        self.assertIn('Finish the test', self.listings[final_ft + 1])

        self.start_with_checkout()
        self.start_dev_server()
        self.unset_PYTHONDONTWRITEBYTECODE()

        print(self.pos)
        assert 'manage.py startapp lists' in self.listings[self.pos]
        self.recognise_listing_and_process_it()
        time.sleep(1)  # voodoo sleep, otherwise db.sqlite3 doesnt appear in CI sometimes

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
