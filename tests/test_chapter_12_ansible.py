#!/usr/bin/env python3
import os
import unittest

from book_tester import ChapterTest


class Chapter12Test(ChapterTest):
    chapter_name = "chapter_12_ansible"
    previous_chapter = "chapter_11_server_prep"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "code listing with git ref")
        self.assertEqual(self.listings[1].type, "against staging")

        self.start_with_checkout()
        self.prep_virtualenv()
        self.prep_database()
        # self.sourcetree.run_command('mkdir -p static/stuff')

        # skips
        self.skip_with_check(62, "git diff")
        self.skip_with_check(63, "should show our changes")

        # vm_restore = 'MANUAL_END'

        # hack fast-forward
        if os.environ.get("SKIP"):
            self.pos = 42
            self.sourcetree.run_command(
                f"git switch {self.sourcetree.get_commit_spec('ch08l003')}"
            )

        # if DO_SERVER_COMMANDS:
        #     subprocess.check_call(['vagrant', 'snapshot', 'restore', vm_restore])
        #
        # self.current_server_cd = '~/sites/$SITENAME'

        while self.pos < len(self.listings):
            listing = self.listings[self.pos]
            print(self.pos, listing.type, repr(listing))
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(ignore=["gunicorn==19"])
        # if DO_SERVER_COMMANDS:
        #     subprocess.run(['vagrant', 'snapshot', 'delete', 'MAKING_END'], check=False)
        #     subprocess.run(['vagrant', 'snapshot', 'save', 'MAKING_END'], check=True)
        #


if __name__ == "__main__":
    unittest.main()
