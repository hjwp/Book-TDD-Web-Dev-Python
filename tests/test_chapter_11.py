#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_tester import ChapterTest

class Chapter11Test(ChapterTest):
    chapter_no = 11

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing')
        self.assertEqual(self.listings[1].type, 'code listing')
        self.assertEqual(self.listings[2].type, 'output')

        self.sourcetree.start_with_checkout(self.chapter_no)
        # other prep
        self.sourcetree.run_command('mkdir ../database')
        self.sourcetree.run_command('python3 manage.py syncdb --noinput')

        # skips
        self.skip_with_check(31, '# review changes') # diff

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 49
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch11l022')
            ))


        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no, ignore_moves=True)


if __name__ == '__main__':
    unittest.main()
