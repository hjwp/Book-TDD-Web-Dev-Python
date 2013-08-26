#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import time

from book_tester import ChapterTest

class Chapter8Test(ChapterTest):
    chapter_no = 8

    def setUp(self):
        super().setUp()
        self.run_server_command('rm -rf ~/sites')
        self.run_server_command('sudo rm -f /etc/nginx/sites-available/*ottg*')
        self.run_server_command('sudo rm -f /etc/nginx/sites-enabled/*ottg*')
        self.run_server_command('sudo ln -sf ../sites-available/default /etc/nginx/sites-enabled/default')
        self.run_server_command('sudo service nginx reload')
        self._cleanup_runserver()

    def tearDown(self):
        #self.run_server_command('rm -rf ~/sites')
        super().tearDown()


    def test_listings_and_commands_and_output(self):
        self.parse_listings()

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing with git ref')
        self.assertEqual(self.listings[1].type, 'code listing with git ref')
        self.assertEqual(self.listings[2].type, 'test')

        self.sourcetree.start_with_checkout(self.chapter_no)
        # other prep
        self.sourcetree.run_command('python3 manage.py syncdb --noinput')

        # skips
        self.listings[4].skip = True # domain name registration
        self.listings[5].skip = True # domain name registration
        self.listings[17].skip = True # preview of future tree
        self.listings[32].skip = True # comment in server commands

        assert self.listings[35] == 'python3 manage.py runserver'
        self.listings[35].skip = True # TODO: - test this, ignore errors and check stderr
        self.listings[36].skip = True # TODO: - test this, ignore errors and check stderr

        assert self.listings[37] == 'pip-3.3 install virtualenv'
        self.listings[37].skip = True # TODO: - test this

        assert self.listings[54] == 'git push'
        self.listings[54].skip = True

        assert 'installed Django' in self.listings[59]
        self.listings[59].skip = True #TODO test this

        assert '0 errors found' in self.listings[61]
        self.listings[61].skip = True #TODO test this

        assert self.listings[66] == 'sudo service nginx reload'
        assert 'runserver' in self.listings[68]
        assert 'runserver' in self.listings[74]
        assert self.listings[65] == 'sudo reboot'

        while self.pos < 66:
            print(self.pos)
            self.recognise_listing_and_process_it()

        print('waiting for reboot')
        time.sleep(100)
        self.run_server_command(
            'sudo sed -i "s/# server_names_hash_bucket_size/server_names_hash_bucket_size/g" /etc/nginx/nginx.conf'
        )

        while self.pos < 72:
            print(self.pos)
            self.recognise_listing_and_process_it()

        # kill runserver so we can re-run it later
        self._cleanup_runserver()

        while self.pos < 200:
            print(self.pos)
            self.recognise_listing_and_process_it()
        #print(self.tempdir)
        #time.sleep(200)

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
