#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import unittest
import subprocess

from book_tester import ChapterTest, DO_SERVER_COMMANDS


class Chapter9cTest(ChapterTest):
    chapter_name = 'chapter_11_ansible'
    previous_chapter = 'chapter_10_production_readiness'


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'other command')
        self.assertEqual(self.listings[1].skip, True)
        self.assertEqual(self.listings[2].type, 'code listing with git ref')

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
            subprocess.run(['vagrant', 'snapshot', 'delete', 'FABRIC_END'])
            subprocess.run(['vagrant', 'snapshot', 'save', 'FABRIC_END'], check=True)


if __name__ == '__main__':
    unittest.main()
