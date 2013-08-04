#!/usr/bin/env python2.7
"""Run command on dev server

Usage:
    run_server_command.py [--ignore-errors] <command>
    run_server_command.py <source_file> <dest_file>

Options:
    --ignore-errors:  Ignore errors
"""


from docopt import docopt
from fabric.api import env, run
from fabric.contrib.files import put
import sys
import tempfile

SERVER_ADDRESS = 'superlists.ottg.eu'
env.host_string = SERVER_ADDRESS
env.user = 'harry'
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
        result = run('mv %s %s' % (tf.name, target))
        if result.failed:
            print >> sys.stderr, 'got result %s when trying to move file to target, retrying with sudo' % (result,)
            run('sudo mv %s %s' % (tf.name, target))
    finally:
        env.warn_only = False



if __name__ == '__main__':
    args = docopt(__doc__)
    if args['<command>']:
        run_command(args['<command>'], args['--ignore-errors'])
    else:
        write_file(args['<source_file>'], args['<dest_file>'])
