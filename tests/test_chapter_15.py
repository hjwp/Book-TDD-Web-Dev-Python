#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest

class Chapter15Test(ChapterTest):
    chapter_no = 15

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.sourcetree.start_with_checkout(self.chapter_no)

        # sanity checks
        self.assertEqual(self.listings[0].type, 'other command')
        self.assertEqual(self.listings[1].type, 'code listing with git ref')
        self.assertEqual(self.listings[2].type, 'code listing with git ref')
        #self.assertTrue(self.listings[88].dofirst)

        # skips
        self.skip_with_check(22, 'switch back to master') # comment
        self.skip_with_check(24, 'remove any trace') # comment

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 86
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch15l047')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        # fix incomplete moves from dofirst-ch14l019
        # self.sourcetree.run_command('git rm lists/static/base.css')
        # self.sourcetree.run_command('git rm -r lists/static/bootstrap')
        # self.sourcetree.run_command('git rm lists/static/tests/qunit.css')
        # self.sourcetree.run_command('git rm lists/static/tests/qunit.js')

        # and from the diff-version of settings.py
        # self.sourcetree.run_command('rm superlists/settings.py.orig')

        # tidy up any .origs from patches
        self.sourcetree.run_command('find . -name \*.orig -exec rm {} \;')
        # and do a final commit
        self.sourcetree.run_command('git add . && git commit -m"final commit"')
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
