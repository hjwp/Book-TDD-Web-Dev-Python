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
        listings = [p for n in listings_nodes for p in parse_listing(n)]

        # sanity checks
        self.assertEqual(type(listings[0]), Command)
        self.assertEqual(type(listings[1]), Output)
        self.assertEqual(type(listings[2]), CodeListing)

        self.start_with_checkout(3)

        self.run_command(listings[0])

        listings[1] = self.assert_directory_tree_correct(listings[1])

        # this listing just shows what's on disk by default
        with open(os.path.join(self.tempdir, 'superlists', listings[2].filename)) as f:
            self.assertMultiLineEqual(f.read().strip(), listings[2].contents.strip())
            listings[2].was_written = True

        self.write_to_file(listings[3])

        unit_test = self.run_command(listings[4])
        self.assert_console_output_correct(unit_test, listings[5])

        # next listing involves lots of line-length hackery. to be fixed...
        listings[6].was_written = True #TODO

        self.write_to_file(listings[7])
        all_unit_tests = self.run_command(listings[8])
        #self.assert_console_output_correct(all_unit_tests, listings[9])
        #TODO - fix this, stdout/stderr problems plus chatter

        unit_tests = self.run_command(listings[10])
        self.assert_console_output_correct(unit_tests, listings[11])

        self.write_to_file(listings[12])

        unit_tests = self.run_command(listings[13])
        self.assert_console_output_correct(unit_tests, listings[14])

        git_status = self.run_command(listings[15])
        self.assertIn('superlists/settings.py', git_status)
        self.assertIn('lists/', git_status)
        listings[16].was_checked = True
        self.run_command(listings[17])
        self.run_command(listings[18])
        git_diff = self.run_command(listings[19])
        self.assertIn('1 + 1, 3', git_diff)
        listings[20].was_checked = True

        commit = self.run_command(listings[21])
        self.assertIn('insertions', commit)

        self.write_to_file(listings[22])

        test_run = self.run_command(listings[23])
        self.assert_console_output_correct(test_run, listings[24])

        self.write_to_file(listings[25])

        test_run = self.run_command(listings[26])
        self.assert_console_output_correct(test_run, listings[27])

        self.write_to_file(listings[29])

        test_run = self.run_command(listings[26])  # TODO - retrieve from text
        self.assert_console_output_correct(test_run, listings[30])

        self.write_to_file(listings[31])
        test_run = self.run_command(listings[26])
        self.assert_console_output_correct(test_run, listings[32])

        self.write_to_file(listings[33])
        test_run = self.run_command(listings[26])
        self.assert_console_output_correct(test_run, listings[34])

        self.assert_all_listings_checked(listings)


if __name__ == '__main__':
    unittest.main()
