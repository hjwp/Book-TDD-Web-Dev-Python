#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import time

from book_tester import ChapterTest

class Chapter9Test(ChapterTest):
    chapter_no = 9

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
        self.listings[47].skip = True # example code we won't use
        self.listings[64].skip = True # example code we won't use
        self.listings[88].skip = True # DONTify
        self.listings[94].skip = True # example code
        self.listings[95].skip = True # example code
        self.listings[98].skip = True # print debugging
        self.listings[99].skip = True # print debugging
        self.listings[120].skip = True # git comment
        self.listings[138].skip = True # git comment

        # hack fast-forward
        skip = True
        if skip:
            self.pos = 147
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch09l054')
            ))

        while self.pos < 114:
            print(self.pos)
            self.recognise_listing_and_process_it()

        # revert a little hacky test thing
        self.sourcetree.run_command('git checkout -- lists/models.py')

        while self.pos < 200:
            print(self.pos)
            self.recognise_listing_and_process_it()


        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
