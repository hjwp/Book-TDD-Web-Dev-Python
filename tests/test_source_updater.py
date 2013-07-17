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
        f = s.functions['a_function']
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
        assert list(s.functions) == ['firstfn', 'second_fn']


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
        assert list(s.functions) == ['firstfn', 'a_view', 'second_fn', 'another_view']
        assert list(s.views) == ['a_view', 'another_view']


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
        assert list(s.classes) == ['Jimbob', 'Harlequin']



class ReplaceFunctionTest(unittest.TestCase):

    def test_finding_last_line_in_function(self):
        source = Source._from_contents(dedent("""
            def myfn():
                a += 1
                return b
            """).strip()
        )
        assert source.functions['myfn'].last_line ==  2


    def test_finding_last_line_in_function_with_brackets(self):
        source = Source._from_contents(dedent("""
            def myfn():
                a += 1
                return (
                    '2'
                )
            """).strip()
        )
        assert source.functions['myfn'].last_line ==  4


    def test_finding_last_line_in_function_with_brackets_before_another(self):
        source = Source._from_contents(dedent("""
            def myfn():
                a += 1
                return (
                    '2'
                )

            # bla

            def anotherfn():
                pass
            """).strip()
        )
        assert source.functions['myfn'].last_line ==  4


    def test_changing_the_end_of_a_method(self):
        source = Source._from_contents(dedent("""
            class A(object):
                def method1(self, stuff):
                    # do step 1
                    # do step 2
                    # do step 3
                    # do step 4
                    return (
                        'something'
                    )


                def method2(self):
                    # do stuff
                    pass
            """).lstrip()
        )
        new = dedent("""
            def method1(self, stuff):
                # do step 1
                # do step 2
                # do step A
                return (
                    'something else'
                )
            """
        ).strip()
        expected = dedent("""
            class A(object):
                def method1(self, stuff):
                    # do step 1
                    # do step 2
                    # do step A
                    return (
                        'something else'
                    )


                def method2(self):
                    # do stuff
                    pass
            """
        ).lstrip()
        to_write = source.replace_function(new.split('\n'))
        assert to_write == expected
        assert source.to_write == expected


class RemoveFunctionTest(unittest.TestCase):

    def test_removing_a_function(self):
        source = Source._from_contents(dedent(
            """
            def fn1(args):
                # do stuff
                pass


            def fn2(arg2, arg3):
                # do things
                return 2


            def fn3():
                # do nothing
                # really
                pass
            """).lstrip()
        )

        expected = dedent(
            """
            def fn1(args):
                # do stuff
                pass


            def fn3():
                # do nothing
                # really
                pass
            """
        ).lstrip()

        assert source.remove_function('fn2') == expected
        assert source.to_write == expected



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
