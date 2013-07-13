#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
    Output,
    parsed_html,
    parse_listing,
)

class Chapter3Test(ChapterTest):

    def test_listings_and_commands_and_output(self):
        chapter_3 = parsed_html.cssselect('div.sect1')[3]
        listings_nodes = chapter_3.cssselect('div.listingblock')
        self.listings = [p for n in listings_nodes for p in parse_listing(n)]

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Output)
        self.assertEqual(type(self.listings[2]), CodeListing)

        self.start_with_checkout(3)

        self.run_command(self.listings[0])

        self.listings[1] = self.assert_directory_tree_correct(self.listings[1])

        # this listing just shows what's on disk by default
        with open(os.path.join(self.tempdir, 'superlists', self.listings[2].filename)) as f:
            self.assertMultiLineEqual(f.read().strip(), self.listings[2].contents.strip())
            self.listings[2].was_written = True

        self.check_test_code_cycle(3)

        # next listing also just shows whats on disk in settings.py by default,
        # involves lots of line-length hackery. to be fixed...
        self.listings[6].was_written = True #TODO

        self.write_to_file(self.listings[7])
        all_check_test_code_cycle = self.run_command(self.listings[8])
        #self.assert_console_output_correct(all_unit_tests, self.listings[9])
        #TODO - fix this, stdout/stderr problems plus chatter
        self.listings[9].was_checked = True

        unit_tests = self.run_command(self.listings[10])
        self.assert_console_output_correct(unit_tests, self.listings[11])

        self.check_test_code_cycle(12)

        git_status = self.run_command(self.listings[15])
        self.assertIn('superlists/settings.py', git_status)
        self.assertIn('lists/', git_status)
        self.listings[16].was_checked = True

        self.run_command(self.listings[17])
        self.run_command(self.listings[18])

        git_diff = self.run_command(self.listings[19])
        self.assertIn('1 + 1, 3', git_diff)
        self.listings[20].was_checked = True
        commit = self.run_command(self.listings[21])
        self.assertIn('insertions', commit)

        self.check_test_code_cycle(22)

        self.check_test_code_cycle(25)
        self.assertEqual(self.listings[26], 'python3 manage.py test lists') # sanity check

        current_contents = self.run_command(Command('cat ' + self.listings[28].filename))
        self.assertMultiLineEqual(current_contents.strip(), self.listings[28].contents.strip())
        self.listings[28].was_written = True

        # TODO - retrieve from text
        self.check_test_code_cycle(29, test_command_in_listings=False)
        self.check_test_code_cycle(31, test_command_in_listings=False)
        self.check_test_code_cycle(33)

        self.check_git_diff_and_commit(36)

        self.check_test_code_cycle(39, test_command_in_listings=False)
        print(self.listings[41].contents)
        self.check_test_code_cycle(41, test_command_in_listings=False)
        self.check_test_code_cycle(43, test_command_in_listings=False)
        self.check_test_code_cycle(45, test_command_in_listings=False)
        self.check_test_code_cycle(47, test_command_in_listings=False)
        self.check_test_code_cycle(49)

        self.run_command(Command('python3 manage.py runserver'))
        ft_run = self.run_command(self.listings[52])
        # TODO: fix this firefox/selenium socket error thing
        #self.assert_console_output_correct(ft_run, self.listings[53])
        self.listings[53].was_checked = True


        self.check_git_diff_and_commit(54)

        gitlog = self.run_command(self.listings[57])
        self.assert_console_output_correct(gitlog, self.listings[58])

        self.check_final_diff(3)
        self.assert_all_listings_checked(self.listings)


if __name__ == '__main__':
    unittest.main()
