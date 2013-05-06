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

    def test_listings_and_commands_and_output(self):
        chapter_2 = parsed_html.cssselect('div.sect1')[2]
        listings_nodes = chapter_2.cssselect('div.listingblock')
        listings = [p for n in listings_nodes for p in parse_listing(n)]

        # sanity checks
        self.assertEqual(type(listings[0]), CodeListing)
        self.assertEqual(type(listings[1]), Output)
        self.assertEqual(type(listings[2]), Command)

        self.start_with_checkout(2)

        self.write_to_file(listings[0])

        # listings 1 is an aside

        runserver_output = self.run_command(listings[2])
        first_output = self.run_command(listings[3])
        self.assert_console_output_correct(first_output, listings[4])

        # listings 5 is an aside

        self.write_to_file(listings[6])

        second_ft_run = self.run_command(listings[7])
        self.assert_console_output_correct(second_ft_run, listings[8])

        self.write_to_file(listings[9])

        diff = self.run_command(listings[10])
        print diff
        self.assert_console_output_correct(diff, listings[11])

        commit = Command(listings[12] + 'm"first ft specced out in comments and now uses unittest"')
        self.run_command(commit)
        listings[12].was_run = True # TODO

        diff = self.run_command(Command('git diff -b repo/chapter_2'))
        self.assertEqual(diff, '')

        self.assert_all_listings_checked(listings, [1,5])




if __name__ == '__main__':
    unittest.main()
