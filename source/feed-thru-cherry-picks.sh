#!/bin/bash
set -e

CHAP=$1
PREV=$(($CHAP - 1))
REPO=origin

if (($CHAP < 10)); then
    CHAP="chapter_0$CHAP"
else
    CHAP="chapter_$CHAP"
fi
if (($PREV < 10)); then
    PREV="chapter_0$PREV"
else
    PREV="chapter_$PREV"
fi

cd $CHAP/superlists

git checkout $PREV
git reset --hard $REPO/$PREV
git checkout $CHAP

git fetch $REPO
git reset --hard $REPO/$PREV
git cherry-pick $PREV..$REPO/$CHAP
git diff $REPO/$CHAP

cd ../..
