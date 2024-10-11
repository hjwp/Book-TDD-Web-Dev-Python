#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class AppendixVITest(ChapterTest):
    chapter_name = 'appendix_rest_api'
    previous_chapter = 'chapter_25_page_pattern'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.start_with_checkout()
        # self.prep_virtualenv()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing')
        self.assertEqual(self.listings[1].type, 'code listing')

        # skips
        #self.skip_with_check(22, 'switch back to master') # comment

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 40
            self.sourcetree.run_command('git checkout {}'.format(
                self.sourcetree.get_commit_spec('ch36l027')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.sourcetree.run_command(
            'git add . && git commit -m"final commit in rest api chapter"'
        )
        self.check_final_diff()


if __name__ == '__main__':
    unittest.main()
