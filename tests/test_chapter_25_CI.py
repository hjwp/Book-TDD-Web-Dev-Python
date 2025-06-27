#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class Chapter25Test(ChapterTest):
    chapter_name = "chapter_25_CI"
    previous_chapter = "chapter_24_outside_in"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.start_with_checkout()
        # self.prep_virtualenv()

        # sanity checks
        self.assertEqual(self.listings[0].skip, True)
        self.assertEqual(self.listings[1].skip, True)
        self.assertEqual(self.listings[10].type, "code listing with git ref")

        # skips
        # self.skip_with_check(22, 'switch back to master') # comment

        # hack fast-forward
        self.skip_forward_if_skipto_set()

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.sourcetree.run_command(
            "git add .gitlab-ci.yml",
        )
        # TODO: test package.json
        # self.sourcetree.run_command(
        #     "git add src/lists/static/package.json src/lists/static/tests"
        # )
        self.sourcetree.run_command("git commit -m'final commit'")
        # self.check_final_diff(ignore=["moves"])


if __name__ == "__main__":
    unittest.main()
