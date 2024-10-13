#!/usr/bin/env python

# use with
# FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter $PWD/../../fix-commit-numbers.py 3fc31f1b..

import re
import sys

while incoming := sys.stdin.readline():
    # if m := re.match(r"(.+) --ch(\d+)l(\d+)(-?)(\d?)--", incoming.rstrip()):
    if m := re.match(r"(.+) (\(|--)ch(\d+)l(\d+)(-?)(\d?)(\)|--)", incoming.rstrip()):
        prefix, sep1, chap_num, listing_num, extra_dash, suffix, sep2 = m.groups()
        chap_num = int(chap_num)
        listing_num = int(listing_num)
        suffix = int(suffix) if suffix else None
        if chap_num == 14:
            pass

        elif suffix and listing_num == 30:
            listing_num = listing_num - 13 + suffix

        if listing_num == 30:
            assert suffix is None
            listing_num = 21
        elif listing_num == 31:
            assert suffix is None
            listing_num = 22
        elif listing_num == 32 and suffix == "1":
            listing_num = 23
        elif listing_num == 32 and suffix == "2":
            listing_num = 24
        elif listing_num == 33 and suffix is None:
            listing_num = 25
        elif listing_num == 33 and suffix:
            listing_num = 26
        elif listing_num == 34:
            listing_num = 27
        elif listing_num == 35:
            listing_num = 28
        elif listing_num == 36:
            assert suffix
            listing_num = 28 + suffix

        print(f"{prefix} {sep1}ch{chap_num}l{listing_num:03d}{sep2}")
    else:
        print(incoming, end="")
