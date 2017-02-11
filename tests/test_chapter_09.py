#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil
import unittest
import time

from book_tester import ChapterTest
LOCAL = False

class Chapter9Test(ChapterTest):
    chapter_name = 'chapter_09'
    previous_chapter = 'chapter_prettification'

    def hack_hosts_file(self):
        with open('/etc/hosts', 'r') as f:
            self.oldhosts = f.read()
        shutil.copy('/etc/hosts', '/tmp/hosts.bak')
        with open('/etc/hosts', 'a') as f:
            f.write('\n192.168.56.101  superlists-staging.ottg.eu')
            f.write('\n192.168.56.101  superlists.ottg.eu')
        self.addCleanup(self.restore_hosts_file)

    def restore_hosts_file(self):
        with open('/etc/hosts', 'w') as f:
            f.write(self.oldhosts)

    def setUp(self):
        if LOCAL:
            self.hack_hosts_file()
        super().setUp()


    def cleanup_server(self):
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
        if LOCAL:
            def fix_git_clones(listing):
                if listing.type == 'server command':
                    return listing.replace('https://github.com/hjwp/book-example.git', '.../Book/source/chapter_prettification/superlists')
                return listing
            self.listings = [
                fix_git_clones(l) for l in self.listings
            ]

        # sanity checks
        self.assertEqual(self.listings[0].type, 'code listing with git ref')
        self.assertEqual(self.listings[1].type, 'code listing with git ref')
        self.assertEqual(self.listings[2].type, 'test')

        self.start_with_checkout()
        # other prep
        self.sourcetree.run_command('python3 manage.py migrate --noinput')

        # skips
        self.skip_with_check(37, 'replace the URL in the next line with')

        #self.skip_with_check(70, 'installed Django') #TODO test this
        #self.skip_with_check(72, '0 errors found') #TODO test this

        reboot_pos = 77
        assert self.listings[reboot_pos] == 'sudo reboot'
        assert self.listings[reboot_pos + 1] == 'sudo service nginx reload'

        # find two runservers, the first one of which should be killed
        # before we migrate and restart it, and the second one should be
        # killed before we switch to gunicorn
        migrate_pos = 83
        assert 'migrate' in self.listings[migrate_pos], 'wrong pos in listings\n{}'.format(
            '\n'.join('{} {}'.format(ix, l) for ix, l in enumerate(self.listings))
        )
        self.skip_with_check(migrate_pos + 1, 'Creating tables')
        self.skip_with_check(migrate_pos + 2, 'ls')
        self.skip_with_check(migrate_pos + 3, 'db.sqlite3')
        assert 'Creating tables' in self.listings[migrate_pos + 1]
        assert 'runserver' in self.listings[migrate_pos - 3]
        gunicorn_pos = 93
        assert 'gunicorn superlists.wsgi:application' in self.listings[gunicorn_pos]
        assert 'runserver' in self.listings[gunicorn_pos - 6]

        # hack fast-forward
        skip = False
        if skip:
            self.pos = 42
            self.sourcetree.run_command('git checkout {0}'.format(
                self.sourcetree.get_commit_spec('ch08l003')
            ))
            if self.pos > 43:
                self.current_server_cd = '~/sites/$SITENAME/source'
            if self.pos > 47:
                self.sourcetree.run_command('virtualenv --python=python3.3 ../virtualenv')
            if self.pos > 54:
                self.sourcetree.run_command('../virtualenv/bin/pip install django')

        else:
            self.cleanup_server()

        while self.pos < reboot_pos + 1:
            print(self.pos)
            self.recognise_listing_and_process_it()

        print('waiting for reboot')
        time.sleep(100)
        self.run_server_command(
            'sudo sed -i "s/# server_names_hash_bucket_size/server_names_hash_bucket_size/g" /etc/nginx/nginx.conf'
        )

        while self.pos < migrate_pos:
            print(self.pos)
            self.recognise_listing_and_process_it()
        self._cleanup_runserver()
        migrate_output = self.run_server_command(self.listings[migrate_pos])
        self.assertIn('Creating tables', migrate_output)
        self.skip_with_check(migrate_pos + 1, 'Creating tables')
        ls_output = self.run_server_command(self.listings[migrate_pos + 2])
        self.assertIn('db.sqlite3', ls_output)
        self.pos = migrate_pos + 4

        while self.pos < gunicorn_pos:
            print(self.pos)
            self.recognise_listing_and_process_it()
        self._cleanup_runserver()

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()

        self.assert_all_listings_checked(self.listings)
        self.check_final_diff()


if __name__ == '__main__':
    unittest.main()
