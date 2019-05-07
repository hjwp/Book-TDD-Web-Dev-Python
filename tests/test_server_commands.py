#!/usr/bin/env python3
import tempfile
from book_tester import ChapterTest


class RunServerCommandIntegrationTest(ChapterTest):

    def xtest_semifunctional_run_command_sanity_check(self):
        tf = tempfile.NamedTemporaryFile()
        self.run_server_command('touch /tmp/foo-on-server')
        result = self.run_server_command('ls /tmp')
        assert 'foo-on-server' in result
        assert tf.name not in result


    def xtest_semifunctional_run_ignore_errors(self):
        self.run_server_command('barf', ignore_errors=True)


class WriteFileOnServerIntegrationTest(ChapterTest):

    def xtest_semifunctional_write_file(self):
        self.write_file_on_server('/tmp/file.name', 'some stuff')
        result = self.run_server_command('cat /tmp/file.name')
        assert 'some stuff' in result
        self.run_server_command('rm /tmp/file.name')


    def xtest_semifunctional_write_file_with_root_perms(self):
        self.write_file_on_server('/root/file.name', 'some stuff')
        result = self.run_server_command('sudo cat /root/file.name')
        assert 'some stuff' in result
        self.run_server_command('sudo rm /root/file.name')

