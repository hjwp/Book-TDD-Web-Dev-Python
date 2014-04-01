#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest

class Chapter13Test(ChapterTest):
    chapter_no = 13

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'other command')
        self.assertEqual(self.listings[1].type, 'output')
        self.assertEqual(self.listings[2].type, 'code listing with git ref')
        self.skip_with_check(48, 'needs the -f')
        self.skip_with_check(51, 'git push -f origin')
        fab_pos = 37
        assert 'fab' in self.listings[fab_pos]

        # skips
        #self.skip_with_check(30, '# review changes') # diff

        #prep
        self.sourcetree.start_with_checkout(self.chapter_no)
        self.prep_virtualenv()
        self.prep_database()
        self.sourcetree.run_command('git fetch --tags repo')

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 37
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch12l015')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
