#!/usr/bin/env python3
import unittest
import tempfile
from textwrap import dedent


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
        s.to_write = 'abc\ndef'
        s.path = tf.name
        s.write()
        with open(tf.name) as f:
            self.assertEqual(f.read(), s.to_write)


class FunctionFinderTest(unittest.TestCase):

    def test_function_object(self):
        s = Source._from_contents(dedent(
            """
            def a_function(stuff, args):
                pass
            """
        ))
        f = s.functions[0]
        self.assertEqual(f.name, 'a_function')
        self.assertEqual(f.full_line, 'def a_function(stuff, args):')


    def test_finds_functions(self):
        s = Source._from_contents(dedent(
            """
            def firstfn(stuff, args):
                pass

            # stuff

            def second_fn():
                pass
            """
        ))
        assert [f.name for f in s.functions] == ['firstfn', 'second_fn']


    def test_finds_views(self):
        s = Source._from_contents(dedent(
            """
            def firstfn(stuff, args):
                pass

            # stuff
            def a_view(request):
                pass

            def second_fn():
                pass

            def another_view(request, stuff):
                pass
            """
        ))
        assert [f.name for f in s.functions] == ['firstfn', 'a_view', 'second_fn', 'another_view']
        assert [f.name for f in s.views] == ['a_view', 'another_view']


    def test_finds_classes(self):
        s = Source._from_contents(dedent(
            """
            import thingy

            class Jimbob(object):
                pass

            # stuff
            class Harlequin(thingy.Thing):
                pass
            """
        ))
        assert [c.name for c in s.classes] == ['Jimbob', 'Harlequin']



class SourceUpdateTest(unittest.TestCase):

    def test_update_with_empty_contents(self):
        s = Source()
        s.update('new stuff\n')
        self.assertEqual(s.to_write, 'new stuff\n')

    def test_adds_final_newline_if_necessary(self):
        s = Source()
        s.update('new stuff')
        self.assertEqual(s.to_write, 'new stuff\n')

    def test_strips_line_callouts(self):
        s = Source()
        s.update('hello\nbla #')
        assert s.to_write == 'hello\nbla\n'



if __name__ == '__main__':
    unittest.main()
