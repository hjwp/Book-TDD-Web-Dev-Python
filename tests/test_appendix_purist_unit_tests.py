#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class Chapter20Test(ChapterTest):
    chapter_name = 'appendix_purist_unit_tests'
    previous_chapter = 'chapter_22_outside_in'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'other command')
        self.assertEqual(self.listings[1].type, 'output')
        self.assertEqual(self.listings[4].type, 'code listing currentcontents')

        # skips
        self.skip_with_check(1, '# a branch')  # comment
        self.skip_with_check(109, '# optional backup')  # comment
        self.skip_with_check(112, '# reset master')  # comment

        # prep
        self.start_with_checkout()

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 75
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch19l041')
            ))

        while self.pos < len(self.listings):
            print(self.pos, self.listings[self.pos].type)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(ignore=["moves"])



if __name__ == '__main__':
    unittest.main()
