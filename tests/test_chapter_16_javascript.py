#!/usr/bin/env python3
import os
import unittest

from book_tester import ChapterTest


class Chapter16Test(ChapterTest):
    chapter_name = "chapter_16_javascript"
    previous_chapter = "chapter_15_advanced_forms"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        # self.fail('\n'.join(f'{i}: {l.type} -- {l}' for i, l in enumerate(self.listings)))
        self.start_with_checkout()

        # sanity checks
        self.assertEqual(self.listings[0].type, "code listing with git ref")
        self.assertEqual(self.listings[1].type, "test")
        self.assertEqual(self.listings[2].type, "output")

        # skip some inline bash comments
        self.skip_with_check(13, "if you're on Windows")
        self.skip_with_check(15, "delete all the other stuff")

        # hack fast-forward
        if os.environ.get("SKIP"):
            self.pos = 10
            self.sourcetree.run_command(
                "git checkout {}".format(self.sourcetree.get_commit_spec("ch16l004"))
            )

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.sourcetree.run_command('git add . && git commit -m"final commit"')
        self.check_final_diff()


if __name__ == "__main__":
    unittest.main()
