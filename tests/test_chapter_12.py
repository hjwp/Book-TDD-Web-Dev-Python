#!/usr/bin/env python3
import os
import unittest

from book_tester import ChapterTest

class Chapter12Test(ChapterTest):
    chapter_no = 12

    def prep_virtualenv(self):
        virtualenv_path = os.path.join(self.tempdir, 'virtualenv')
        if not os.path.exists(virtualenv_path):
            print('preparing virtualenv')
            self.sourcetree.run_command(
                'virtualenv --python=python3 ../virtualenv'
            )
            self.sourcetree.run_command(
                '../virtualenv/bin/pip install -r requirements.txt'
            )


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'other command')
        self.assertEqual(self.listings[1].type, 'output')
        self.assertEqual(self.listings[2].type, 'code listing with git ref')
        self.skip_with_check(47, 'needs the -f')
        self.skip_with_check(50, 'git push -f origin')
        fab_pos = 36
        assert 'fab' in self.listings[fab_pos]

        self.sourcetree.start_with_checkout(self.chapter_no)
        self.prep_virtualenv()
        self.sourcetree.run_command('mkdir ../database')
        self.sourcetree.run_command('python3 manage.py syncdb --noinput')

        # skips
        #self.skip_with_check(30, '# review changes') # diff

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 37
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch12l015')
            ))

        # while self.pos < fab_pos:
        #     print(self.pos)
        #     self.recognise_listing_and_process_it()

        # self.sourcetree.run_command('git stash')
        # self.sourcetree.run_command('git checkout repo/chapter_12^')
        # self.sourcetree.run_command('git stash pop')
        # self.recognise_listing_and_process_it()
        # self.sourcetree.run_command('git stash')
        # self.sourcetree.run_command('git checkout master')
        # self.sourcetree.run_command('git stash pop')

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
