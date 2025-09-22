#!/usr/bin/env python3
import os
import unittest

from book_tester import ChapterTest


class Chapter9Test(ChapterTest):
    chapter_name = "chapter_09_docker"
    previous_chapter = "chapter_08_prettification"

    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, "code listing with git ref")
        self.assertEqual(self.listings[1].type, "test")

        # skips:

        # docker build output, we want to run the 'docker build'
        # but not check output
        self.skip_with_check(29, "naming to docker.io/library/superlists")
        self.skip_with_check(36, "naming to docker.io/library/superlists")
        self.skip_with_check(36, "naming to docker.io/library/superlists")
        # normal git one
        self.skip_with_check(82, "add Dockerfile, .dockerignore, .gitignore")

        self.start_with_checkout()
        # simulate having a db.sqlite3 and a static folder from previous chaps
        self.sourcetree.run_command("./manage.py migrate --noinput")
        self.sourcetree.run_command("./manage.py collectstatic --noinput")
        self.sourcetree.run_command("docker pull python:3.14-rc-slim")
        # Hack to be able to pretend that 3.14 is out and we dont have to use the rc
        self.sourcetree.run_command("docker tag python:3.14-rc-slim python:3.14-slim")

        # hack fast-forward
        self.skip_forward_if_skipto_set()


        while self.pos < len(self.listings):
            listing = self.listings[self.pos]
            print(self.pos, listing.type, repr(listing))
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff()


if __name__ == "__main__":
    unittest.main()
