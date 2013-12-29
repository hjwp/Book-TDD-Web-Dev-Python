#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest

class Chapter14Test(ChapterTest):
    chapter_no = 14

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.sourcetree.start_with_checkout(self.chapter_no)

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing with git ref')
        self.assertEqual(self.listings[1].type, 'code listing with git ref')
        self.assertEqual(self.listings[2].type, 'other command')
        self.assertTrue(self.listings[87].dofirst)

        # skips
        self.skip_with_check(22, 'switch back to master') # comment
        self.skip_with_check(24, 'remove any trace') # comment
        self.skip_with_check(26, 'new FT') # comment

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 84
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch14l046')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.sourcetree.run_command('git add . && git commit -m"final commit"')
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
