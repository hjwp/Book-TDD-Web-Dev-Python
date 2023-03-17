#!/bin/bash
set -e

CHAP=$1

cd $CHAP/superlists
git fpush local $CHAP
# git fpush origin $CHAP

cd ../..
