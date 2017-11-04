#!/bin/bash
PYTHONHASHSEED=0 py.test --tb=short tests/test_book_tester.py
# py.test --tb=short `ls tests/test_* | grep -v test_chapter | grep -v test_server` 
