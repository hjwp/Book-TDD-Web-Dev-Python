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

class Chapter2Test(ChapterTest):

    def start_with_checkout(self):
        local_repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../source/chapter_2/superlists'))
        self.run_command(Command('mkdir superlists'), cwd=self.tempdir)
        self.run_command(Command('git init .'))
        self.run_command(Command('git remote add repo %s' % (local_repo_path,)))
        self.run_command(Command('git fetch repo'))
        self.run_command(Command('git checkout chapter_1_end'))


    def test_listings_and_commands_and_output(self):
        chapter_2 = parsed_html.cssselect('div.sect1')[2]
        listings_nodes = chapter_2.cssselect('div.listingblock')
        listings = [p for n in listings_nodes for p in parse_listing(n)]

        # sanity checks
        self.assertEqual(type(listings[0]), CodeListing)
        self.assertEqual(type(listings[1]), Output)
        self.assertEqual(type(listings[2]), Command)

        self.start_with_checkout()

        self.write_to_file(listings[0])

        # listings 1 is an aside

        runserver_output = self.run_command(listings[2])
        first_output = self.run_command(listings[3])
        self.assert_console_output_correct(first_output, listings[4])

        # listings 5 is an aside

        self.write_to_file(listings[6])

        second_ft_run = self.run_command(listings[7])
        self.assert_console_output_correct(second_ft_run, listings[8])


        for i, listing in enumerate(listings):
            if type(listing) == CodeListing:
                self.assertTrue(
                    listing.was_written,
                    'Listing %d not written:\n%s' % (i, listing)
                )
            if type(listing) == Command:
                self.assertTrue(
                    listing.was_run,
                    'Command %d not run:\n%s' % (i, listing)
                )
            if type(listing) == Output:
                self.assertTrue(
                    listing.was_checked,
                    'Output %d not checked:\n%s' % (i, listing)
                )




if __name__ == '__main__':
    unittest.main()
