#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest

class Chapter13Test(ChapterTest):
    chapter_no = 13

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.sourcetree.start_with_checkout(self.chapter_no)

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing')
        self.assertEqual(self.listings[1].type, 'code listing with git ref')
        self.assertEqual(self.listings[2].type, 'code listing with git ref')

        # skips
        #self.skip_with_check(30, '# review changes') # diff

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 5
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch13l004')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.sourcetree.run_command('git add . && git commit -m"final commit"')
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
