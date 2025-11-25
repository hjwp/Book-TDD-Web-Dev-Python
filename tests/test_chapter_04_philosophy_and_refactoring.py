#!/usr/bin/env python3
import time
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
    Output,
)


class Chapter4Test(ChapterTest):
    chapter_name = "chapter_04_philosophy_and_refactoring"
    previous_chapter = "chapter_03_unit_test_first_view"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Output)
        self.assertEqual(type(self.listings[2]), CodeListing)

        self.start_with_checkout()
        self.start_dev_server()

        self.skip_with_check(38, "add the untracked templates folder")
        self.skip_with_check(40, "review the changes")

        while self.pos < len(self.listings):
            print(self.pos, self.listings[self.pos].type)
            time.sleep(0.5)  # let runserver fs watcher catch up
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff()


if __name__ == "__main__":
    unittest.main()
