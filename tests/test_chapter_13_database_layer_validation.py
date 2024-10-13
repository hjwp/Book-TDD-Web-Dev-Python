#!/usr/bin/env python3
import os
import unittest

from book_tester import ChapterTest


class Chapter13Test(ChapterTest):
    chapter_name = "chapter_13_database_layer_validation"
    previous_chapter = "chapter_13_organising_test_files"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "test")
        self.assertEqual(self.listings[1].type, "output")
        self.assertEqual(self.listings[2].type, "code listing with git ref")

        # other prep
        self.start_with_checkout()
        self.prep_database()

        # self.skip_with_check(5, "equivalent to running sqlite3")

        # hack fast-forward
        if os.environ.get("SKIP"):
            self.pos = 3
            self.sourcetree.run_command(
                "git checkout {}".format(self.sourcetree.get_commit_spec("ch13l001"))
            )

        while self.pos < len(self.listings):
            print(self.pos, self.listings[self.pos].type)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff()


if __name__ == "__main__":
    unittest.main()
