#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class Chapter15Test(ChapterTest):
    chapter_name = "chapter_15_simple_form"
    previous_chapter = "chapter_14_database_layer_validation"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "code listing with git ref")
        self.assertEqual(self.listings[1].type, "code listing with git ref")
        self.assertEqual(self.listings[2].type, "output")

        # skips
        self.skip_with_check(31, "# review changes")  # diff

        # prep
        self.start_with_checkout()
        self.prep_database()

        # hack fast-forward
        self.skip_forward_if_skipto_set()

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(ignore=["moves"])


if __name__ == "__main__":
    unittest.main()
