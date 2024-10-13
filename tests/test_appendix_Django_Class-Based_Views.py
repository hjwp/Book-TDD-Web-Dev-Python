#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class AppendixIITest(ChapterTest):
    chapter_name = 'appendix_Django_Class-Based_Views'
    previous_chapter = 'chapter_16_advanced_forms'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.start_with_checkout()
        #self.prep_virtualenv()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing currentcontents')
        self.assertEqual(self.listings[1].type, 'code listing with git ref')
        self.assertEqual(self.listings[2].type, 'code listing with git ref')

        # skips
        #self.skip_with_check(22, 'switch back to master') # comment

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 27
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch20l015')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(ignore=["moves"])


if __name__ == '__main__':
    unittest.main()
