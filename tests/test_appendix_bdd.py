#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class AppendixVTest(ChapterTest):
    chapter_name = 'appendix_bdd'
    previous_chapter = 'chapter_22_server_side_debugging'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.start_with_checkout()
        #self.prep_virtualenv()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'other command')
        self.assertEqual(self.listings[4].type, 'tree')
        self.assertEqual(self.listings[6].type, 'diff')
        self.assertEqual(self.listings[7].type, 'bdd test')

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
        self.sourcetree.run_command('git add . && git commit -m"final commit in bdd chapter"')
        self.check_final_diff()


if __name__ == '__main__':
    unittest.main()
