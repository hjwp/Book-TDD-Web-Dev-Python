#!/usr/bin/env python3
import unittest
import tempfile


from source_updater import Source


class SourceTest(unittest.TestCase):

    def test_from_path_constructor_with_existing_file(self):
        tf = tempfile.NamedTemporaryFile(delete=False)
        self.addCleanup(tf.close)
        tf.write('stuff'.encode('utf8'))
        tf.flush()

        s = Source.from_path(tf.name)
        self.assertIsInstance(s, Source)
        self.assertEqual(s.path, tf.name)
        self.assertEqual(s.contents, 'stuff')


    def test_from_path_constructor_with_nonexistent_file(self):
        s = Source.from_path('no.such.path')
        self.assertIsInstance(s, Source)
        self.assertEqual(s.path, 'no.such.path')
        self.assertEqual(s.contents, '')


    def test_lines(self):
        s = Source()
        s.contents = 'abc\ndef'
        self.assertEqual(s.lines, ['abc', 'def'])


    def test_write_writes_new_content_to_path(self):
        s = Source()
        tf = tempfile.NamedTemporaryFile()
        s.new_contents = 'abc\ndef'
        s.path = tf.name
        s.write()
        with open(tf.name) as f:
            self.assertEqual(f.read(), s.new_contents)



class SourceUpdateTest(unittest.TestCase):

    def test_update_with_empty_contents(self):
        s = Source()
        s.update('new stuff\n')
        self.assertEqual(s.new_contents, 'new stuff\n')

    def test_adds_final_newline_if_necessary(self):
        s = Source()
        s.update('new stuff')
        self.assertEqual(s.new_contents, 'new stuff\n')


if __name__ == '__main__':
    unittest.main()
