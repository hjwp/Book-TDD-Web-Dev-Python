#!/usr/bin/env python3
from collections import namedtuple
import csv
from datetime import datetime
import os
import re
import subprocess

Commit = namedtuple('Commit', ['hash', 'subject', 'date'])
WordCount = namedtuple('WordCount', ['filename', 'lines', 'words'])
FileWordCount = namedtuple('FileWordCount', ['date', 'subject', 'hash', 'lines', 'words'])
BOOK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_log():
    commits = []
    log = subprocess.check_output(['git', 'log', '--format=%h|%s|%ai']).decode('utf8')
    for line in log.split('\n'):
        if line:
            hash, subject, datestring = line.split('|')
            date = datetime.strptime(datestring[:16], '%Y-%m-%d %H:%M')
            commits.append(Commit(hash=hash, subject=subject, date=date))
    return commits


def checkout_commit(hash):
    subprocess.check_call(['git', 'checkout', hash])


def get_wordcounts():
    docs = [f for f in os.listdir(BOOK_ROOT) if f.endswith('.asciidoc')]
    wordcounts = []
    for filename in docs:
        with open(os.path.join(BOOK_ROOT, filename)) as f:
            contents = f.read()
        lines = len(contents.split('\n'))
        words = len(contents.split())
        filename = re.sub(r'_(\d)\.asciidoc', r'_0\1.asciidoc', filename)
        filename = re.sub(r'chapter(\d\d)\.asciidoc', r'chapter_\1.asciidoc', filename)
        wordcounts.append(WordCount(filename, lines=lines, words=words))
    return wordcounts


def main():
    commits = get_log()
    all_wordcounts = {}
    filenames = set()
    try:
        for commit in commits:
            checkout_commit(commit.hash)
            all_wordcounts[commit] = get_wordcounts()
            filenames.update(set(wc.filename for wc in all_wordcounts[commit]))

        with open(os.path.join(BOOK_ROOT, 'wordcounts.tsv'), 'w') as csvfile:
            fieldnames = ['date.{}'.format(thing) for thing in ['year', 'month', 'day', 'hour']]
            fieldnames += ['subject', 'hash', 'date']
            fieldnames.extend(sorted(filename + " (words)" for filename in filenames))
            fieldnames.extend(sorted(filename + " (lines)" for filename in filenames))
            writer = csv.DictWriter(csvfile, fieldnames, dialect="excel-tab")
            writer.writeheader()
            for commit, wordcounts in all_wordcounts.items():
                row = {}
                row['hash'] = commit.hash
                row['subject'] = commit.subject
                row['date'] = ''
                row['date.year'] = commit.date.year
                row['date.month'] = commit.date.month
                row['date.day'] = commit.date.day
                row['date.hour'] = commit.date.hour
                for wordcount in wordcounts:
                    row[wordcount.filename + " (words)"] = wordcount.words
                    row[wordcount.filename + " (lines)"] = wordcount.lines
                writer.writerow(row)

    finally:
        checkout_commit('master')



if __name__ == '__main__':
    main()

