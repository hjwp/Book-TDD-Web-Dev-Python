#!/usr/bin/env python
"""Run command on dev server

Usage:
    run_server_command.py [--ignore-errors] <command>
    run_server_command.py <source_file> <dest_file>

Options:
    --ignore-errors:  Ignore errors
"""


from docopt import docopt
from fabric.api import env, run
import os
from fabric.contrib.files import put
import sys
import tempfile

env.host_string = 'superlists-staging.ottg.eu'
# env.port = '2222'
env.key_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../.vagrant/machines/default/virtualbox/private_key')
env.user = 'ubuntu'
env.warn_only = False

def run_command(command, ignore_errors):
    try:
        env.warn_only = ignore_errors
        run(command)
    finally:
        env.warn_only = False


def write_file(source, target):
    tf = tempfile.NamedTemporaryFile()
    put(source, tf.name)

    try:
        env.warn_only = True
        result = run(f'mv {tf.name} {target}')
        if result.failed:
            print('got result {result} when trying to move file to target, retrying with sudo', file=sys.stderr)
            result = run(f'sudo mv {tf.name} {target}')
    finally:
        env.warn_only = False



if __name__ == '__main__':
    args = docopt(__doc__)
    if args['<command>']:
        run_command(args['<command>'], args['--ignore-errors'])
    else:
        write_file(args['<source_file>'], args['<dest_file>'])
