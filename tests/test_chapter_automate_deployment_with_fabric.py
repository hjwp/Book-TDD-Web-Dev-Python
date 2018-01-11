#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import subprocess

from book_tester import ChapterTest, DO_SERVER_COMMANDS


class Chapter9cTest(ChapterTest):
    chapter_name = 'chapter_automate_deployment_with_fabric'
    previous_chapter = 'chapter_making_deployment_production_ready'


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'other command')
        self.assertEqual(self.listings[1].skip, True)
        self.assertEqual(self.listings[2].type, 'code listing with git ref')
        if not DO_SERVER_COMMANDS:
            self.skip_with_check(9, 'fab deploy')
            self.skip_with_check(10, '[elspeth@superlists-staging.ottg.eu]')
            self.skip_with_check(12, 'fab deploy')
            self.skip_with_check(13, '[elspeth@superlists.ottg.eu]')

        self.start_with_checkout()

        vm_restore = 'MAKING_END'

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 42
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch08l003')
            ))

        if DO_SERVER_COMMANDS:
            subprocess.check_call(['vagrant', 'snapshot', 'restore', vm_restore])

        self.current_server_cd = '~/sites/superlists-staging.ottg.eu'

        while self.pos < len(self.listings):
            listing = self.listings[self.pos]
            print(self.pos, listing.type, repr(listing))
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff()
        if DO_SERVER_COMMANDS:
            subprocess.check_call(['vagrant', 'snapshot', 'save', 'FABRIC_END'])


if __name__ == '__main__':
    unittest.main()
