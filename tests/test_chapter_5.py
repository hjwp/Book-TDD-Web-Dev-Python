# -*- coding: utf-8 -*-
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
    Output,
    parsed_html,
    parse_listing,
)

class Chapter5Test(ChapterTest):

    def test_listings_and_commands_and_output(self):
        chapter_5 = parsed_html.cssselect('div.sect1')[5]
        listings_nodes = chapter_5.cssselect('div.listingblock')
        self.listings = [p for n in listings_nodes for p in parse_listing(n)]

        # sanity checks
        self.assertEqual(type(self.listings[0]), CodeListing)
        self.assertEqual(type(self.listings[1]), Command)
        self.assertEqual(type(self.listings[2]), Output)

        self.start_with_checkout(5)
        self.start_dev_server()

        # skips
        self.listings[58].skip = True
        self.listings[67].skip = True

        while self.pos < 76:
            print self.pos
            self.recognise_listing_and_process_it()

        self.check_final_diff(5)
        self.assert_all_listings_checked(self.listings)


if __name__ == '__main__':
    unittest.main()
