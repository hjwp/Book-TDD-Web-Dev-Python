#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class Chapter20Test(ChapterTest):
    chapter_no = 20

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.sourcetree.start_with_checkout(self.chapter_no)
        #self.prep_virtualenv()

        # sanity checks
        self.assertEqual(self.listings[0].skip, True)
        self.assertEqual(self.listings[1].skip, True)
        self.assertEqual(self.listings[11].type, 'code listing with git ref')

        # skips
        #self.skip_with_check(22, 'switch back to master') # comment

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 35
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch19l016')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no, ignore_moves=True)


if __name__ == '__main__':
    unittest.main()
