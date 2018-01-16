#!/usr/bin/env python3.6
import os
import unittest
import subprocess

from book_tester import ChapterTest, DO_SERVER_COMMANDS


class Chapter18Test(ChapterTest):
    chapter_name = 'chapter_server_side_debugging'
    previous_chapter = 'chapter_fixtures_and_wait_decorator'


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'other command')
        self.assertEqual(self.listings[1].type, 'output')

        # skips
        self.skip_with_check(1, "if you haven't already")
        if DO_SERVER_COMMANDS:
            self.replace_command_with_check(
                13,
                "EMAIL_PASSWORD=yoursekritpasswordhere",
                "EMAIL_PASSWORD=" + os.environ['EMAIL_PASSWORD']
            )

        # prep
        self.start_with_checkout()
        self.prep_database()

        vm_restore = 'FABRIC_END'

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 10
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch17l004')
            ))

        if DO_SERVER_COMMANDS:
            subprocess.check_call(['vagrant', 'snapshot', 'restore', vm_restore])

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)

        # tidy up any .origs from patches
        self.sourcetree.run_command('find . -name \*.orig -exec rm {} \;')
        self.sourcetree.run_command('git add . && git commit -m"final commit ch17"')
        self.check_final_diff(ignore=["moves"])
        if DO_SERVER_COMMANDS:
            subprocess.check_call(['vagrant', 'snapshot', 'save', 'SERVER_DEBUGGED'])


if __name__ == '__main__':
    unittest.main()
