#!/usr/bin/env python3
import os
import unittest

from book_tester import ChapterTest


class Chapter20Test(ChapterTest):
    chapter_name = "chapter_22_fixtures_and_wait_decorator"
    previous_chapter = "chapter_21_mocking_2"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "code listing with git ref")
        self.assertEqual(self.listings[1].type, "other command")
        self.assertEqual(self.listings[2].type, "output")

        # skips
        # self.skip_with_check(22, 'switch back to master') # comment

        # prep
        self.start_with_checkout()
        self.prep_database()

        # hack fast-forward
        if os.environ.get("SKIP"):
            self.pos = 10
            self.sourcetree.run_command(
                "git switch {}".format(self.sourcetree.get_commit_spec("ch17l004"))
            )

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)

        self.sourcetree.tidy_up_after_patches()
        self.sourcetree.run_command('git add . && git commit -m"final commit ch17"')
        self.check_final_diff(ignore=["moves"])


if __name__ == "__main__":
    unittest.main()
