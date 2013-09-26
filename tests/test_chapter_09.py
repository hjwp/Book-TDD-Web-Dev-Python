#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_tester import ChapterTest

class Chapter9Test(ChapterTest):
    chapter_no = 9

    def skip_with_check(self, pos, expected_content):
        listing = self.listings[pos]
        assert expected_content in listing
        listing.skip = True


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        print(self.listings[0])
        self.assertEqual(self.listings[0].type, 'code listing with git ref')
        self.assertEqual(self.listings[1].type, 'other command')

        self.sourcetree.start_with_checkout(self.chapter_no)
        # other prep
        self.sourcetree.run_command('mkdir ../database')
        self.sourcetree.run_command('python3 manage.py syncdb --noinput')

        # skips
        self.skip_with_check(159, '# should show new file') # example code


        # hack fast-forward
        skip = False
        if skip:
            self.pos = 187
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch09l066')
            ))

        while self.pos < 136:
            print(self.pos)
            self.recognise_listing_and_process_it()

        if not self.pos > 136:
            # revert a little hacky test thing
            self.sourcetree.run_command('git checkout -- lists/models.py')

        while self.pos < 174:
            print(self.pos)
            self.recognise_listing_and_process_it()

        if not self.pos > 176:
            # manually apply ch09l058, which touches 3 files
            self.sourcetree.run_command(
                'git checkout {0} -- .'.format(self.sourcetree.get_commit_spec('ch09l058'))
            )

        while self.pos < 178:
            print(self.pos)
            self.recognise_listing_and_process_it()

        # manually apply ch09l059, which touches several files
        if not self.pos > 158:
            self.sourcetree.run_command(
                'git checkout {0} -- .'.format(self.sourcetree.get_commit_spec('ch09l059'))
            )
            self.pos = 159

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
