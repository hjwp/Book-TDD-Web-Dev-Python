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
        #listings[6]

        self.write_to_file(listings[7])
        all_unit_tests = self.run_command(listings[8])
        self.assert_console_output_correct(all_unit_tests, listings[9])

        self.assert_all_listings_checked(listings)


if __name__ == '__main__':
    unittest.main()
