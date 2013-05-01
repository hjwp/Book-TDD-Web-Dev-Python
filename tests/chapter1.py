from collections import namedtuple
import os
import signal
import subprocess
import tempfile
import unittest
from lxml import html

base_dir = os.path.split(os.path.dirname(__file__))[0]
raw_html = open(os.path.join(base_dir, 'book.html')).read()
html = html.fromstring(raw_html)

tempdir = tempfile.mkdtemp()

def write_to_file(filename, contents):
    print 'writing to file', filename
    with open(os.path.join(tempdir, filename), 'w') as f:
        f.write(contents)
    print 'wrote', open(os.path.join(tempdir, filename)).read()




class Chapter1Test(unittest.TestCase):

    def setUp(self):
        self.processes = []

    def tearDown(self):
        for process in self.processes:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                print 'error killing', process._command


    def run_command(self, command):
        cwd = tempdir
        if 'superlists' in os.listdir(tempdir):
            cwd = os.path.join(tempdir, 'superlists')
        if 'functional_tests.py' in command and 'functional_tests.py' in os.listdir(tempdir):
            cwd = tempdir
        print 'running command', command
        process = subprocess.Popen(
            command, shell=True, cwd=cwd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        process._command = command
        self.processes.append(process)
        print 'directory listing is now', os.listdir(tempdir)
        if 'runserver' in command:
            return
        process.wait()
        return process.stdout.read()


    def assert_console_output_correct(self, expected, actual):
        def nonblank(lines):
            return '\n'.join(l for l in lines if l and l.strip() != '$')

        self.assertMultiLineEqual(
            nonblank(actual.replace('\r\n', '\n').strip().split('\n')),
            nonblank(expected.replace('\r\n', '\n').strip().split('\n'))
        )


    def test_listings_and_commands_and_output(self):
        CodeListing = namedtuple('CodeListing', ['filename', 'contents'])
        chapter_1 = html.cssselect('div.sect1')[1]
        listings = chapter_1.cssselect('div.listingblock')
        code_listings = []
        commands = []
        outputs = []
        for listing in listings:
            if listing.getnext().get('class') == 'paragraph caption':
                filename = listing.getnext().text_content()
                contents = listing.text_content().strip()
                code_listings.append(CodeListing(filename, contents))
                continue
            if listing.cssselect('pre code strong'):
                commands_in_this_listing = [
                    el.text_content()
                    for el in listing.cssselect('pre code strong')
                ]
                commands.extend(commands_in_this_listing)
                if not commands_in_this_listing:
                    outputs.extend(listing.text_content())
                else:
                    output_after_command = ''
                    for line in listing.text_content().split('\n'):
                        if any(cmd in line for cmd in commands_in_this_listing):
                            if output_after_command:
                                outputs.append(output_after_command)
                                output_after_command = ''
                        else:
                            output_after_command += line + '\n'
                    if output_after_command:
                        outputs.append(output_after_command)
                        output_after_command = ''

        ## hack -- listings with a star in are weird
        fix_pos = commands.index("git rm --cached superlists/")
        commands.remove("git rm --cached superlists/")
        commands.remove(".pyc")
        commands.insert(fix_pos, "git rm --cached superlists/*.pyc")

        self.assertEqual(len(code_listings), 1)
        self.assertEqual(len(commands), 16, 'len %s not %s, %s' %(len(commands), 16, str(commands)))
        self.assertEqual(len(outputs), 14, 'len %s not %s, %s' %(len(outputs), 14, '\n\n'.join(outputs)))


if __name__ == '__main__':
    unittest.main()
