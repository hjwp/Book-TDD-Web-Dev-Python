#!/bin/bash
set -e

PREV=$1
CHAP=$2

# assumes a git remote local pointing at a local bare repo...
REPO=local

cd $CHAP/superlists

git checkout $PREV
git reset --hard $REPO/$PREV

git fetch $REPO
git checkout $CHAP
git reset --hard $REPO/$PREV

git cherry-pick -Xrename-threshold=20%  $PREV..$REPO/$CHAP
git diff -w $REPO/$CHAP

cd ../..
