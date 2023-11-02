#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from book_tester import ChapterTest

class Chapter12Test(ChapterTest):
    chapter_name = 'chapter_14_simple_form'
    previous_chapter = 'chapter_13_database_layer_validation'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing')
        self.assertEqual(self.listings[1].type, 'code listing')
        self.assertEqual(self.listings[2].type, 'output')

        # skips
        self.skip_with_check(29, '# review changes') # diff

        # prep
        self.start_with_checkout()
        self.prep_database()

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 59
            self.sourcetree.run_command('git checkout {}'.format(
                self.sourcetree.get_commit_spec('ch11l030')
            ))


        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(ignore=["moves"])


if __name__ == '__main__':
    unittest.main()
