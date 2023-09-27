#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import subprocess

from book_tester import ChapterTest, DO_SERVER_COMMANDS


class Chapter9Test(ChapterTest):
    chapter_name = 'chapter_09_docker'
    previous_chapter = 'chapter_08_prettification'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing with git ref')
        self.assertEqual(self.listings[1].type, 'test')

        self.start_with_checkout()

        # skips
        self.skip_with_check(13, 'replace the URL in the next line with')
        self.skip_with_check(24, 'do some git config first')
        self.skip_with_check(33, 'Performing system checks')
        self.skip_with_check(44, 'Starting development server')

        if not DO_SERVER_COMMANDS:
            self.skip_with_check(38, 'curl superlists-staging.ottg.eu')
            self.skip_with_check(39, 'Failed to connect to superlists-staging.ottg.eu')
            self.skip_with_check(47, 'curl superlists-staging.ottg.eu:8000')
            self.skip_with_check(48, '<!DOCTYPE html>')

        vm_restore = None # 'MANUAL_1'

        # hack fast-forward
        skip = False
        if skip:
            # self.pos = 8
            # self.sourcetree.run_command('git checkout {0}'.format(
            #     self.sourcetree.get_commit_spec('ch08l001')
            # ))
            self.pos = 43
            self.current_server_cd = '~/sites/$SITENAME'
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch08l004')
            ))
            vm_restore = 'MANUAL_2'

        if DO_SERVER_COMMANDS:
            if vm_restore:
                subprocess.check_call(['vagrant', 'snapshot', 'restore', vm_restore])
            else:
                subprocess.check_call(['vagrant', 'destroy', '-f'])
                subprocess.check_call(['vagrant', 'up'])

        while self.pos < len(self.listings):
            listing = self.listings[self.pos]
            print(self.pos, listing.type, repr(listing))
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff()
        if DO_SERVER_COMMANDS:
            subprocess.run(['vagrant', 'snapshot', 'delete', 'MANUAL_END'])
            subprocess.run(['vagrant', 'snapshot', 'save', 'MANUAL_END'], check=True)



if __name__ == '__main__':
    unittest.main()
