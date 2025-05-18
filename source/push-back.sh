#!/bin/bash
set -e

CHAP=$1

cd "$CHAP/superlists"
git push --force-with-lease local "$CHAP"
# git push --force-with-lease origin "$CHAP"

cd ../..
