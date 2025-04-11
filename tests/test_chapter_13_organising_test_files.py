#!/usr/bin/env python3
import os
import unittest

from book_tester import ChapterTest


class Chapter13Test(ChapterTest):
    chapter_name = "chapter_13_organising_test_files"
    previous_chapter = "chapter_12_ansible"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "code listing with git ref")
        self.assertEqual(self.listings[1].type, "code listing with git ref")
        self.assertEqual(self.listings[2].type, "test")

        # other prep
        self.start_with_checkout()
        self.prep_database()

        # hack fast-forward
        if os.environ.get("SKIP"):
            self.pos = 6
            self.sourcetree.run_command(
                f"git checkout {self.sourcetree.get_commit_spec('ch13l002')}"
            )

        while self.pos < len(self.listings):
            print(self.pos, self.listings[self.pos].type)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(
            ignore=[
                # "django==1.11"
            ]
        )


if __name__ == "__main__":
    unittest.main()
