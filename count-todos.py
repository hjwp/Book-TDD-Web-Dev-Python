import csv
import datetime
import sys
from pathlib import Path

MARKERS = ["TODO", "RITA", "DAVID", "SEBASTIAN", "JAN", "CSANAD"]

out = csv.writer(sys.stdout)
out.writerow(["Date", "Chapter"] + MARKERS)
today = datetime.date.today()
for path in sorted(
    list(Path(".").rglob("chapter*.asciidoc"))
    + list(Path(".").rglob("appendix*.asciidoc"))
):
    chapter_name = str(path).replace(".asciidoc", "")
    todos = [path.read_text().count(thing) for thing in MARKERS]
    out.writerow([today.isoformat(), chapter_name] + todos)
