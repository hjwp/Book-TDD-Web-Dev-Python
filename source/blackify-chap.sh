#!/bin/bash
set -e

PREV=$1
CHAP=$2

# assumes a git remote local pointing at a local bare repo...
REPO=local

cd $CHAP/superlists

git fetch $REPO

STARTCOMMIT="$(git rev-parse $PREV)"
ENDCOMMIT="$(git rev-parse $CHAP)"

git checkout $CHAP
git reset --hard $REPO/$PREV

git rev-list $STARTCOMMIT^..$ENDCOMMIT| tac | xargs -n1 sh -c 'git co $0 -- . && black . && git commit -am "$(git show -s --format=%B $0)"'

git diff -w $REPO/$CHAP


cd ../..
