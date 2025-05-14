#!/bin/bash
# replay all the commits for a given chapter ($CHAP)
# onto the latest version of the previous chapter ($PREV)
set -e

PREV=$1
CHAP=$2

# assumes a git remote called "local" (eg pointing at a local bare repo...)
# rather than using origin/github,
# this allows us to feed through changes without pushing to github
REPO=local

cd "$CHAP/superlists"

# determine the commit we want to start from,
# which is the last commit of the $PREV branch as it was *before* our new version.
# We assume that the repo version in $CHAP/superlists has *not* got this latest version yet.
# (so that's why we don't do the git fetch until after this step)
# START_COMMIT="$(git rev-list -n 1 "$REPO/$PREV")"
# CHAP_COMMIT_LIST="$START_COMMIT..$REPO/$CHAP"
START_COMMIT="$(git rev-list -n 1 "origin/$PREV")"
CHAP_COMMIT_LIST="$START_COMMIT..origin/$CHAP"

# check START_COMMIT exists in $CHAP branch's history
# https://stackoverflow.com/a/4129070/366221
if [ "$(git merge-base "$START_COMMIT" "$CHAP")" != "$START_COMMIT" ]; then
    echo "Error: $START_COMMIT is not in the history of $CHAP"
    exit 1
fi

# now we pull down the latest version of $PREV
git fetch "$REPO"

# reset our chapter to the new version of the end of $PREV
git switch "$CHAP"
git reset --hard "$REPO/$PREV"

# now cherry pick all the old commits from $CHAP onto this new base.
# (we can't just use rebase because it does the wrong thing with trying to find common history)
git cherry-pick -Xrename-threshold=20%  "$CHAP_COMMIT_LIST"


# display a little diff to sanity-check what we've done.
git diff -w "$REPO/$CHAP"

cd ../..
