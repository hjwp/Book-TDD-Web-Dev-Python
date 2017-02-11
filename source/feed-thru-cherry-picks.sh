#!/bin/bash
set -e

CHAP=$1
PREV=$2
# assumes a git remote local pointing at a local bare repo...
REPO=local

cd $CHAP/superlists

git checkout $PREV
git reset --hard $REPO/$PREV
git checkout $CHAP

git fetch $REPO
git reset --hard $REPO/$PREV
git cherry-pick $PREV..$REPO/$CHAP
git diff $REPO/$CHAP

cd ../..
