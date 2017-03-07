#!/usr/bin/env python3
import unittest
import os
import shutil
from textwrap import dedent
import tempfile

from book_tester import CodeListing

from write_to_file import (
    _find_last_line_for_class,
    number_of_identical_chars,
    write_to_file,
)


class ClassFinderTest(unittest.TestCase):

    def test_find_last_line_for_class(self):
        source = dedent(
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
            """
        )

        lineno = _find_last_line_for_class(source, 'ClassA')
        self.assertEqual(lineno, 9)
        # sanity-check
        self.assertEqual(source.split('\n')[lineno - 1].strip(), 'pass')

        lineno = _find_last_line_for_class(source, 'ClassB')
        self.assertEqual(lineno, 13)




class LineFinderTest(unittest.TestCase):

    def test_number_of_identical_chars(self):
        self.assertEqual(
            number_of_identical_chars('1234', '5678'),
            0
        )
        self.assertEqual(
            number_of_identical_chars('1234', '1235'),
            3
        )
        self.assertEqual(
            number_of_identical_chars('1234', '1243'),
            2
        )
        self.assertEqual(
            number_of_identical_chars('12345', '123WHATEVER45'),
            5
        )



class WriteToFileTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_simple_case(self):
        #done
        listing = CodeListing(filename='foo.py', contents='abc\ndef')
        write_to_file(listing, self.tempdir)
        with open(os.path.join(self.tempdir, listing.filename)) as f:
            self.assertEqual(f.read(), listing.contents + '\n')
        self.assertTrue(listing.was_written)

    def test_multiple_files(self):
        listing = CodeListing(filename='foo.py, bar.py', contents='abc\ndef')
        write_to_file(listing, self.tempdir)
        with open(os.path.join(self.tempdir, 'foo.py')) as f:
            self.assertEqual(f.read(), listing.contents + '\n')
        with open(os.path.join(self.tempdir, 'bar.py')) as f:
            self.assertEqual(f.read(), listing.contents + '\n')
        self.assertTrue(listing.was_written)


    def assert_write_to_file_gives(
        self, old_contents, new_contents, expected_contents
    ):
        listing = CodeListing(filename='foo.py', contents=new_contents)
        with open(os.path.join(self.tempdir, 'foo.py'), 'w') as f:
            f.write(old_contents)

        write_to_file(listing, self.tempdir)

        with open(os.path.join(self.tempdir, listing.filename)) as f:
            actual = f.read()
            self.assertMultiLineEqual(actual, expected_contents)


    def test_strips_python_line_callouts_one_space(self):
        contents = 'hello\nbla #\nstuff'
        self.assert_write_to_file_gives('', contents, 'hello\nbla\nstuff\n')

    def test_strips_python_line_callouts_two_spaces(self):
        contents = 'hello\nbla  #\nstuff'
        self.assert_write_to_file_gives('', contents, 'hello\nbla\nstuff\n')


    def test_strips_js_line_callouts(self):
        contents = 'hello\nbla //\nstuff'
        self.assert_write_to_file_gives('', contents, 'hello\nbla\nstuff\n')
        contents = 'hello\nbla  //'
        self.assert_write_to_file_gives('', contents, 'hello\nbla\n')


    def test_doesnt_mess_with_multiple_newlines(self):
        contents = 'hello\n\n\nbla'
        self.assert_write_to_file_gives('', contents, 'hello\n\n\nbla\n')


    def test_existing_file_bears_no_relation_means_replaced(self):
        old = '#abc\n#def\n#ghi\n#jkl\n'
        new = '#mno\n#pqr\n#stu\n#vvv\n'
        expected = new
        self.assert_write_to_file_gives(old, new, expected)


    def test_existing_file_has_views_means_apppend(self):
        old = dedent(
            """
            from django.stuff import things

            def a_view(request, param):
                pass
            """
        ).lstrip()
        new = dedent(
            """
            def another_view(request):
                pass
            """
        ).strip()

        expected = dedent(
            """
            from django.stuff import things

            def a_view(request, param):
                pass


            def another_view(request):
                pass
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_existing_file_has_single_class_means_replace(self):
        old = dedent(
            """
            class Jimmy(object):
                pass
            """).lstrip()
        new = dedent(
            """
            class Carruthers(object):
                pass
            """).strip()

        expected = dedent(
            """
            class Carruthers(object):
                pass
            """).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_existing_file_has_multiple_classes_means_append(self):
        old = dedent(
            """
            import apples
            import pears

            class Jimmy(object):
                pass



            class Bob(object):
                pass
            """
        ).lstrip()
        new = dedent(
            """
            class Carruthers(object):
                pass
            """
        ).strip()

        expected = dedent(
            """
            import apples
            import pears

            class Jimmy(object):
                pass



            class Bob(object):
                pass



            class Carruthers(object):
                pass
            """).lstrip()

        self.assert_write_to_file_gives(old, new, expected)



    def test_leading_elipsis_is_ignored(self):
        old = dedent(
            """
            class C():
                def foo():
                    # bla 1
                    # bla 2
                    # bla 3
                    # bla 4
                    return 1

            # the end
            """
        ).lstrip()
        new = dedent(
            """
            [...]
            # bla 2
            # bla 3b
            # bla 4b
            return 1
            """
        )
        expected = dedent(
            """
            class C():
                def foo():
                    # bla 1
                    # bla 2
                    # bla 3b
                    # bla 4b
                    return 1

            # the end
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_adding_import_at_top_then_elipsis_then_modified_stuff(self):
        old = dedent(
            """
            import topline
            # some stuff

            class C():
                def foo():
                    return 1
            """
        )
        new = dedent(
            """
            import newtopline
            [...]

                def foo():
                    return 2
            """
        )
        expected = dedent(
            """
            import newtopline
            import topline

            # some stuff

            class C():
                def foo():
                    return 2
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def DONTtest_adding_import_at_top_without_elipsis_then_modified_stuff(self):
        old = dedent(
            """
            import anoldthing
            import bthing
            import cthing

            class C(cthing.Bar):
                def foo():
                    return 1

                    # more stuff...
            """
        )
        new = dedent(
            """
            import anewthing
            import bthing
            import cthing

            class C(anewthing.Baz):
                def foo():
                    [...]
            """
        )
        expected = dedent(
            """
            import anewthing
            import bthing
            import cthing

            class C(anewthing.Baz):
                def foo():
                    return 1

                    # more stuff...
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_adding_import_at_top_then_elipsis_then_totally_new_stuff(self):
        old = dedent(
            """
            import topline

            # some stuff
            class C():
                pass
            """
        ).lstrip()
        new = dedent(
            """
            import newtopline
            [...]

            class Nu():
                pass
            """
        )
        expected = dedent(
            """
            import newtopline
            import topline

            # some stuff
            class C():
                pass



            class Nu():
                pass
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_elipsis_indicating_which_class_to_add_new_method_to(self):
        old = dedent(
            """
            import topline

            class A(object):
                def metha(self):
                    pass

            class B(object):
                def methb(self):
                    pass
            """
        ).lstrip()
        new = dedent(
            """
            class A(object):
                [...]

                def metha2(self):
                    pass
            """
        )
        expected = dedent(
            """
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
        self.assert_write_to_file_gives(old, new, expected)


    def test_adding_import_at_top_sorts_alphabetically_respecting_django_and_locals(self):
        old = dedent(
            """
            import atopline

            from django.monkeys import monkeys
            from django.chickens import chickens

            from lists.views import thing

            # some stuff
            class C():
                def foo():
                    return 1
            """)
        new = dedent(
            """
            import btopline
            [...]

                def foo():
                    return 2
            """
        )
        expected = dedent(
            """
            import atopline
            import btopline

            from django.chickens import chickens
            from django.monkeys import monkeys

            from lists.views import thing

            # some stuff
            class C():
                def foo():
                    return 2
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


        new = dedent(
            """
            from django.dickens import dickens
            [...]

                def foo():
                    return 2
            """
        )
        expected = dedent(
            """
            import atopline

            from django.chickens import chickens
            from django.dickens import dickens
            from django.monkeys import monkeys

            from lists.views import thing

            # some stuff
            class C():
                def foo():
                    return 2
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


        new = dedent(
            """
            from lists.zoos import thing
            [...]

                def foo():
                    return 2
            """
        )
        expected = dedent(
            """
            import atopline

            from django.chickens import chickens
            from django.monkeys import monkeys

            from lists.views import thing
            from lists.zoos import thing

            # some stuff
            class C():
                def foo():
                    return 2
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_new_contents_then_indented_elipsis_then_appendix(self):
        old = '#abc\n#def\n#ghi\n#jkl\n'
        new = (
            '#abc\n'
            'def foo(v):\n'
            '    return v + 1\n'
            '    #def\n'
            '    [... old stuff as before]\n'
            '# then add this'
        )
        expected = (
            '#abc\n'
            'def foo(v):\n'
            '    return v + 1\n'
            '    #def\n'
            '    #ghi\n'
            '    #jkl\n'
            '\n'
            '# then add this\n'
        )
        self.assert_write_to_file_gives(old, new, expected)


    def test_for_existing_file_replaces_matching_lines(self):
        old = dedent(
            """
            class Foo(object):
                def method_1(self):
                    return 1

                def method_2(self):
                    # two
                    return 2
            """
        ).lstrip()
        new = dedent(
            """
                def method_2(self):
                    # two
                    return 'two'
                """
        ).strip()
        expected = dedent(
            """
            class Foo(object):
                def method_1(self):
                    return 1

                def method_2(self):
                    # two
                    return 'two'
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_for_existing_file_doesnt_swallow_whitespace(self):
        old = dedent(
            """
            one = (
                1,
            )

            two = (
                2,
            )

            three = (
                3,
            )
            """).lstrip()
        new = dedent(
            """
            two = (
                2,
                #two
            )
            """
        ).strip()


        expected = dedent(
            """
            one = (
                1,
            )

            two = (
                2,
                #two
            )

            three = (
                3,
            )
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_longer_new_file_starts_replacing_from_first_different_line(self):
        old = dedent(
            """
            # line 1
            # line 2
            # line 3

            """
        ).lstrip()
        new = dedent(
            """
            # line 1
            # line 2

            # line 3

            # line 4
            """
        ).strip()
        expected = dedent(
            """
            # line 1
            # line 2

            # line 3

            # line 4
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_changing_the_end_of_a_method(self):
        old = dedent(
            """
            class A(object):
                def method1(self):
                    # do step 1
                    # do step 2
                    # do step 3
                    # do step 4
                    # do step 5
                    pass

                def method2(self):
                    # do stuff
                    pass
            """
        ).lstrip()
        new = dedent(
            """
            def method1(self):
                # do step 1
                # do step 2
                # do step A
                # do step B
            """
        ).strip()
        expected = dedent(
            """
            class A(object):
                def method1(self):
                    # do step 1
                    # do step 2
                    # do step A
                    # do step B

                def method2(self):
                    # do stuff
                    pass
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_for_existing_file_inserting_new_lines_between_comments(self):
        old = dedent(
            """
            # test 1
            a = foo()
            assert  a == 1

            if a:
                # test 2
                self.fail('finish me')

                # test 3

                # the end
            # is here
            """).lstrip()
        new = dedent(
            """
            # test 2
            b = bar()
            assert b == 2

            # test 3
            assert True
            self.fail('finish me')

            # the end
            [...]
            """
        ).lstrip()

        expected = dedent(
            """
            # test 1
            a = foo()
            assert  a == 1

            if a:
                # test 2
                b = bar()
                assert b == 2

                # test 3
                assert True
                self.fail('finish me')

                # the end
            # is here
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_single_line_replacement(self):
        old = dedent(
            """
            def wiggle():
                abc def
                abcd fghi
                jkl mno
            """
        ).lstrip()

        new = dedent(
            """
            abcd abcd
            """
        ).strip()

        expected = dedent(
            """
            def wiggle():
                abc def
                abcd abcd
                jkl mno
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_single_line_replacement_finds_most_probable_line(self):
        old = dedent(
            """
            abc
            abc daf ghi
            abc dex xyz
            jkl mno
            """
        ).lstrip()

        new = dedent(
            """
            abc deFFF ghi
            """
        ).strip()

        expected = dedent(
            """
            abc
            abc deFFF ghi
            abc dex xyz
            jkl mno
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_single_line_assertion_replacement(self):
        old = dedent(
            """
            class Wibble(unittest.TestCase):

                def test_number_1(self):
                    self.assertEqual(1 + 1, 2)
            """
        ).lstrip()

        new = dedent(
            """
                self.assertEqual(1 + 1, 3)
                """
        ).strip()

        expected = dedent(
            """
            class Wibble(unittest.TestCase):

                def test_number_1(self):
                    self.assertEqual(1 + 1, 3)
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_single_line_assertion_replacement_finds_right_one(self):
        old = dedent(
            """
            class Wibble(unittest.TestCase):

                def test_number_1(self):
                    self.assertEqual(1 + 1, 2)

                def test_number_2(self):
                    self.assertEqual(1 + 2, 3)
            """
        ).lstrip()

        new = dedent(
            """
                self.assertEqual(1 + 2, 4)
                """
        ).strip()

        expected = dedent(
            """
            class Wibble(unittest.TestCase):

                def test_number_1(self):
                    self.assertEqual(1 + 1, 2)

                def test_number_2(self):
                    self.assertEqual(1 + 2, 4)
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_single_line_assertion_replacement_real_views_example(self):
        old = dedent(
            """
            from lists.models import Item, List

            def home_page(request):
                return render(request, 'home.html')


            def view_list(request, list_id):
                list = List.objects.get(id=list_id)
                items = Item.objects.filter(list=list)
                return render(request, 'list.html', {'items': items})


            def new_list(request):
                list = List.objects.create()
                Item.objects.create(text=request.POST['item_text'], list=list)
                return redirect('/lists/%d/' % (list.id,))


            def add_item(request):
                pass
            """
        ).lstrip()

        new = dedent(
            """
            def add_item(request, list_id):
                pass
            """
        )

        expected = dedent(
            """
            from lists.models import Item, List

            def home_page(request):
                return render(request, 'home.html')


            def view_list(request, list_id):
                list = List.objects.get(id=list_id)
                items = Item.objects.filter(list=list)
                return render(request, 'list.html', {'items': items})


            def new_list(request):
                list = List.objects.create()
                Item.objects.create(text=request.POST['item_text'], list=list)
                return redirect('/lists/%d/' % (list.id,))


            def add_item(request, list_id):
                pass
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_changing_function_signature_and_stripping_comment(self):
        old = dedent(
            """
            # stuff

            def foo():
                pass
            """
        ).lstrip()

        new = dedent(
            """
            def foo(bar):
                pass
            """
        ).strip()

        expected = new + '\n'
        self.assert_write_to_file_gives(old, new, expected)


    def test_with_two_elipsis_dedented_change(self):
        old = dedent(
            """
            class Wibble(object):

                def foo(self):
                    return 2

                def bar(self):
                    return 3
            """).lstrip()

        new = dedent(
            """
                [...]
                def foo(self):
                    return 4

                def bar(self):
                [...]
                """
        ).strip()

        expected = dedent(
            """
            class Wibble(object):

                def foo(self):
                    return 4

                def bar(self):
                    return 3
            """
        ).lstrip()
        self.assert_write_to_file_gives(old, new, expected)


    def test_indents_in_new_dont_confuse_things(self):
        old = dedent(
            """
            class Wibble():
                def foo(self):
                    # comment 1
                    do something
                    # comment 2
                    do something else
                    and keep going
            """).lstrip()

        new = (
            "    # comment 2\n"
            "    time.sleep(2)\n"
            "    do something else\n"
        )

        expected = dedent(
            """
            class Wibble():
                def foo(self):
                    # comment 1
                    do something
                    # comment 2
                    time.sleep(2)
                    do something else
                    and keep going
            """).lstrip()
        self.assert_write_to_file_gives(old, new, expected)

    def test_double_indents_in_new_dont_confuse_things(self):
        old = dedent(
            """
            class Wibble():
                def foo(self):
                    if something:
                        do something
                # end of class
            """).lstrip()

        new = dedent(
            """
                if something:
                    do something else
            # end of class
            """)

        expected = dedent(
            """
            class Wibble():
                def foo(self):
                    if something:
                        do something else
                # end of class
            """).lstrip()
        self.assert_write_to_file_gives(old, new, expected)



if __name__ == '__main__':
    unittest.main()
