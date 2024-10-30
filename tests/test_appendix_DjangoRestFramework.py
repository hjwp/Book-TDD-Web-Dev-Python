#!/usr/bin/env python3
import unittest

from book_tester import ChapterTest


class AppendixVIITest(ChapterTest):
    chapter_name = 'appendix_DjangoRestFramework'
    previous_chapter = 'appendix_rest_api'

    def test_listings_and_commands_and_output(self):
        self.parse_listings()
        self.start_with_checkout()
        self.prep_virtualenv()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'other command')
        self.assertEqual(self.listings[1].type, 'code listing')

        # skips
        #self.skip_with_check(22, 'switch back to master') # comment

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 40
            self.sourcetree.run_command('git switch {}'.format(
                self.sourcetree.get_commit_spec('ch36l027')
            ))

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        # TODO:
        # self.sourcetree.patch_from_commit('ch37l015')
        # self.sourcetree.patch_from_commit('ch37l017')
        # self.sourcetree.run_command(
        #    'git add . && git commit -m"final commit in rest api chapter"'
        #)


if __name__ == '__main__':
    unittest.main()
