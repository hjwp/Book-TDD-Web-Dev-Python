#!/bin/bash
PYTHONHASHSEED=0 py.test --failed-first --tb=short -k 'not test_listings_and_commands_and_output'  $@ tests/
# py.test --tb=short `ls tests/test_* | grep -v test_chapter | grep -v test_server` 
