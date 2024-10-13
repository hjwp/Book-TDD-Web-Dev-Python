#!/usr/bin/env python

# use with
# FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter $PWD/../../fix-commit-numbers.py 3fc31f1b..

import re
import sys

incoming = sys.stdin.read()
if m := re.match(r"(.+) --ch(\d+)l(\d+)(-?)(\d?)--", incoming):
    prefix, chap_num, listing_num, extra_dash, suffix = m.groups()
    chap_num = int(chap_num)
    listing_num = int(listing_num)
    suffix = int(suffix) if suffix else None
    if chap_num != 14:
        chap_num = 14

    if suffix and listing_num == 30:
        listing_num = listing_num - 1 + suffix

    if listing_num == 32 and suffix == "1":
        listing_num = listing_num
    elif listing_num == 32 and suffix == "2":
        listing_num = 33
    elif listing_num == 33 and suffix is None:
        listing_num = 34
    elif listing_num == 33 and suffix :
        listing_num = 35
    elif listing_num == 34:
        listing_num = 36
    elif listing_num == 35:
        listing_num = 37
    elif listing_num == 36:
        assert suffix
        listing_num = 37 + suffix

    print(f"{prefix} --ch{chap_num}l{listing_num:03d}--")
else:
    print(incoming)
