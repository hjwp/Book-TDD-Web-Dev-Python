import os
import signal
import shutil
import subprocess
import tempfile


class SourceTree(object):

    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.processes = []
        self.dev_server_running = False


    def cleanup(self):
        for process in self.processes:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                pass
        shutil.rmtree(self.tempdir)


    def start_with_checkout(self, chapter):
        local_repo_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../source/chapter_%d/superlists' % (chapter,)
        ))
        self.run_command('mkdir superlists', cwd=self.tempdir)
        self.run_command('git init .')
        self.run_command('git remote add repo %s' % (local_repo_path,))
        self.run_command('git fetch repo')
        self.run_command('git checkout chapter_%s' % (chapter - 1,))



    def run_command(self, command, cwd=None, user_input=None):
        if cwd is None:
            cwd = os.path.join(self.tempdir, 'superlists')
        print('running command', command)
        process = subprocess.Popen(
            command, shell=True, cwd=cwd, executable='/bin/bash',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            preexec_fn=os.setsid,
            universal_newlines=True,
        )
        process._command = command
        self.processes.append(process)
        if 'runserver' in command:
            return #test this another day
        if user_input and not user_input.endswith('\n'):
            user_input += '\n'
        #import time
        #time.sleep(1)
        output, _ = process.communicate(user_input)
        if process.returncode and 'test' not in command:
            print('process %s return a non-zero code (%s)' % (command, process.returncode))
            print('output:\n', output)
            raise Exception('process %s return a non-zero code (%s)' % (command, process.returncode))
        return output

