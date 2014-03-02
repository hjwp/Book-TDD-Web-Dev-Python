#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class Chapter17Test(ChapterTest):
    chapter_no = 17

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.sourcetree.start_with_checkout(self.chapter_no)
        self.sourcetree.run_command('mkdir -p ../database')
        self.sourcetree.run_command('python3 manage.py syncdb --migrate --noinput')

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing')
        self.assertEqual(self.listings[1].type, 'code listing with git ref')
        self.assertEqual(self.listings[2].type, 'code listing with git ref')

        # skips
        #self.skip_with_check(22, 'switch back to master') # comment

        self.sourcetree.run_command('rm accounts/tests.py')

        # hack fast-forward
        skip = True
        if skip:
            self.pos = 10
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch17l004')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
