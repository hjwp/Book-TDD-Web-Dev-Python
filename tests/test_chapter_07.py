#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_parser import Command, Output
from book_tester import ChapterTest

class Chapter7Test(ChapterTest):
    chapter_no = 7

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing with git ref')
        self.assertEqual(type(self.listings[1]), Command)
        self.assertEqual(type(self.listings[2]), Output)

        self.sourcetree.start_with_checkout(self.chapter_no)
        # other prep
        self.sourcetree.run_command('python3 manage.py syncdb --noinput')

        # skips
        self.skip_with_check(23, 'the -b means ignore whitespace')
        self.skip_with_check(26, 'leave static, for now')
        self.skip_with_check(49, 'will now show all the bootstrap')

        while self.pos < 31:
            print(self.pos)
            self.recognise_listing_and_process_it()

        settings = self.sourcetree.get_contents('superlists/settings.py')
        assert self.listings[31].filename == 'superlists/settings.py'
        for line in self.listings[31].contents.split('\n'):
            assert line in settings
        self.listings[31].skip = True

        while self.pos < 51:
            print(self.pos)
            self.recognise_listing_and_process_it()

        settings = self.sourcetree.get_contents('superlists/settings.py')
        assert self.listings[51].filename == 'superlists/settings.py'
        for line in self.listings[51].contents.split('\n'):
            assert line in settings
        self.listings[51].skip = True
        self.listings[52].skip = True # tree showing where static will go

        #import time
        #print(self.tempdir)
        #time.sleep(200)
        while self.pos < 62:
            print(self.pos)
            self.recognise_listing_and_process_it()


        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
