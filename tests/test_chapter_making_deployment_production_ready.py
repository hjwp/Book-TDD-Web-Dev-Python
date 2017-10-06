#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_tester import ChapterTest
LOCAL = False

class Chapter9bTest(ChapterTest):
    chapter_name = 'chapter_making_deployment_production_ready'
    previous_chapter = 'chapter_manual_deployment'


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'server command')
        self.assertEqual(self.listings[3].skip, True)

        self.start_with_checkout()

        # skips
        self.skip_with_check(36, 'git status')
        self.skip_with_check(37, 'see three new files')


        # hack fast-forward
        skip = False
        if skip:
            self.pos = 42
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch08l003')
            ))

        while self.pos < len(self.listings):
            listing = self.listings[self.pos]
            print(self.pos, listing.type, repr(listing))
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(ignore=["gunicorn==19"])


if __name__ == '__main__':
    unittest.main()
