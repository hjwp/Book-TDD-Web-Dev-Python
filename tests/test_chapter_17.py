#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest

class Chapter17Test(ChapterTest):
    chapter_name = 'chapter_17'
    previous_chapter = 'chapter_16'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.sourcetree.start_with_checkout(self.previous_chapter)

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing')
        self.assertEqual(self.listings[1].type, 'code listing')
        self.assertEqual(self.listings[2].type, 'test')

        # skips
        #self.skip_with_check(22, 'switch back to master') # comment

        self.prep_virtualenv()
        self.prep_database()
        self.sourcetree.run_command('rm accounts/tests.py')

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 100
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch16l047')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)

        # tidy up any .origs from patches
        self.check_final_diff(ignore=["moves"])


if __name__ == '__main__':
    unittest.main()
