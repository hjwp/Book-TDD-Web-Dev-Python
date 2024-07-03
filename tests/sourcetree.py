import getpass
import os
import io
import re
import signal
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


def strip_comments(line):
    match_python = re.match(r"^(.+\S) +#$", line)
    if match_python:
        print("match python")
        return match_python.group(1)
    match_js = re.match(r"^(.+\S) +//$", line)
    if match_js:
        return match_js.group(1)
    return line


BOOTSTRAP_WGET = "wget -O bootstrap.zip https://github.com/twbs/bootstrap/releases/download/v3.3.4/bootstrap-3.3.4-dist.zip"


@dataclass
class Commit:
    info: str

    @staticmethod
    def from_diff(commit_info):
        return Commit(info=commit_info)

    @property
    def all_lines(self):
        return self.info.split("\n")

    @property
    def lines_to_add(self):
        return [
            l[1:]
            for l in self.all_lines
            if l.startswith("+") and l[1:].strip() and not l[1] == "+"
        ]

    @property
    def lines_to_remove(self):
        return [
            l[1:]
            for l in self.all_lines
            if l.startswith("-") and l[1:].strip() and not l[1] == "-"
        ]

    @property
    def moved_lines(self):
        return [l for l in self.lines_to_add if l in self.lines_to_remove]

    @property
    def deleted_lines(self):
        return [l for l in self.lines_to_remove if l not in self.lines_to_add]

    @property
    def new_lines(self):
        return [l for l in self.lines_to_add if l not in self.lines_to_remove]

    @property
    def stripped_lines_to_add(self):
        return [l.strip() for l in self.lines_to_add]


class ApplyCommitException(Exception):
    pass


class SourceTree:
    def __init__(self):
        self.tempdir = Path(tempfile.mkdtemp())
        self.processes = []
        self.dev_server_running = False

    def get_contents(self, path):
        with open(os.path.join(self.tempdir, path)) as f:
            return f.read()

    def cleanup(self):
        for process in self.processes:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                pass
        if os.environ.get("TMPDIR_CLEANUP") not in  ("0", "false"):
            shutil.rmtree(self.tempdir)

    def run_command(
        self, command, cwd=None, user_input=None, ignore_errors=False, silent=False
    ):
        if cwd is None:
            cwd = self.tempdir

        actual_command = command
        if command.startswith("fab deploy"):
            actual_command = f"cd deploy_tools && {command}"
            actual_command = actual_command.replace(
                "fab deploy",
                "fab -D -i ~/Dropbox/Book/.vagrant/machines/default/virtualbox/private_key deploy",
            )
        elif command.startswith("curl"):
            actual_command = command.replace("curl", "curl --silent --show-error")
        process = subprocess.Popen(
            actual_command,
            shell=True,
            cwd=cwd,
            executable="/bin/bash",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            preexec_fn=os.setsid,
            universal_newlines=True,
        )
        process._command = command
        self.processes.append(process)
        if "runserver" in command:
            # can't read output, stdout.read just hangs.
            # TODO: readline?  see below.
            return
        if "docker run" in command and "superlists" in command and not ignore_errors:
            output = ""
            while True:
                output += process.stdout.readline()
                if "Quit the server with CONTROL-C." in output:
                    # go any further and we hang.
                    print("docker run out:\n", output)
                    return output

        if user_input and not user_input.endswith("\n"):
            user_input += "\n"
        if user_input:
            print("sending user input: {}".format(user_input))
        output, _ = process.communicate(user_input)
        if process.returncode and not ignore_errors:
            if (
                " test" in command
                or "functional_tests" in command
                or "diff" in command
                or "migrate" in command
            ):
                return output
            print(
                "process %s return a non-zero code (%s)" % (command, process.returncode)
            )
            print("output:\n", output)
            raise Exception(
                "process %s return a non-zero code (%s)" % (command, process.returncode)
            )
        if not silent:
            try:
                print(output)
            except io.BlockingIOError as e:
                print(e)
                pass
        return output

    def get_local_repo_path(self, chapter_name):
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../source/{}/superlists".format(chapter_name),
            )
        )

    def start_with_checkout(self, chapter, previous_chapter):
        print("starting with checkout")
        self.run_command("git init .")
        self.run_command(f'git remote add repo "{self.get_local_repo_path(chapter)}"')
        self.run_command("git fetch repo")
        # NB - relies on previous_chapter existing as a branch in the chapter local_repo_path
        self.run_command("git reset --hard repo/{}".format(previous_chapter))
        print(self.run_command("git status"))
        self.chapter = chapter

    def get_commit_spec(self, commit_ref):
        return f"repo/{self.chapter}^{{/--{commit_ref}--}}"

    def get_files_from_commit_spec(self, commit_spec):
        return self.run_command(
            f"git diff-tree --no-commit-id --name-only --find-renames -r {commit_spec}"
        ).split()

    def show_future_version(self, commit_spec, path):
        return self.run_command("git show {}:{}".format(commit_spec, path), silent=True)

    def patch_from_commit(self, commit_ref, path=None):
        commit_spec = self.get_commit_spec(commit_ref)
        self.run_command(
            #'git diff {commit}^ {commit} | patch'.format(commit=commit_spec)
            "git show -M {commit} | patch -p1 --fuzz=3 --no-backup-if-mismatch".format(
                commit=commit_spec
            )
        )
        # self.run_command('git reset')

    def tidy_up_after_patches(self):
        # tidy up any .origs from patches
        self.run_command('find . -name "*.orig" -exec rm {} \\;')

    def apply_listing_from_commit(self, listing):
        commit_spec = self.get_commit_spec(listing.commit_ref)
        commit_info = self.run_command("git show -w %s" % (commit_spec,))
        print("Applying listing from commit.\nListing:\n" + listing.contents)

        commit = Commit.from_diff(commit_info)

        files = self.get_files_from_commit_spec(commit_spec)
        if files != [listing.filename]:
            raise ApplyCommitException(
                f"wrong files in listing {listing.commit_ref}: {listing.filename!r} should have been {files}"
            )
        future_contents = self.show_future_version(commit_spec, listing.filename)

        check_listing_matches_commit(listing, commit, future_contents)

        self.patch_from_commit(listing.commit_ref, listing.filename)
        listing.was_written = True
        print("applied commit.")


