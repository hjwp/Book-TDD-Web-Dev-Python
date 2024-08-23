#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class Chapter22Test(ChapterTest):
    chapter_name = 'chapter_24_page_pattern'
    previous_chapter = 'chapter_23_CI'


    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.start_with_checkout()
        #self.prep_virtualenv()

        # sanity checks
        # self.assertEqual(self.listings[0].type, 'code listing')
        self.assertEqual(self.listings[0].type, 'code listing with git ref')
        self.assertEqual(self.listings[1].type, 'test')
        self.assertEqual(self.listings[2].type, 'output')

        # skips
        #self.skip_with_check(22, 'switch back to master') # comment

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 23
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch18l011')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)

        self.sourcetree.tidy_up_after_patches()
        # final branch includes a suggested implementation...
        # so just check diff up to the last listing
        commit = self.sourcetree.get_commit_spec('ch22l013')
        diff = self.sourcetree.run_command(
            'git diff -b {}'.format(commit)
        )
        self.check_final_diff(ignore=["moves"], diff=diff)


if __name__ == '__main__':
    unittest.main()
