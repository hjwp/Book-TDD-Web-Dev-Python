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
            process.poll()
            if process.returncode is None:
                print 'killing', vars(process)
                os.killpg(process.pid, signal.SIGTERM)


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
        chapter_1 = html.cssselect('div.sect1')[1]
        listings = chapter_1.cssselect('div.listingblock')
        for listing in listings:
            if listing.getnext().get('class') == 'paragraph caption':
                filename = listing.getnext().text_content()
                write_to_file(filename, listing.text_content().strip())
            elif listing.cssselect('pre code strong'):
                command = listing.cssselect('pre code strong')[0].text_content()
                output_lines = listing.text_content().split('\n')
                output_excluding_command = '\n'.join(
                    l for l in output_lines if command not in l
                )
                actual_output = self.run_command(command)
                if 'runserver' in command:
                    continue
                self.assert_console_output_correct(output_excluding_command, actual_output)


if __name__ == '__main__':
    unittest.main()