def check_listing_matches_commit(listing, commit, future_contents):
    if listing.is_diff():
        diff = Commit.from_diff(listing.contents)
        if diff.new_lines != commit.new_lines:
            raise ApplyCommitException(
                "diff new lines did not match.\n{}\n!=\n{}".format(
                    diff.new_lines, commit.new_lines
                )
            )

        return

    listing_lines = [strip_comments(l) for l in listing.contents.split("\n")]
    stripped_listing_lines = [l.strip() for l in listing_lines]
    for new_line in commit.new_lines:
        if new_line.strip() not in stripped_listing_lines:
            # print('stripped_listing_lines', stripped_listing_lines)
            raise ApplyCommitException(
                f"could not find commit new line {new_line!r} in listing {listing.commit_ref}:\n{listing.contents}"
            )

    check_chunks_against_future_contents("\n".join(listing_lines), future_contents)


def check_chunks_against_future_contents(listing_contents, future_contents):
    future_lines = future_contents.split("\n")

    for chunk in split_into_chunks(listing_contents):
        reindented_chunk = reindent_to_match(chunk, future_lines)
        if reindented_chunk not in future_contents:
            missing_lines = [
                l for l in reindented_chunk.splitlines() if l not in future_lines
            ]
            if missing_lines:
                print("missing lines:\n" + "\n".join(repr(l) for l in missing_lines))
                raise ApplyCommitException(
                    f"{len(missing_lines)} lines did not match future contents"
                )
            else:
                print("reindented listing")
                print("\n".join(repr(l) for l in reindented_chunk.splitlines()))
                print("future contents")
                print("\n".join(repr(l) for l in future_contents.splitlines()))
                tdir = Path(tempfile.mkdtemp())
                print("saving to", tdir)
                (tdir / "listing.txt").write_text(reindented_chunk)
                (tdir / "future.txt").write_text(future_contents)
                raise ApplyCommitException(
                    "Commit lines in wrong order, or listing is missing a [...] (?)"
                )


def get_offset(lines, future_lines):
    for line in lines:
        if line == "":
            continue
        if line in future_lines:
            return ""
        else:
            for future_line in future_lines:
                if future_line.endswith(line):
                    return future_line[: -len(line)]

    raise Exception("not match found to determine offset")


def reindent_to_match(code, future_lines):
    offset = get_offset(code.splitlines(), future_lines)
    return "\n".join((offset + line) if line else "" for line in code.splitlines())


def split_into_chunks(code):
    chunk = ""
    for line in code.splitlines():
        if line.strip() == "[...]":
            if chunk:
                yield chunk
                chunk = ""
        elif line.startswith("[...]"):
            if chunk:
                yield chunk
                chunk = ""
        elif line.endswith("[...]"):
            linestart, _, _ = line.partition("[...]")
            chunk += linestart
            yield chunk
            chunk = ""
        else:
            if chunk:
                chunk = f"{chunk}\n{line}"
            else:
                chunk = line

    if chunk:
        yield chunk
