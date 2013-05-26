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

class Chapter4Test(ChapterTest):

    def test_listings_and_commands_and_output(self):
        chapter_4 = parsed_html.cssselect('div.sect1')[4]
        listings_nodes = chapter_4.cssselect('div.listingblock')
        self.listings = [p for n in listings_nodes for p in parse_listing(n)]

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Output)
        self.assertEqual(type(self.listings[2]), CodeListing)

        self.start_with_checkout(4)
        self.start_dev_server()

        while self.pos < 8:
            self.recognise_listing_and_process_it()

        self.assertIn('wibble', self.listings[8])
        self.listings[8].was_checked = True
        self.assertIn('wibble', self.listings[9])
        self.listings[9].was_checked = True
        self.pos = 10

        while self.pos < 20:
            self.recognise_listing_and_process_it()

        unit_tests = self.run_command(Command('python manage.py test lists'))
        self.assertIn("OK", unit_tests)

        self.recognise_listing_and_process_it()

        add = self.run_command(self.listings[22])
        self.listings[23].was_checked = True

        diff = self.run_command(self.listings[24])
        self.assertIn('templates', diff)
        self.listings[25].was_checked = True
        self.pos = 26

        while self.pos < 37:
            self.recognise_listing_and_process_it()

        diff = self.run_command(self.listings[37])
        self.assertIn('templates', diff)
        self.listings[37].was_checked = True
        self.pos = 38

        self.recognise_listing_and_process_it()

        self.check_final_diff(4)
        self.assert_all_listings_checked(self.listings)


if __name__ == '__main__':
    unittest.main()
