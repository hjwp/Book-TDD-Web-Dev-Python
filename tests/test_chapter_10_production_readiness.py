#!/usr/bin/env python3
import os
import subprocess
import unittest
from pathlib import Path

from book_tester import ChapterTest

THIS_DIR = Path(__file__).parent


class Chapter10Test(ChapterTest):
    chapter_name = "chapter_10_production_readiness"
    previous_chapter = "chapter_09_docker"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "other command")
        self.assertEqual(self.listings[3].type, "docker run tty")

        self.start_with_checkout()
        self.prep_virtualenv()
        self.prep_database()

        # skips
        self.skip_with_check(47, "should show dockerfile")
        self.skip_with_check(50, "should now be clean")
        self.skip_with_check(55, "Change the owner")
        self.skip_with_check(57, "Change the file to be group-writeable as well")
        self.skip_with_check(61, "note container id")

        # hack fast-forward, nu way
        self.skip_forward_if_skipto_set()

        while self.pos < len(self.listings):
            listing = self.listings[self.pos]
            print(self.pos, listing.type, repr(listing))

            self.recognise_listing_and_process_it()

        self.check_final_diff(
            ignore=[
                "Django==5.2",
                "gunicorn==2",
                "whitenoise==6.",
            ]
        )
        self.assert_all_listings_checked(self.listings)


if __name__ == "__main__":
    unittest.main()
