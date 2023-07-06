import unittest
from unittest.mock import patch
import subprocess
from textwrap import dedent
import os

from book_parser import CodeListing
from sourcetree import (
    ApplyCommitException,
    Commit,
    SourceTree,
    check_chunks_against_future_contents,
    get_offset,
    strip_comments,
)


class GetFileTest(unittest.TestCase):
    def test_get_contents(self):
        sourcetree = SourceTree()
        with open(sourcetree.tempdir + "/foo.txt", "w") as f:
            f.write("bla bla")
        assert sourcetree.get_contents("foo.txt") == "bla bla"


class StripCommentTest(unittest.TestCase):
    def test_strips_python_comments(self):
        assert strip_comments("foo #") == "foo"
        assert strip_comments("foo  #") == "foo"

    def test_strips_js_comments(self):
        assert strip_comments("foo //") == "foo"
        assert strip_comments("foo  //") == "foo"

    def test_doesnt_break_comment_lines(self):
        assert strip_comments("# normal comment") == "# normal comment"

    def test_doesnt_break_trailing_slashes(self):
        assert strip_comments("a_url/") == "a_url/"


class StartWithCheckoutTest(unittest.TestCase):
    def test_get_local_repo_path(self):
        sourcetree = SourceTree()
        assert sourcetree.get_local_repo_path("chapter_name") == os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../source/chapter_name/superlists")
        )

    def test_checks_out_repo_chapter_as_main(self):
        sourcetree = SourceTree()
        sourcetree.get_local_repo_path = lambda c: os.path.abspath(
            os.path.join(os.path.dirname(__file__), "testrepo")
        )
        sourcetree.start_with_checkout("chapter_17", "chapter_16")
        remotes = sourcetree.run_command("git remote").split()
        assert remotes == ["repo"]
        branch = sourcetree.run_command("git branch").strip()
        assert branch == "* main"
        diff = sourcetree.run_command("git diff repo/chapter_16").strip()
        assert diff == ""


