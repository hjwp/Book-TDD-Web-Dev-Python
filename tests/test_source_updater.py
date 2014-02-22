#!/usr/bin/env python3
import unittest
import tempfile
from textwrap import dedent


from source_updater import Source, SourceUpdateError


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
        s.get_updated_contents = lambda: 'abc\ndef'
        s.path = tf.name
        s.write()
        with open(tf.name) as f:
            self.assertEqual(f.read(), s.get_updated_contents())



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
        assert source.get_updated_contents() == expected


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
        assert source.get_updated_contents() == expected


class AddToClassTest(unittest.TestCase):

    def test_finding_class_info(self):
        source = Source._from_contents(dedent(
            """
            import topline

            class ClassA(object):
                def metha(self):
                    pass

                def metha2(self):
                    pass

            class ClassB(object):
                def methb(self):
                    pass
            """).lstrip()
        )

        assert source.classes['ClassA'].start_line == 2
        assert source.classes['ClassA'].last_line == 7
        assert source.classes['ClassA'].source == dedent(
            """
            class ClassA(object):
                def metha(self):
                    pass

                def metha2(self):
                    pass
            """).strip()

        assert source.classes['ClassB'].last_line == 11
        assert source.classes['ClassB'].source == dedent(
            """
            class ClassB(object):
                def methb(self):
                    pass
            """).strip()


    def test_addding_to_class(self):
        source = Source._from_contents(dedent("""
            import topline

            class A(object):
                def metha(self):
                    pass



            class B(object):
                def methb(self):
                    pass
            """).lstrip()
        )
        source.add_to_class('A', dedent(
            """
            def metha2(self):
                pass
            """).strip().split('\n')
        )

        expected = dedent("""
            import topline

            class A(object):
                def metha(self):
                    pass


                def metha2(self):
                    pass



            class B(object):
                def methb(self):
                    pass
            """
        ).lstrip()
        assert source.contents == expected


    def test_addding_to_class_fixes_indents_and_superfluous_lines(self):
        source = Source._from_contents(dedent("""
            import topline

            class A(object):
                def metha(self):
                    pass
            """).lstrip()
        )
        source.add_to_class('A', [
            "",
            "    def metha2(self):",
            "        pass",
        ])

        expected = dedent("""
            import topline

            class A(object):
                def metha(self):
                    pass


                def metha2(self):
                    pass
            """
        ).lstrip()
        assert source.contents == expected



