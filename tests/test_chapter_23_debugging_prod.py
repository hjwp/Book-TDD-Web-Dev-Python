#!/usr/bin/env python3.7
import unittest

from book_tester import ChapterTest


class Chapter18Test(ChapterTest):
    chapter_name = "chapter_23_debugging_prod"
    previous_chapter = "chapter_22_fixtures_and_wait_decorator"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "docker run tty")
        self.assertEqual(self.listings[1].type, "output")

        # skips
        self.skip_with_check(1, "naming to docker")

        # self.replace_command_with_check(
        #     13,
        #     "EMAIL_PASSWORD=yoursekritpasswordhere",
        #     "EMAIL_PASSWORD=" + os.environ["EMAIL_PASSWORD"],
        # )

        # deploy_pos = 49
        # assert "ansible-playbook" in self.listings[deploy_pos]

        # prep
        self.start_with_checkout()
        self.prep_database()
        self.sourcetree.run_command("touch container.db.sqlite3")
        self.sourcetree.run_command("sudo chown 1234 container.db.sqlite3")
        # for macos, see chap 10
        self.sourcetree.run_command("sudo chmod g+rw container.db.sqlite3")

        # vm_restore = "FABRIC_END"

        # hack fast-forward
        self.skip_forward_if_skipto_set()

        # if DO_SERVER_COMMANDS:
        #     subprocess.check_call(["vagrant", "snapshot", "restore", vm_restore])

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)

        self.sourcetree.tidy_up_after_patches()
        self.sourcetree.run_command('git add . && git commit -m"final commit ch17"')
        self.check_final_diff(ignore=["moves", "YAHOO_PASSWORD"])
        # if DO_SERVER_COMMANDS:
        #     subprocess.check_call(["vagrant", "snapshot", "save", "SERVER_DEBUGGED"])


if __name__ == "__main__":
    unittest.main()
