#!/usr/bin/env python3
import unittest
import subprocess

from book_tester import ChapterTest, DO_SERVER_COMMANDS


class Chapter9Test(ChapterTest):
    chapter_name = "chapter_09_docker"
    previous_chapter = "chapter_08_prettification"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "code listing with git ref")
        self.assertEqual(self.listings[1].type, "test")

        # skips
        self.skip_with_check(20, "naming to docker.io/library/superlists")
        self.skip_with_check(27, "naming to docker.io/library/superlists")

        self.start_with_checkout()
        # simulate having a db.sqlite3 and a static folder from previous chaps
        self.sourcetree.run_command("./manage.py migrate --noinput")
        self.sourcetree.run_command("./manage.py collectstatic --noinput")

        vm_restore = None  # 'MANUAL_1'

        # hack fast-forward
        skip = True
        if skip:
            self.pos = 8
            self.sourcetree.run_command(
                "git checkout {}".format(self.sourcetree.get_commit_spec("ch09l001"))
            )
            # vm_restore = "MANUAL_2"

        if DO_SERVER_COMMANDS:
            if vm_restore:
                subprocess.check_call(["vagrant", "snapshot", "restore", vm_restore])
            else:
                subprocess.check_call(["vagrant", "destroy", "-f"])
                subprocess.check_call(["vagrant", "up"])

        while self.pos < len(self.listings):
            if self.pos == 47:
                assert "curl -iv" in self.listings[self.pos]
                print('sleeping')
                # breakpoint()
                import time; time.sleep(1)

            listing = self.listings[self.pos]
            print(self.pos, listing.type, repr(listing))
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff()
        if DO_SERVER_COMMANDS:
            subprocess.run(["vagrant", "snapshot", "delete", "MANUAL_END"])
            subprocess.run(["vagrant", "snapshot", "save", "MANUAL_END"], check=True)


if __name__ == "__main__":
    unittest.main()