class ImportsTest(unittest.TestCase):

    def test_finding_different_types_of_import(self):
        source = Source._from_contents(dedent(
            """
            import trees
            from django.core.widgets import things, more_things
            import cars
            from datetime import datetime

            from django.monkeys import banana_eating

            from lists.views import Thing

            not_an_import = 'import things'

            def foo():
                # normal code
                pass
            """
        ))

        assert set(source.imports) == {
            "import trees",
            "from django.core.widgets import things, more_things",
            "import cars",
            "from datetime import datetime",
            "from django.monkeys import banana_eating",
            "from lists.views import Thing",
        }
        assert set(source.django_imports) == {
            "from django.core.widgets import things, more_things",
            "from django.monkeys import banana_eating",
        }
        assert set(source.project_imports) == {
            "from lists.views import Thing",
        }
        assert set(source.general_imports) == {
            "import trees",
            "from datetime import datetime",
            "import cars",
        }


    def test_find_first_nonimport_line(self):
        source = Source._from_contents(dedent(
            """
            import trees
            from django.core.widgets import things, more_things
            from django.monkeys import banana_eating
            from lists.views import Thing

            not_an_import = 'bla'
            # the end
            """).lstrip()
        )

        assert source.find_first_nonimport_line() == 5


    def test_find_first_nonimport_line_raises_if_imports_in_a_mess(self):
        source = Source._from_contents(dedent(
            """
            import trees
            def foo():
                return 'monkeys'
            import monkeys
            """).lstrip()
        )
        with self.assertRaises(SourceUpdateError):
            source.find_first_nonimport_line()

    def test_fixed_imports(self):
        source = Source._from_contents(dedent(
            """
            import btopline
            import atopline
            """).lstrip()
        )
        assert source.fixed_imports == dedent(
            """
            import atopline
            import btopline
            """).lstrip()

        source = Source._from_contents(dedent(
            """
            import atopline

            from django.monkeys import monkeys
            from django.chickens import chickens
            """).lstrip()
        )
        assert source.fixed_imports == dedent(
            """
            import atopline

            from django.chickens import chickens
            from django.monkeys import monkeys
            """).lstrip()

        source = Source._from_contents(dedent(
            """
            from lists.views import thing
            import atopline
            """).lstrip()
        )
        assert source.fixed_imports == dedent(
            """
            import atopline

            from lists.views import thing
            """).lstrip()

        source = Source._from_contents(dedent(
            """
            from lists.views import thing

            from django.db import models
            import atopline

            from django.aardvarks import Wilbur

            """).lstrip()
        )
        assert source.fixed_imports == dedent(
            """
            import atopline

            from django.aardvarks import Wilbur
            from django.db import models

            from lists.views import thing
            """).lstrip()


    def test_add_import(self):
        source = Source._from_contents(dedent(
            """
            import atopline

            from django.monkeys import monkeys
            from django.chickens import chickens

            from lists.views import thing

            # some stuff
            class C():
                def foo():
                    return 1
            """).lstrip()
        )
        source.add_imports([
            "import btopline"
        ])

        assert source.fixed_imports == dedent(
            """
            import atopline
            import btopline

            from django.chickens import chickens
            from django.monkeys import monkeys

            from lists.views import thing
            """
        ).lstrip()

        source.add_imports([
            "from django.dickens import ChuzzleWit"
        ])
        assert source.fixed_imports == dedent(
            """
            import atopline
            import btopline

            from django.chickens import chickens
            from django.dickens import ChuzzleWit
            from django.monkeys import monkeys

            from lists.views import thing
            """
        ).lstrip()


    def test_add_import_chooses_longer_lines(self):
        source = Source._from_contents(dedent(
            """
            import atopline
            from django.chickens import chickens
            from lists.views import thing
            # some stuff
            """).lstrip()
        )
        source.add_imports([
            "from django.chickens import chickens, eggs"
        ])

        assert source.fixed_imports == dedent(
            """
            import atopline

            from django.chickens import chickens, eggs

            from lists.views import thing
            """
        ).lstrip()


    def test_add_import_ends_up_in_updated_contents_when_appending(self):
        source = Source._from_contents(dedent(
            """
            import atopline

            # some stuff
            class C():
                def foo():
                    return 1
            """).lstrip()
        )
        source.add_imports([
            "from django.db import models"
        ])

        assert source.contents == dedent(
            """
            import atopline

            from django.db import models

            # some stuff
            class C():
                def foo():
                    return 1
            """
        ).lstrip()


    def test_add_import_ends_up_in_updated_contents_when_prepending(self):
        source = Source._from_contents(dedent(
            """
            import btopline

            # some stuff
            class C():
                def foo():
                    return 1
            """).lstrip()
        )
        source.add_imports([
            "import atopline"
        ])

        assert source.contents == dedent(
            """
            import atopline
            import btopline

            # some stuff
            class C():
                def foo():
                    return 1
            """
        ).lstrip()




class LineFindingTests(unittest.TestCase):

    def test_finding_start_line(self):
        source = Source._from_contents(dedent(
            """
            stuff
            things
            bla
            bla bla
                indented
            more
            then end
            """).lstrip()
        )

        assert source.find_start_line(['stuff', 'whatever']) == 0
        assert source.find_start_line(['bla bla', 'whatever']) == 3
        assert source.find_start_line(['indented', 'whatever']) == 4
        assert source.find_start_line(['    indented', 'whatever']) == 4
        assert source.find_start_line(['no such line', 'whatever']) == None
        with self.assertRaises(SourceUpdateError):
            source.find_start_line([''])
        with self.assertRaises(SourceUpdateError):
            source.find_start_line([])


    def test_finding_end_line(self):
        source = Source._from_contents(dedent(
            """
            stuff
            things
            bla
                bla bla
                indented
                more
            then end
            """).lstrip()
        )

        assert source.find_end_line(['stuff', 'things']) == 1
        assert source.find_end_line(['bla bla', 'whatever', 'more']) == 5
        assert source.find_end_line(['bla bla', 'whatever']) == None
        assert source.find_end_line(['no such line', 'whatever']) == None
        with self.assertRaises(SourceUpdateError):
            source.find_end_line([])
        with self.assertRaises(SourceUpdateError):
            source.find_end_line(['whatever',''])


    def test_finding_end_line_depends_on_start(self):
        source = Source._from_contents(dedent(
            """
            stuff
            things
            bla

            more stuff
            things
            bla
            then end
            """).lstrip()
        )

        assert source.find_end_line(['more stuff', 'things', 'bla']) == 6



class SourceUpdateTest(unittest.TestCase):

    def test_update_with_empty_contents(self):
        s = Source()
        s.update('new stuff\n')
        self.assertEqual(s.get_updated_contents(), 'new stuff\n')

    def test_adds_final_newline_if_necessary(self):
        s = Source()
        s.update('new stuff')
        self.assertEqual(s.get_updated_contents(), 'new stuff\n')


if __name__ == '__main__':
    unittest.main()