class ApplyFromGitRefTest(unittest.TestCase):
    def setUp(self):
        self.sourcetree = SourceTree()
        self.sourcetree.get_local_repo_path = lambda c: os.path.abspath(
            os.path.join(os.path.dirname(__file__), "testrepo")
        )
        self.sourcetree.start_with_checkout("chapter_17", "chapter_16")
        self.sourcetree.run_command("git checkout test-start")
        self.sourcetree.run_command("git reset")

    def test_from_real_git_stuff(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                file 1 line 2 amended
                file 1 line 3
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        self.sourcetree.apply_listing_from_commit(listing)

        with open(self.sourcetree.tempdir + "/file1.txt") as f:
            assert (
                f.read()
                == dedent(
                    """
                    file 1 line 1
                    file 1 line 2 amended
                    file 1 line 3
                    """
                ).lstrip()
            )

        assert listing.was_written

    def test_leaves_staging_empty(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                file 1 line 2 amended
                file 1 line 3
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        self.sourcetree.apply_listing_from_commit(listing)

        staged = self.sourcetree.run_command("git diff --staged")
        assert staged == ""

    def test_raises_if_wrong_file(self):
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                file 1 line 1
                file 1 line 2 amended
                file 1 line 3
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def _checkout_commit(self, commit):
        commit_spec = self.sourcetree.get_commit_spec(commit)
        self.sourcetree.run_command("git checkout " + commit_spec)
        self.sourcetree.run_command("git reset")

    def test_raises_if_too_many_files_in_commit(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                file 1 line 1
                file 1 line 2
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l023"

        self._checkout_commit("ch17l022")
        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def test_raises_if_listing_doesnt_show_all_new_lines_in_diff(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                file 1 line 3
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def test_raises_if_listing_lines_in_wrong_order(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                file 1 line 3
                file 1 line 2 amended
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def test_line_ordering_check_isnt_confused_by_dupe_lines(self):
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                another line changed
                some duplicate lines coming up...

                hello
                goodbye
                hello
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l027"
        self._checkout_commit("ch17l026")

        self.sourcetree.apply_listing_from_commit(listing)

    def test_line_ordering_check_isnt_confused_by_new_lines_that_dupe_existing(self):
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                some duplicate lines coming up...

                hello

                one more line at end
                add a line with a dupe of existing
                hello
                goodbye
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l031"
        self._checkout_commit("ch17l030")

        self.sourcetree.apply_listing_from_commit(listing)

    def DONTtest_non_dupes_are_still_order_checked(self):
        # TODO: get this working
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                some duplicate lines coming up...

                hello

                one more line at end
                add a line with a dupe of existing
                goodbye
                hello
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l031"
        self._checkout_commit("ch17l030")

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def test_raises_if_any_other_listing_lines_not_in_before_version(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                what is this?
                file 1 line 2 amended
                file 1 line 3
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def test_happy_with_lines_in_before_and_after_version(self):
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                file 2 line 1 changed
                [...]

                hello
                hello

                one more line at end
            """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l028"
        self._checkout_commit("ch17l027")

        self.sourcetree.apply_listing_from_commit(listing)

    def test_raises_if_listing_line_not_in_after_version(self):
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                hello
                goodbye
                hello

                one more line at end
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l028"

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def test_happy_with_lines_from_just_before_diff(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                file 1 line 1
                file 1 line 2 amended
                file 1 line 3
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        self.sourcetree.apply_listing_from_commit(listing)

    def test_listings_showing_a_move_mean_can_ignore_commit_lines_added_and_removed(
        self,
    ):
        listing = CodeListing(
            filename="pythonfile.py",
            contents=dedent(
                """
                class NuKlass(object):

                    def method1(self):
                        [...]
                        a = a + 3
                        [...]
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l029"
        self._checkout_commit("ch17l028-1")

        self.sourcetree.apply_listing_from_commit(listing)

    def test_listings_showing_a_move_mean_can_ignore_commit_lines_added_and_removed_2(
        self,
    ):
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                hello

                one more line at end
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l030"
        self._checkout_commit("ch17l029")

        self.sourcetree.apply_listing_from_commit(listing)

    def test_happy_with_elipsis(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                [...]
                file 1 line 2 amended
                file 1 line 3
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        self.sourcetree.apply_listing_from_commit(listing)

    def DONTtest_listings_must_use_elipsis_to_indicate_skipped_lines(self):
        # TODO!
        lines = [
            "file 1 line 1",
            "file 1 line 2 amended",
            "file 1 line 3",
            "file 1 line 4 inserted",
            "another line",
        ]
        listing = CodeListing(filename="file1.txt", contents="")
        listing.commit_ref = "ch17l022"
        self._checkout_commit("ch17l021")

        listing.contents = "\n".join(lines)
        self.sourcetree.apply_listing_from_commit(listing)  # should not raise

        lines[1] = "[...]"
        listing.contents = "\n".join(lines)
        self.sourcetree.apply_listing_from_commit(listing)  # should not raise

        lines.pop(1)
        listing.contents = "\n".join(lines)
        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def test_happy_with_python_callouts(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                [...]
                file 1 line 2 amended  #
                file 1 line 3  #
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        self.sourcetree.apply_listing_from_commit(listing)

    def test_happy_with_js_callouts(self):
        listing = CodeListing(
            filename="file1.txt",
            contents=dedent(
                """
                [...]
                file 1 line 2 amended  //
                file 1 line 3  //
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l021"

        self.sourcetree.apply_listing_from_commit(listing)

    def test_happy_with_blank_lines(self):
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                file 2 line 1 changed

                another line changed
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l024"
        self._checkout_commit("ch17l023")

        self.sourcetree.apply_listing_from_commit(listing)

    def test_handles_indents(self):
        listing = CodeListing(
            filename="pythonfile.py",
            contents=dedent(
                """
                def method1(self):
                    # amend method 1
                    return 2

                [...]
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l026"
        self._checkout_commit("ch17l025")

        self.sourcetree.apply_listing_from_commit(listing)

    def test_over_indentation_differences_are_picked_up(self):
        listing = CodeListing(
            filename="pythonfile.py",
            contents=dedent(
                """
                def method1(self):
                        # amend method 1
                    return 2

                [...]
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l026"
        self._checkout_commit("ch17l025")

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def test_under_indentation_differences_are_picked_up(self):
        listing = CodeListing(
            filename="pythonfile.py",
            contents=dedent(
                """
                def method1(self):
                # amend method 1
                return 2

                [...]
                """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l026"
        self._checkout_commit("ch17l025")

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)

    def test_with_diff_listing_passing_case(self):
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                diff --git a/file2.txt b/file2.txt
                index 93f054e..519d518 100644
                --- a/file2.txt
                +++ b/file2.txt
                @@ -4,6 +4,5 @@ another line changed
                 some duplicate lines coming up...

                 hello
                -hello

                 one more line at end
                 """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l030"
        self._checkout_commit("ch17l029")

        self.sourcetree.apply_listing_from_commit(listing)

    def test_with_diff_listing_failure_case(self):
        listing = CodeListing(
            filename="file2.txt",
            contents=dedent(
                """
                diff --git a/file2.txt b/file2.txt
                index 93f054e..519d518 100644
                --- a/file2.txt
                +++ b/file2.txt
                @@ -4,6 +4,5 @@ another line changed
                 some duplicate lines coming up...

                 hello
                -hello
                +something else

                 one more line at end
                 """
            ).lstrip(),
        )
        listing.commit_ref = "ch17l030"
        self._checkout_commit("ch17l029")

        with self.assertRaises(ApplyCommitException):
            self.sourcetree.apply_listing_from_commit(listing)


class SourceTreeRunCommandTest(unittest.TestCase):
    def test_running_simple_command(self):
        sourcetree = SourceTree()
        sourcetree.run_command("touch foo", cwd=sourcetree.tempdir)
        assert os.path.exists(os.path.join(sourcetree.tempdir, "foo"))

    def test_default_directory_is_tempdir(self):
        sourcetree = SourceTree()
        sourcetree.run_command("touch foo")
        assert os.path.exists(os.path.join(sourcetree.tempdir, "foo"))

    def test_returns_output(self):
        sourcetree = SourceTree()
        output = sourcetree.run_command("echo hello", cwd=sourcetree.tempdir)
        assert output == "hello\n"

    def test_raises_on_errors(self):
        sourcetree = SourceTree()
        with self.assertRaises(Exception):
            sourcetree.run_command("synt!tax error", cwd=sourcetree.tempdir)
        sourcetree.run_command(
            "synt!tax error", cwd=sourcetree.tempdir, ignore_errors=True
        )

    def test_environment_variables(self):
        sourcetree = SourceTree()
        os.environ["TEHFOO"] = "baz"
        output = sourcetree.run_command("echo $TEHFOO", cwd=sourcetree.tempdir)
        assert output.strip() == "baz"

    def test_doesnt_raise_for_some_things_where_a_return_code_is_ok(self):
        sourcetree = SourceTree()
        sourcetree.run_command("diff foo bar", cwd=sourcetree.tempdir)
        sourcetree.run_command("python test.py", cwd=sourcetree.tempdir)

    def test_cleanup_kills_backgrounded_processes_and_rmdirs(self):
        sourcetree = SourceTree()
        sourcetree.run_command(
            'python -c"import time; time.sleep(5)" & #runserver', cwd=sourcetree.tempdir
        )
        assert len(sourcetree.processes) == 1
        sourcetree_pid = sourcetree.processes[0].pid
        pids = (
            subprocess.check_output("pgrep -f time.sleep", shell=True)
            .decode("utf8")
            .split()
        )
        print("sourcetree_pid", sourcetree_pid)
        print("pids", pids)
        sids = []
        for pid in reversed(pids):
            print("checking", pid)
            cmd = "ps -o sid --no-header -p %s" % (pid,)
            print(cmd)
            try:
                sid = subprocess.check_output(cmd, shell=True)
                print("sid", sid)
                sids.append(sid)
                assert sourcetree_pid == int(sid)
            except subprocess.CalledProcessError:
                pass
        assert sids

        sourcetree.cleanup()
        assert "time.sleep" not in subprocess.check_output(
            "ps auxf", shell=True
        ).decode("utf8")
        # assert not os.path.exists(sourcetree.tempdir)

    def test_running_interactive_command(self):
        sourcetree = SourceTree()

        command = "python3 -c \"print('input please?'); a = input();print('OK' if a=='yes' else 'NO')\""
        output = sourcetree.run_command(command, user_input="no")
        assert "NO" in output
        output = sourcetree.run_command(command, user_input="yes")
        assert "OK" in output

    @patch("sourcetree.subprocess")
    def test_special_cases_fab_deploy(self, mock_subprocess):
        mock_subprocess.Popen.return_value.returncode = 0
        mock_subprocess.Popen.return_value.communicate.return_value = "a", "b"
        sourcetree = SourceTree()
        sourcetree.run_command("fab deploy:host=elspeth@superlists-staging.ottg.eu")
        expected = (
            "cd deploy_tools &&"
            " fab -D -i"
            " ~/Dropbox/Book/.vagrant/machines/default/virtualbox/private_key"
            " deploy:host=elspeth@superlists-staging.ottg.eu"
        )
        assert mock_subprocess.Popen.call_args[0][0] == expected


class CommitTest(unittest.TestCase):
    def test_init_from_example(self):
        example = dedent(
            """
            commit 9ecbb2c2222b9b31ab21e51e42ed8179ec79b273
            Author: Harry <hjwp2@cantab.net>
            Date:   Thu Aug 22 20:26:09 2013 +0100

                Some comment text. --ch09l021--

                Conflicts:
                    lists/tests/test_views.py

            diff --git a/lists/tests/test_views.py b/lists/tests/test_views.py
            index 8e18d77..03fc675 100644
            --- a/lists/tests/test_views.py
            +++ b/lists/tests/test_views.py
            @@ -55,36 +55,6 @@ class NewListTest(TestCase):



            -class NewItemTest(TestCase):
            -
            -    def test_can_save_a_POST_request_to_an_existing_list(self):
            -        other_list = List.objects.create()
            -        correct_list = List.objects.create()
            -        self.assertEqual(new_item.list, correct_list)
            -
            -
            -    def test_redirects_to_list_view(self):
            -        other_list = List.objects.create()
            -        correct_list = List.objects.create()
            -        self.assertRedirects(response, '/lists/%d/' % (correct_list.id,))
            -
            -
            -
             class ListViewTest(TestCase):

                 def test_list_view_passes_list_to_list_template(self):
            @@ -112,3 +82,29 @@ class ListViewTest(TestCase):
                     self.assertNotContains(response, 'other list item 1')
                     self.assertNotContains(response, 'other list item 2')

            +
            +    def test_can_save_a_POST_request_to_an_existing_list(self):
            +        other_list = List.objects.create()
            +        correct_list = List.objects.create()
            +        self.assertEqual(new_item.list, correct_list)
            +
            +
            +    def test_POST_redirects_to_list_view(self):
            +        other_list = List.objects.create()
            +        correct_list = List.objects.create()
            +        self.assertRedirects(response, '/lists/%d/' % (correct_list.id,))
            + """
        )

        commit = Commit.from_diff(example)

        assert commit.info == example

        assert commit.lines_to_add == [
            "    def test_can_save_a_POST_request_to_an_existing_list(self):",
            "        other_list = List.objects.create()",
            "        correct_list = List.objects.create()",
            "        self.assertEqual(new_item.list, correct_list)",
            "    def test_POST_redirects_to_list_view(self):",
            "        other_list = List.objects.create()",
            "        correct_list = List.objects.create()",
            "        self.assertRedirects(response, '/lists/%d/' % (correct_list.id,))",
        ]

        assert commit.lines_to_remove == [
            "class NewItemTest(TestCase):",
            "    def test_can_save_a_POST_request_to_an_existing_list(self):",
            "        other_list = List.objects.create()",
            "        correct_list = List.objects.create()",
            "        self.assertEqual(new_item.list, correct_list)",
            "    def test_redirects_to_list_view(self):",
            "        other_list = List.objects.create()",
            "        correct_list = List.objects.create()",
            "        self.assertRedirects(response, '/lists/%d/' % (correct_list.id,))",
        ]

        assert commit.moved_lines == [
            "    def test_can_save_a_POST_request_to_an_existing_list(self):",
            "        other_list = List.objects.create()",
            "        correct_list = List.objects.create()",
            "        self.assertEqual(new_item.list, correct_list)",
            "        other_list = List.objects.create()",
            "        correct_list = List.objects.create()",
            "        self.assertRedirects(response, '/lists/%d/' % (correct_list.id,))",
        ]

        assert commit.deleted_lines == [
            "class NewItemTest(TestCase):",
            "    def test_redirects_to_list_view(self):",
        ]

        assert commit.new_lines == [
            "    def test_POST_redirects_to_list_view(self):",
        ]


class CheckChunksTest(unittest.TestCase):
    def test_get_offset_when_none(self):
        lines = [
            "def method1(self):",
            "    return 2",
        ]
        future_lines = [
            "def method1(self):",
            "    return 2",
        ]
        assert get_offset(lines, future_lines) == ""

    def test_get_offset_when_some(self):
        lines = [
            "",
            "def method1(self):",
            "    return 2",
        ]
        future_lines = [
            "    ",
            "    def method1(self):",
            "        return 2",
        ]
        assert get_offset(lines, future_lines) == "    "

    def test_passing_case(self):
        code = dedent(
            """
            def method1(self):
                # amend method 1
                return 2
            """
        ).strip()
        future_contents = dedent(
            """
            class Thing:
                def method1(self):
                    # amend method 1
                    return 2
            """
        ).strip()
        check_chunks_against_future_contents(code, future_contents)  # should not raise

    def test_over_indentation_differences_are_picked_up(self):
        code = dedent(
            """
            def method1(self):
                    # amend method 1
                return 2
            """
        ).strip()
        future_contents = dedent(
            """
            class Thing:
                def method1(self):
                    # amend method 1
                    return 2
            """
        ).strip()
        with self.assertRaises(ApplyCommitException):
            check_chunks_against_future_contents(code, future_contents)

    def test_under_indentation_differences_are_picked_up(self):
        code = dedent(
            """
            def method1(self):
            # amend method 1
                return 2
            """
        ).strip()
        future_contents = dedent(
            """
            class Thing:
                def method1(self):
                    # amend method 1
                    return 2
            """
        ).strip()
        with self.assertRaises(ApplyCommitException):
            check_chunks_against_future_contents(code, future_contents)

    def test_leading_blank_lines_in_listing_are_ignored(self):
        code = dedent(
            """
            def method1(self):
                # amend method 1
                return 2

            """
        )
        future_contents = dedent(
            """
            class Thing:
                def method1(self):
                    # amend method 1
                    return 2
            """
        ).strip()
        check_chunks_against_future_contents(code, future_contents)  # should not raise

    def test_thing(self):
        code = dedent(
            """
            [...]
            item.save()

            return render(
                request,
                "home.html",
                {"new_item_text": item.text},
            )
            """
        )
        future_contents = dedent(
            """
            from django.shortcuts import render
            from lists.models import Item


            def home_page(request):
                item = Item()
                item.text = request.POST.get("item_text", "")
                item.save()

                return render(
                    request,
                    "home.html",
                    {"new_item_text": item.text},
                )
            """
        ).strip()
        check_chunks_against_future_contents(code, future_contents)  # should not raise

    def test_trailing_blank_lines_in_listing_are_ignored(self):
        code = dedent(
            """
            def method1(self):
                # amend method 1
                return 2

            """
        ).lstrip()
        future_contents = dedent(
            """
            class Thing:
                def method1(self):
                    # amend method 1
                    return 2
            """
        ).strip()
        check_chunks_against_future_contents(code, future_contents)  # should not raise

    def test_elipsis_lines_are_ignored(self):
        lines = dedent(
            """
            def method1(self):
                # amend method 1
                return 2
            [...]
            """
        ).strip()
        future_lines = dedent(
            """
                def method1(self):
                    # amend method 1
                    return 2
            stuff
            """
        ).rstrip()
        check_chunks_against_future_contents(lines, future_lines)  # should not raise
