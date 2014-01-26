#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil
import unittest
import time

from book_tester import ChapterTest

class Chapter8Test(ChapterTest):
    chapter_no = 8

    def setUp(self):
        super().setUp()
        with open('/etc/hosts', 'r') as f:
            self.oldhosts = f.read()
        shutil.copy('/etc/hosts', '/tmp/hosts.bak')
        with open('/etc/hosts', 'a') as f:
            f.write('\n192.168.56.102  superlists-staging.ottg.eu')
            f.write('\n192.168.56.102  superlists.ottg.eu')
        self.run_server_command('rm -rf ~/sites')
        self.run_server_command('sudo rm -f /etc/nginx/sites-available/*ottg*')
        self.run_server_command('sudo rm -f /etc/nginx/sites-enabled/*ottg*')
        self.run_server_command('sudo ln -sf ../sites-available/default /etc/nginx/sites-enabled/default')
        self.run_server_command('sudo service nginx reload')
        self._cleanup_runserver()

    def tearDown(self):
        with open('/etc/hosts', 'w') as f:
            f.write(self.oldhosts)
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
        self.skip_with_check(4, 'manage.py test functional_tests')
        self.skip_with_check(5, '123-reg')

        self.skip_with_check(41, 'replace the URL in the next line with')
        # TODO: - test this, ignore errors and check stderr
        self.skip_with_check(44, 'python3 manage.py runserver')
        self.skip_with_check(45, 'ImportError')

        self.skip_with_check(46, 'pip-3.3 install virtualenv') # TODO: - test this

        self.skip_with_check(65, 'git push')
        self.skip_with_check(70, 'installed Django') #TODO test this
        self.skip_with_check(72, '0 errors found') #TODO test this

        reboot_pos = 76
        assert self.listings[reboot_pos] == 'sudo reboot'
        assert self.listings[reboot_pos + 1] == 'sudo service nginx reload'

        # find two runservers, the first one of which should be killed
        # before we syncdb and restart it, and the second one should be
        # killed before we switch to gunicorn
        syncdb_pos = 82
        assert 'syncdb' in self.listings[syncdb_pos], 'wrong pos in listings\n{}'.format(
            '\n'.join('{} {}'.format(ix, l) for ix, l in enumerate(self.listings))
        )
        self.skip_with_check(syncdb_pos + 1, 'Creating tables')
        self.skip_with_check(syncdb_pos + 2, 'ls')
        self.skip_with_check(syncdb_pos + 3, 'db.sqlite3')
        assert 'Creating tables' in self.listings[syncdb_pos + 1]
        assert 'runserver' in self.listings[syncdb_pos - 3]
        gunicorn_pos = 92
        assert 'gunicorn superlists.wsgi:application' in self.listings[gunicorn_pos]
        assert 'runserver' in self.listings[gunicorn_pos - 6]

        while self.pos < reboot_pos + 1:
            print(self.pos)
            self.recognise_listing_and_process_it()

        print('waiting for reboot')
        time.sleep(100)
        self.run_server_command(
            'sudo sed -i "s/# server_names_hash_bucket_size/server_names_hash_bucket_size/g" /etc/nginx/nginx.conf'
        )

        while self.pos < syncdb_pos:
            print(self.pos)
            self.recognise_listing_and_process_it()
        self._cleanup_runserver()
        syncdb_output = self.run_server_command(self.listings[syncdb_pos])
        self.assertIn('Creating tables', syncdb_output)
        self.skip_with_check(syncdb_pos + 1, 'Creating tables')
        ls_output = self.run_server_command(self.listings[syncdb_pos + 2])
        self.assertIn('db.sqlite3', ls_output)
        self.pos = syncdb_pos + 4

        while self.pos < gunicorn_pos:
            print(self.pos)
            self.recognise_listing_and_process_it()
        self._cleanup_runserver()

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff(self.chapter_no)


if __name__ == '__main__':
    unittest.main()
