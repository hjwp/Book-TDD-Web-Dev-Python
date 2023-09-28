#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import subprocess

from book_tester import ChapterTest, DO_SERVER_COMMANDS



class Chapter9bTest(ChapterTest):
    chapter_name = 'chapter_10_ansible'
    previous_chapter = 'chapter_manual_deployment'


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'server command')
        self.assertEqual(self.listings[2].type, 'against staging')

        self.start_with_checkout()
        self.sourcetree.run_command('mkdir -p static/stuff')

        # skips
        self.skip_with_check(8, 'check our symlink')
        self.skip_with_check(19, 'Starting gunicorn')
        self.skip_with_check(41, 'something more secure later')
        self.skip_with_check(70, 'this command tells Systemd')
        self.skip_with_check(72, 'this command actually starts')
        self.skip_with_check(85, 'git status')
        self.skip_with_check(86, 'see three new files')

        # fixes
        self.replace_command_with_check(
            39,
            'git pull',
            'git fetch'
            ' && git checkout chapter_10_ansible'
            ' && git reset --hard origin/chapter_10_ansible',
        )

        vm_restore = 'MANUAL_END'

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 42
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch08l003')
            ))

        if DO_SERVER_COMMANDS:
            subprocess.check_call(['vagrant', 'snapshot', 'restore', vm_restore])

        self.current_server_cd = '~/sites/$SITENAME'

        while self.pos < len(self.listings):
            listing = self.listings[self.pos]
            print(self.pos, listing.type, repr(listing))
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(ignore=["gunicorn==19"])
        if DO_SERVER_COMMANDS:
            subprocess.run(['vagrant', 'snapshot', 'delete', 'MAKING_END'])
            subprocess.run(['vagrant', 'snapshot', 'save', 'MAKING_END'], check=True)


if __name__ == '__main__':
    unittest.main()
