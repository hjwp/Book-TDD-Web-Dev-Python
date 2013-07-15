#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from book_tester import (
    ChapterTest,
    Command,
)
from write_to_file import remove_function

class Chapter6Test(ChapterTest):
    chapter_no = 6

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Command)
        self.assertEqual(type(self.listings[2]), Command)

        self.start_with_checkout(self.chapter_no)
        #self.start_dev_server()

        # other prep
        self.run_command(Command('python3 manage.py syncdb --noinput'))

        # skips
        self.listings[18].skip = True


        while self.pos < 37:
            print(self.pos)
            self.recognise_listing_and_process_it()

        assert 'egrep' in self.listings[37]
        egrep = self.run_command(self.listings[37])
        self.assertCountEqual(egrep.strip().split('\n'), self.listings[38].split('\n'))
        self.listings[37].was_checked = True
        self.listings[38].was_checked = True
        self.pos = 39

        def remove_function_from(function_name, filename):
            with open(os.path.join(self.tempdir, filename)) as f:
                old_views = f.read()
            new_views = remove_function(old_views, function_name)
            with open(os.path.join(self.tempdir, filename), 'w') as f:
                f.write(new_views)

        remove_function_from(
            'test_home_page_displays_all_list_items',
            'superlists/lists/tests.py'
        )

        while self.pos < 43:
            print(self.pos)
            self.recognise_listing_and_process_it()

        # command followed by unrelated output
        self.run_command(self.listings[43])
        self.listings[43].was_checked = True
        self.pos = 44

        while self.pos < 52:
            print(self.pos)
            self.recognise_listing_and_process_it()

        assert 'git status' in self.listings[52]
        status = self.run_command(self.listings[52])
        self.assertIn('list.html', self.listings[53])
        self.assertIn('list.html', status)
        self.listings[52].was_checked = True
        self.listings[53].was_checked = True
        self.pos = 54

        self.listings[58].skip = True # irrelevant comment
        self.listings[59].skip = True # move function
        remove_function_from(
            'test_home_page_can_save_a_POST_request',
            'superlists/lists/tests.py'
        )

        self.listings[81].skip = True
        # at this point I ask the user to guess what she should
        # code, based only on outputs.
        # TODO: create code listings.
        # for now, just cheat and skip ahead.
        self.listings[82].skip = True
        self.listings[83].skip = True

        self.listings[88].skip = True # "decoding its traceback"

        while self.pos < 999:
            print(self.pos)
            self.recognise_listing_and_process_it()



        self.check_final_diff(self.chapter_no)
        self.assert_all_listings_checked(self.listings)


if __name__ == '__main__':
    unittest.main()
