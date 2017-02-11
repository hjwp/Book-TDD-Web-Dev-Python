#!/bin/bash
set -e

CHAP=$1

cd $CHAP/superlists
git push -f local $CHAP
git push -uf origin $CHAP

cd ../..
