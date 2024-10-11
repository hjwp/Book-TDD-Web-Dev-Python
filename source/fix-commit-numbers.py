#!/usr/bin/env python

# use with 
# FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter $PWD/../../fix-commit-numbers.py 3fc31f1b..

import re
import sys

incoming = sys.stdin.read()
if m := re.match(r"(.+) --ch(\d+)l(\d+)--", incoming):
    prefix, chap_num, listing_num = m.groups()
    new_listing_num = int(listing_num) + 1
    print(f"{prefix} --ch{chap_num}l{new_listing_num:03d}--")
else:
    print(incoming)
