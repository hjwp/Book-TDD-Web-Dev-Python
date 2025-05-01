#!/usr/bin/env python3
import os
import unittest

from book_tester import ChapterTest


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
        # self.sourcetree.run_command("mkdir -p static/stuff")

        # skips
        self.skip_with_check(46, "should show dockerfile")
        self.skip_with_check(49, "should now be clean")
        self.skip_with_check(54, "otherwise")

        # vm_restore = "MANUAL_END"

        # hack fast-forward
        if target_listing := os.environ.get("SKIPTO"):
            self.sourcetree.run_command("uv pip install gunicorn whitenoise")
            commit_spec = self.sourcetree.get_commit_spec(target_listing)
            while True:
                listing = self.listings[self.pos]
                found = False
                if getattr(listing, "commit_ref", None) == target_listing:
                    found = True
                    print("Skipping to pos", self.pos)
                    self.sourcetree.run_command(f"git checkout {commit_spec}")
                    break
                self.pos += 1
            if not found:
                raise Exception(f"Could not find {target_listing}")

        # if DO_SERVER_COMMANDS:
        #     subprocess.check_call(["vagrant", "snapshot", "restore", vm_restore])
        # self.current_server_cd = "~/sites/$SITENAME"

        while self.pos < len(self.listings):
            listing = self.listings[self.pos]
            print(self.pos, listing.type, repr(listing))
            self.recognise_listing_and_process_it()

        self.check_final_diff(
            ignore=[
                "Django==5.1",
                "gunicorn==2",
                "whitenoise==6.",
            ]
        )
        self.assert_all_listings_checked(self.listings)


if __name__ == "__main__":
    unittest.main()
