#!/usr/bin/env python3.7
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

# this relies on an entry in the hosts file
env.host_string = 'superlists-staging.ottg.eu'
# env.port = '2222'
# env.key_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../.vagrant/machines/default/virtualbox/private_key')
env.user = 'elspeth'
env.disable_known_hosts = True
env.warn_only = True

def run_command(command, ignore_errors):
    env.warn_only = True
    result = run(command)
    print(result)
    if result.failed and not ignore_errors:
        raise Exception(
            f'server command run returned error code {result.return_code}, output was:\n{result.stderr}\n{result}'
        )


def write_file(source, target):
    tf = tempfile.NamedTemporaryFile()
    put(source, tf.name)

    try:
        env.warn_only = True
        result = run(f'mv {tf.name} {target}')
        if result.failed:
            print(f'got result {result} when trying to move file to target, retrying with sudo', file=sys.stderr)
            result = run(f'sudo mv {tf.name} {target}')
    finally:
        env.warn_only = False



if __name__ == '__main__':
    args = docopt(__doc__)
    if args['<command>']:
        run_command(args['<command>'], args['--ignore-errors'])
    else:
        write_file(args['<source_file>'], args['<dest_file>'])
