#!/usr/bin/env python3.7
import os
import unittest

from book_tester import DO_SERVER_COMMANDS, ChapterTest


class Chapter18Test(ChapterTest):
    chapter_name = "chapter_21_server_side_debugging"
    previous_chapter = "chapter_20_fixtures_and_wait_decorator"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "against staging")
        self.assertEqual(self.listings[1].type, "output")

        # skips
        # self.skip_with_check(45, "commit changes first")
        if DO_SERVER_COMMANDS:
            self.replace_command_with_check(
                13,
                "EMAIL_PASSWORD=yoursekritpasswordhere",
                "EMAIL_PASSWORD=" + os.environ["EMAIL_PASSWORD"],
            )

        # deploy_pos = 49
        # assert "ansible-playbook" in self.listings[deploy_pos]

        # prep
        self.start_with_checkout()
        self.prep_database()

        # vm_restore = "FABRIC_END"

        # hack fast-forward
        if os.environ.get("SKIP"):
            self.pos = 10
            self.sourcetree.run_command(
                "git checkout {}".format(self.sourcetree.get_commit_spec("ch17l004"))
            )

        # if DO_SERVER_COMMANDS:
        #     subprocess.check_call(["vagrant", "snapshot", "restore", vm_restore])

        while self.pos < len(self.listings):
            print(self.pos)
            # if self.pos == deploy_pos + 1 and DO_SERVER_COMMANDS:
            #     print("hacking in code update on server")
            #     self.run_server_command(
            #         "cd /home/elspeth/sites/staging.ottg.co.uk"
            #         " && git checkout chapter_21_server_side_debugging"
            #         " && git reset --hard origin/chapter_21_server_side_debugging",
            #     )
            #     self.run_server_command(
            #         "sudo systemctl restart gunicorn-staging.ottg.co.uk"
            #     )
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)

        self.sourcetree.tidy_up_after_patches()
        self.sourcetree.run_command('git add . && git commit -m"final commit ch17"')
        self.check_final_diff(ignore=["moves", "YAHOO_PASSWORD"])
        # if DO_SERVER_COMMANDS:
        #     subprocess.check_call(["vagrant", "snapshot", "save", "SERVER_DEBUGGED"])


if __name__ == "__main__":
    unittest.main()
