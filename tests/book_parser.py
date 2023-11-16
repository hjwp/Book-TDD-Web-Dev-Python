#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re


COMMIT_REF_FINDER = r"ch\d\dl\d\d\d-?\d?"


class CodeListing(object):
    COMMIT_REF_FINDER = r"^(.+) \((" + COMMIT_REF_FINDER + r")\)$"

    def __init__(self, filename, contents):
        self.is_server_listing = False
        if re.match(CodeListing.COMMIT_REF_FINDER, filename):
            self.filename = re.match(CodeListing.COMMIT_REF_FINDER, filename).group(1)
            self.commit_ref = re.match(CodeListing.COMMIT_REF_FINDER, filename).group(2)
        elif filename.startswith("server: "):
            self.filename = filename.replace("server: ", "")
            self.commit_ref = None
            self.is_server_listing = True
        else:
            self.filename = filename
            self.commit_ref = None
        self.contents = contents
        self.was_written = False
        self.skip = False
        self.currentcontents = False
        self.against_server = False

    def is_diff(self):
        lines = self.contents.split("\n")
        if any(l.count("@@") > 1 for l in lines):
            return True
        if len([l for l in lines if l.startswith("+") or l.startswith("-")]) > 2:
            return True

    @property
    def type(self):
        if self.is_server_listing:
            return "server code listing"
        elif self.currentcontents:
            return "code listing currentcontents"
        elif self.commit_ref:
            return "code listing with git ref"
        elif self.is_diff():
            return "diff"
        else:
            return "code listing"

    def __repr__(self):
        return "<CodeListing %s: %s...>" % (self.filename, self.contents.split("\n")[0])


class Command(str):
    def __init__(self, a_string):
        self.was_run = False
        self.skip = False
        self.ignore_errors = False
        self.server_command = False
        self.against_server = False
        self.dofirst = None
        str.__init__(a_string)

    @property
    def type(self):
        if self.server_command:
            return "server command"
        for git_cmd in ("git diff", "git status", "git commit"):
            if git_cmd in self:
                return git_cmd
        if self.startswith("python") and "test" in self:
            return "test"
        if self == "python manage.py behave":
            return "bdd test"
        if self == "python manage.py migrate":
            return "interactive manage.py"
        if self == "python manage.py makemigrations":
            return "interactive manage.py"
        if self == "python manage.py collectstatic":
            return "interactive manage.py"
        if self.startswith("STAGING_SERVER="):
            return "against staging"
        else:
            return "other command"

    def __repr__(self):
        return "<Command %s>" % (str.__repr__(self),)


class Output(str):
    def __init__(self, a_string):
        self.was_checked = False
        self.skip = False
        self.dofirst = None
        self.qunit_output = False
        self.against_server = False
        str.__init__(a_string)

    @property
    def type(self) -> str:
        if self.qunit_output:
            return "qunit output"
        if "├" in self:
            return "tree"
        else:
            return "output"


def fix_newlines(text):
    if text is None:
        return ""
    return text.replace("\r\n", "\n").replace("\\\n", "").strip("\n")


def parse_output(listing):
    text = fix_newlines(listing.text_content().strip())

    commands = listing.cssselect("pre strong")
    if not commands:
        return [Output(text)]

    outputs = []
    output_before = listing.text
    if output_before:
        output_before = fix_newlines(output_before.strip())
    else:
        output_before = ""

    for command in commands:
        if "$" in output_before and "\n" in output_before:
            last_cr = output_before.rfind("\n")
            previous_lines = output_before[:last_cr]
            if previous_lines:
                outputs.append(Output(previous_lines))
        elif output_before and "$" not in output_before:
            outputs.append(Output(output_before))

        command_text = fix_newlines(command.text)
        if output_before.strip().startswith("(virtualenv)"):
            command_text = "source ./.venv/bin/activate && " + command_text
        outputs.append(Command(command_text))

        output_before = fix_newlines(command.tail)

    if output_before:
        outputs.append(Output(output_before))

    return outputs


def _strip_callouts(content):
    callout_at_end = r"\s+\(\d+\)$"
    counts = 0
    while re.search(callout_at_end, content, re.MULTILINE):
        content = re.sub(callout_at_end, "", content, flags=re.MULTILINE)
        counts += 1
    return content


def parse_listing(listing):
    classes = listing.get("class").split()
    skip = "skipme" in classes
    dofirst_classes = [c for c in classes if c.startswith("dofirst")]
    if dofirst_classes:
        dofirst = re.findall(COMMIT_REF_FINDER, dofirst_classes[0])[0]
    else:
        dofirst = None

    if "sourcecode" in classes:
        try:
            filename = listing.cssselect(".title")[0].text_content().strip()
        except IndexError:
            raise Exception(
                "could not find title for listing {}".format(listing.text_content())
            )
        contents = (
            listing.cssselect(".content")[0]
            .text_content()
            .replace("\r\n", "\n")
            .strip("\n")
        )
        contents = _strip_callouts(contents)
        listing = CodeListing(filename, contents)
        listing.skip = skip
        listing.dofirst = dofirst
        if "currentcontents" in classes:
            listing.currentcontents = True
        return [listing]

    elif "qunit-output" in classes:
        contents = (
            listing.cssselect(".content")[0]
            .text_content()
            .replace("\r\n", "\n")
            .strip("\n")
        )
        output = Output(contents)
        output.qunit_output = True
        output.skip = skip
        output.dofirst = dofirst
        return [output]

    if "server-commands" in classes:
        listing = listing.cssselect("div.content")[0]

    outputs = parse_output(listing)
    if skip:
        for listing in outputs:
            listing.skip = True
    if dofirst:
        outputs[0].dofirst = dofirst
    if "ignore-errors" in classes:
        for listing in outputs:
            if isinstance(listing, Command):
                listing.ignore_errors = True
    if "server-commands" in classes:
        for listing in outputs:
            if isinstance(listing, Command):
                listing.server_command = True
    if "against-server" in classes:
        for listing in outputs:
            listing.against_server = True

    return outputs


def get_commands(node):
    return [
        el.text_content().replace("\\\n", "")
        for el in node.cssselect("pre code strong")
    ]
