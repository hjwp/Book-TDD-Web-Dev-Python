#!/usr/bin/env python3
"""Update required checkouts in source repo (branch for chap. n-1)
Does not affect working branch when username = harry

Usage:
  update_source_repo.py [<chapter_no>]

Options:
  -h --help                                 Show this screen.

"""
from docopt import docopt
import subprocess
import os
import getpass

THIS_FOLDER = os.path.abspath(os.path.dirname(__file__))

def fetch_if_possible(target_dir):
    fetch = subprocess.Popen(
        ['git', 'fetch'], cwd=target_dir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = fetch.communicate()
    print(stdout.decode(), stderr.decode())
    if fetch.returncode:
        if 'Name or service not known' in stderr.decode():
            # no internet
            print('No Internet')
            return False
        raise Exception("Error running git fetch")
    return True



def update_sources_for_chapter(chapter_no):
    target = os.path.join(
        THIS_FOLDER, 'source', 'chapter_{0:02d}'.format(chapter_no), 'superlists'
    )
    print('updating', target)
    subprocess.check_output(['git', 'submodule', 'update', target])
    current_chapter = 'chapter_{0:02d}'.format(chapter_no)
    chapter_before = 'chapter_{0:02d}'.format(chapter_no - 1)
    commit_specified_by_submodule = subprocess.check_output(
        ['git', 'log', '-n 1', '--format=%H'], cwd=target
    ).decode().strip()
    print('current commit', commit_specified_by_submodule)
    connected = fetch_if_possible(target)
    if not connected:
        return
    if chapter_no > 1:
        subprocess.check_output(['git', 'checkout', chapter_before], cwd=target)
        subprocess.check_output(['git', 'reset', '--hard', 'origin/{}'.format(chapter_before)], cwd=target)
    subprocess.check_output(['git', 'checkout', current_chapter], cwd=target)
    if getpass.getuser() == 'harry':
        print("skipping {} reset on harry's dev machine".format(current_chapter))
    else:
        subprocess.check_output(
            ['git', 'reset', '--hard', commit_specified_by_submodule],
            cwd=target
        )

def main(arguments):
    subprocess.check_output(['git', 'submodule', 'init'])
    if arguments['<chapter_no>']:
        update_sources_for_chapter(int(arguments['<chapter_no>']))
    else:
        print('updating all source repos')
        folders = os.listdir(os.path.join(THIS_FOLDER, 'source'))
        for folder in sorted(folders):
            if folder.startswith('chapter_'):
                chapter_no = int(folder[8:10])
                update_sources_for_chapter(chapter_no)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)



